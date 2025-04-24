from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_file
from datetime import datetime, timedelta
from sqlalchemy import func
from core.auth import login_user, register_user
from core.database import init_db, Session
from core.models import Transaction
from core.fraud_detection import FraudDetector
from core.monitoring import TransactionMonitor
from core.report_generator import ReportGenerator
import json
import secrets
import threading
import time
import os
import re

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Inicializar base de datos
init_db()

# Configuración del monitor
monitor = TransactionMonitor()
monitor_active = False


# --------------------------
# Rutas de Autenticación
# --------------------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = login_user(email, password)

        if user:
            session['user'] = json.dumps({
                'id': user.id,
                'username': user.username,
                'role': user.role
            })
            flash("Sesión iniciada correctamente.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Credenciales inválidas. Intenta nuevamente.", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        success = register_user(username, email, password)

        if success:
            flash("Registro exitoso. Inicia sesión.", "success")
            return redirect(url_for('login'))
        else:
            flash("Error al registrar usuario. Verifica tus datos.", "danger")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop('user', None)
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for('login'))


# --------------------------
# Rutas de la Aplicación
# --------------------------

@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        flash("Debes iniciar sesión primero.", "warning")
        return redirect(url_for('login'))

    user_data = json.loads(session['user'])
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    return render_template("dashboard.html",
                           user={
                               'username': user_data['username'],
                               'role': user_data['role']
                           },
                           default_start_date=start_date,
                           default_end_date=end_date)


@app.route("/transactions")
def transactions():
    if 'user' not in session:
        flash("Acceso denegado. Por favor inicia sesión.", "warning")
        return redirect(url_for('login'))

    user_data = json.loads(session['user'])
    user_id = user_data['id']
    db_session = Session()

    try:
        transactions_list = db_session.query(Transaction).filter_by(user_id=user_id).all()
        fraud_detector = FraudDetector()
        processed_transactions = []

        for tx in transactions_list:
            tx_data = {
                'id': tx.id,
                'amount': tx.amount,
                'date': tx.date
            }
            is_fraud = fraud_detector.detect_fraud(tx_data)

            processed_transactions.append({
                'id': tx.id,
                'amount': tx.amount,
                'date': tx.date,
                'payment_method': tx.payment_method,
                'is_fraud': is_fraud
            })

        return render_template('transactions.html',
                               user=user_data,
                               transactions=processed_transactions)

    except Exception as e:
        flash(f"Error al cargar transacciones: {str(e)}", "danger")
        return redirect(url_for('dashboard'))
    finally:
        db_session.close()


# --------------------------
# API Endpoints
# --------------------------

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_data = json.loads(session['user'])
    data = request.get_json()
    db_session = Session()

    try:
        # Validación y normalización del monto
        try:
            amount_str = str(data.get('amount', '')).strip()
            clean_amount = re.sub(r'[^\d.,]', '', amount_str)

            if not clean_amount:
                return jsonify({"error": "Monto no puede estar vacío"}), 400

            if ',' in clean_amount:
                if len(clean_amount.split(',')[-1]) == 2:
                    clean_amount = clean_amount.replace(',', '.')
                else:
                    clean_amount = clean_amount.replace(',', '')

            amount = round(float(clean_amount), 2)

            if amount <= 0:
                return jsonify({"error": "El monto debe ser positivo"}), 400

        except (TypeError, ValueError, AttributeError) as e:
            return jsonify({"error": f"Formato de monto inválido: {str(e)}"}), 400

        # Validación del método de pago
        method = data.get('method')
        valid_methods = ["Tarjeta Crédito", "Tarjeta Débito", "Transferencia", "Efectivo"]
        if not method or method not in valid_methods:
            return jsonify({"error": f"Método de pago inválido. Use: {', '.join(valid_methods)}"}), 400

        # Verificación de duplicados - Lógica ajustada
        now = datetime.now()
        time_threshold = now - timedelta(minutes=1)  # Aumentamos el umbral de tiempo a 1 minuto
        amount_tolerance = 0.05  # Aumentamos la tolerancia del monto

        duplicate = db_session.query(Transaction).filter(
            Transaction.user_id == user_data['id'],
            func.abs(Transaction.amount - amount) < amount_tolerance,
            Transaction.payment_method == method,
            Transaction.date >= time_threshold
        ).first()

        if duplicate:
            time_diff = (now - duplicate.date).total_seconds()
            return jsonify({
                "success": False,
                "duplicate": True,
                "error": f"Transacción similar registrada hace {time_diff:.1f} segundos"
            }), 400

        # Creación de la transacción
        new_transaction = Transaction(
            user_id=user_data['id'],
            amount=amount,
            payment_method=method,
            date=now,
            is_flagged=False
        )

        db_session.add(new_transaction)
        db_session.commit()

        return jsonify({
            "success": True,
            "transaction": {
                "id": new_transaction.id,
                "amount": float(new_transaction.amount),
                "date": new_transaction.date.strftime('%Y-%m-%d %H:%M:%S'),
                "payment_method": new_transaction.payment_method,
                "is_flagged": False
            },
            "message": "Transacción registrada exitosamente"
        })

    except Exception as e:
        db_session.rollback()
        app.logger.error(f"Error adding transaction: {str(e)}")
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    finally:
        db_session.close()

# --------------------------
# API para Monitoreo en Tiempo Real
# --------------------------

@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    global monitor_active

    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    if not monitor_active:
        monitor_active = True
        threading.Thread(target=run_monitoring).start()
        return jsonify({"status": "started"})

    return jsonify({"status": "already_running"})


@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    global monitor_active
    monitor_active = False
    return jsonify({"status": "stopped"})


@app.route('/api/monitoring/status')
def monitoring_status():
    return jsonify({"active": monitor_active})


@app.route('/api/monitoring/transactions')
def get_recent_transactions():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_data = json.loads(session['user'])
    db_session = Session()

    try:
        transactions = db_session.query(Transaction) \
            .filter_by(user_id=user_data['id']) \
            .order_by(Transaction.date.desc()) \
            .limit(5) \
            .all()

        fraud_detector = FraudDetector()
        result = []

        for tx in transactions:
            tx_data = {
                'id': tx.id,
                'amount': float(tx.amount),
                'date': tx.date.strftime('%Y-%m-%d %H:%M:%S')
            }
            is_fraud = bool(fraud_detector.detect_fraud(tx_data))

            result.append({
                'id': tx.id,
                'amount': float(tx.amount),
                'date': tx.date.strftime('%Y-%m-%d %H:%M:%S'),
                'payment_method': tx.payment_method,
                'is_fraud': is_fraud
            })

        return jsonify({"transactions": result})

    except Exception as e:
        app.logger.error(f"Error en get_recent_transactions: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500
    finally:
        db_session.close()


def run_monitoring():
    global monitor_active
    db_session = Session()
    fraud_detector = FraudDetector()

    try:
        while monitor_active:
            new_transactions = monitor.detect_new_transactions()
            for tx in new_transactions:
                tx_data = {
                    'id': tx.id,
                    'amount': tx.amount,
                    'date': tx.date
                }
                is_fraud = fraud_detector.detect_fraud(tx_data)
            time.sleep(5)
    finally:
        db_session.close()


# --------------------------
# API para Generación de Reportes (Versión Corregida)
# --------------------------

@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_data = json.loads(session['user'])
    data = request.get_json()
    db_session = Session()

    try:
        # Validación de fechas
        if not data.get('startDate') or not data.get('endDate'):
            return jsonify({"error": "Fechas requeridas"}), 400

        try:
            start_date = datetime.strptime(data['startDate'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['endDate'], '%Y-%m-%d').date()

            if start_date > end_date:
                return jsonify({"error": "La fecha inicial no puede ser mayor a la final"}), 400

        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}), 400

        # Validación del formato
        report_format = data.get('format', 'pdf').lower()
        if report_format not in ['pdf', 'csv']:
            return jsonify({"error": "Formato no soportado. Use PDF o CSV"}), 400

        # Generar reporte
        report_generator = ReportGenerator()

        if report_format == 'pdf':
            report_path = report_generator.generate_pdf_report(
                user_id=user_data['id'],
                start_date=data['startDate'],
                end_date=data['endDate']
            )
            mimetype = 'application/pdf'
        else:
            report_path = report_generator.generate_csv_report(
                user_id=user_data['id'],
                start_date=data['startDate'],
                end_date=data['endDate']
            )
            mimetype = 'text/csv'

        # Verificar que el archivo se creó
        if not os.path.exists(report_path):
            return jsonify({"error": "Error al generar el archivo de reporte"}), 500

        # Obtener nombre del archivo
        filename = f"reporte_{data['startDate']}_a_{data['endDate']}.{report_format}"

        return send_file(
            report_path,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )

    except Exception as e:
        app.logger.error(f"Error generando reporte: {str(e)}")
        return jsonify({"error": f"Error interno al generar reporte: {str(e)}"}), 500
    finally:
        db_session.close()


if __name__ == "__main__":
    if not os.path.exists('temp'):
        os.makedirs('temp')
    if not os.path.exists('reports'):
        os.makedirs('reports')
    app.run(debug=True)
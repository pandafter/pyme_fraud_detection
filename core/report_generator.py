import os
from datetime import datetime
import csv
from fpdf import FPDF
from core.database import Session
from core.models import Transaction


class ReportGenerator:
    def __init__(self):
        self.reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def generate_pdf_report(self, user_id, start_date, end_date):
        # Obtener transacciones
        transactions = self._get_transactions(user_id, start_date, end_date)

        # Crear PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Título
        pdf.cell(200, 10, txt=f"Reporte de Transacciones ({start_date} a {end_date})", ln=1, align='C')
        pdf.ln(10)

        # Contenido
        for tx in transactions:
            pdf.cell(200, 10, txt=f"ID: {tx.id} | Fecha: {tx.date} | Monto: ${tx.amount} | Método: {tx.payment_method}",
                     ln=1)

        # Guardar archivo
        filename = f"reporte_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        pdf.output(filepath)

        return filepath

    def generate_csv_report(self, user_id, start_date, end_date):
        # Obtener transacciones
        transactions = self._get_transactions(user_id, start_date, end_date)

        # Crear CSV
        filename = f"reporte_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        filepath = os.path.join(self.reports_dir, filename)

        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = ['id', 'date', 'amount', 'payment_method']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for tx in transactions:
                writer.writerow({
                    'id': tx.id,
                    'date': tx.date,
                    'amount': tx.amount,
                    'payment_method': tx.payment_method
                })

        return filepath

    def _get_transactions(self, user_id, start_date, end_date):
        db_session = Session()
        try:
            return db_session.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            ).order_by(Transaction.date.desc()).all()
        finally:
            db_session.close()
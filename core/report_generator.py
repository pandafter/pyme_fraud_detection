import pandas as pd
from fpdf import FPDF
from datetime import datetime
from core.database import Session
from core.models import Transaction


class ReportGenerator:
    def __init__(self):
        self.session = Session()

    def generate_csv_report(self, start_date, end_date):
        """Genera reporte en formato CSV con detalles de fraude"""
        transactions = self._get_transactions(start_date, end_date)
        df = pd.DataFrame([{
            'ID': tx.id,
            'Usuario': tx.user_id,
            'Monto': tx.amount,
            'Fecha': tx.date.strftime('%Y-%m-%d %H:%M'),
            'Método': tx.payment_method,
            'Estado de Riesgo': '⚠️ Alto' if tx.is_flagged else '✔️ Normal',
            'Comentario': getattr(tx, 'fraud_reason', 'N/A')  # si se almacena la razón
        } for tx in transactions])

        filename = f"reporte_fraude_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        df.to_csv(filename, index=False)
        return filename

    def generate_pdf_report(self, start_date, end_date):
        """Genera reporte PDF con transacciones sospechosas"""
        transactions = self._get_transactions(start_date, end_date)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "REPORTE DE TRANSACCIONES SOSPECHOSAS", ln=1, align='C')
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Periodo: {start_date} a {end_date}", ln=1, align='C')
        pdf.ln(10)

        for tx in transactions:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"ID: {tx.id} | Usuario: {tx.user_id} | Monto: ${tx.amount:.2f}", ln=1)
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Fecha: {tx.date.strftime('%Y-%m-%d %H:%M')} | Método: {tx.payment_method}", ln=1)
            pdf.cell(0, 10,
                     f"Riesgo: {'Alto' if tx.is_flagged else 'Normal'} | Comentario: {getattr(tx, 'fraud_reason', 'N/A')}",
                     ln=1)
            pdf.ln(5)

        filename = f"reporte_fraude_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        pdf.output(filename)
        return filename

    def _get_transactions(self, start_date, end_date):
        """Obtiene transacciones en el rango de fechas"""
        return self.session.query(Transaction).filter(
            Transaction.date.between(start_date, end_date),
            Transaction.is_flagged == True  # Solo transacciones marcadas
        ).all()
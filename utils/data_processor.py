import pandas as pd
from core.database import Session
from core.models import Transaction


def prepare_transaction_data():
    """Prepara datos para el modelo de ML"""
    session = Session()
    try:
        # Obtener todas las transacciones
        transactions = session.query(Transaction).all()

        # Convertir a DataFrame
        data = []
        for t in transactions:
            data.append({
                'id': t.id,
                'user_id': t.user_id,
                'amount': t.amount,
                'date': t.date,
                'payment_method': t.payment_method,
                'is_fraud': t.is_flagged
            })

        return pd.DataFrame(data)
    finally:
        session.close()
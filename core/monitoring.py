import threading
import time
from core.fraud_detection import FraudDetector
from core.database import Session
from core.models import Transaction
from utils.alert_system import AlertSystem


class TransactionMonitor:
    def __init__(self, check_interval=60):
        self.check_interval = check_interval  # segundos
        self.detector = FraudDetector()
        self.running = False
        self.callback = None  # NUEVO

    def start_monitoring(self, callback=None):  # MODIFICADO
        """Inicia el monitoreo en segundo plano"""
        self.running = True
        self.callback = callback  # NUEVO
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()

    def stop_monitoring(self):
        """Detiene el monitoreo"""
        self.running = False

    def _monitor_loop(self):
        """Bucle principal de monitoreo"""
        session = Session()
        last_checked_id = self._get_last_transaction_id(session)

        while self.running:
            try:
                # Obtener nuevas transacciones
                new_transactions = session.query(Transaction).filter(
                    Transaction.id > last_checked_id
                ).all()

                for tx in new_transactions:
                    # Verificar fraude
                    tx_data = {
                        'amount': tx.amount,
                        'date': tx.date
                    }
                    if self.detector.detect_fraud(tx_data):
                        tx.is_flagged = True
                        AlertSystem.send_alert(tx)  # Enviar alerta
                        session.commit()

                    # NUEVO: enviar al callback
                    if self.callback:
                        self.callback(tx)

                    last_checked_id = max(last_checked_id, tx.id)

            except Exception as e:
                print(f"Error en monitoreo: {e}")

            time.sleep(self.check_interval)

    def _get_last_transaction_id(self, session):
        """Obtiene el ID de la última transacción"""
        last_tx = session.query(Transaction).order_by(Transaction.id.desc()).first()
        return last_tx.id if last_tx else 0

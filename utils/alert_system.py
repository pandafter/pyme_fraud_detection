import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import json
from typing import Dict
import logging


class AlertSystem:
    def __init__(self, config_path: str = 'config/email_config.json'):
        self.logger = logging.getLogger('alert_system')
        self.config = self._load_config(config_path)
        self.setup_complete = bool(self.config)

    def _load_config(self, path: str) -> Dict:
        """Carga configuración desde archivo JSON"""
        try:
            with open(path) as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load email config: {str(e)}")
            return {}

    def send_alert(self, transaction_data: Dict, fraud_details: Dict) -> bool:
        """Envía alerta por email y registra en sistema"""
        if not self.setup_complete:
            self.logger.warning("Alert system not configured")
            return False

        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = self.config['sender_email']
            msg['Subject'] = self._generate_subject(transaction_data)

            # Cuerpo del email
            body = self._generate_email_body(transaction_data, fraud_details)
            msg.attach(MIMEText(body, 'html'))

            # Enviar a todos los destinatarios
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['username'], self.config['password'])

                for recipient in self.config['recipients']:
                    msg['To'] = recipient
                    server.send_message(msg)
                    self.logger.info(f"Alert sent to {recipient}")

            # Registrar en sistema
            self._log_alert(transaction_data, fraud_details)
            return True

        except Exception as e:
            self.logger.error(f"Failed to send alert: {str(e)}")
            return False

    def _generate_subject(self, tx: Dict) -> str:
        """Genera asunto del email"""
        return f"ALERTA FRAUDE: Transacción #{tx.get('id')} - ${tx.get('amount', 0):.2f}"

    def _generate_email_body(self, tx: Dict, fraud_details: Dict) -> str:
        """Genera cuerpo HTML del email"""
        return f"""
        <html>
            <body>
                <h2>Alerta de Transacción Fraudulenta</h2>
                <p><strong>ID:</strong> {tx.get('id')}</p>
                <p><strong>Usuario:</strong> {tx.get('user_id')}</p>
                <p><strong>Monto:</strong> ${tx.get('amount', 0):.2f}</p>
                <p><strong>Fecha:</strong> {tx.get('date')}</p>
                <p><strong>Confianza:</strong> {fraud_details.get('confidence', 0) * 100:.1f}%</p>

                <h3>Razones:</h3>
                <ul>
                    {''.join(f"<li>{reason}</li>" for reason in fraud_details.get('reasons', []))}
                </ul>

                <p><a href="{self.config.get('dashboard_url', '#')}">Ver en Dashboard</a></p>
            </body>
        </html>
        """

    def _log_alert(self, tx: Dict, details: Dict) -> None:
        """Registra alerta en base de datos y archivo log"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'transaction_id': tx.get('id'),
            'user_id': tx.get('user_id'),
            'amount': tx.get('amount'),
            'reasons': details.get('reasons', []),
            'confidence': details.get('confidence', 0)
        }

        # Guardar en archivo log
        with open('fraud_alerts.log', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')


import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from joblib import dump, load
from core.database import Session
from core.models import Transaction
from datetime import datetime, timedelta
import os
import logging
from typing import Dict, Any, Optional, List

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('fraud_detector')

MODEL_DIR = os.path.join(os.path.dirname(__file__), '../ml')
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, 'model.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')
MIN_TRAIN_SAMPLES = 20  # Mínimo reducido para desarrollo

class FraudDetector:
    def __init__(self, contamination: float = 0.05):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=150,
            max_samples=0.8,
            verbose=0
        )
        self.scaler = StandardScaler()
        self.features = ['amount', 'hour_of_day', 'day_of_week', 'amount_log']
        self.loaded = False

    def _extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extrae y calcula features de las transacciones"""
        try:
            df = df.copy()
            df['hour_of_day'] = df['date'].dt.hour
            df['day_of_week'] = df['date'].dt.dayofweek
            df['amount_log'] = np.log1p(df['amount'])
            return df
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            return pd.DataFrame()

    def load_transactions(self) -> pd.DataFrame:
        """Carga transacciones históricas"""
        session = Session()
        try:
            transactions = session.query(
                Transaction.id,
                Transaction.amount,
                Transaction.date,
                Transaction.is_flagged
            ).all()

            if not transactions:
                return pd.DataFrame()

            df = pd.DataFrame([{
                'id': t.id,
                'amount': float(t.amount),
                'date': t.date,
                'is_flagged': bool(t.is_flagged)
            } for t in transactions])

            return self._extract_features(df)
        except Exception as e:
            logger.error(f"Error loading transactions: {str(e)}")
            return pd.DataFrame()
        finally:
            session.close()

    def train_model(self) -> bool:
        """Entrena el modelo con validaciones mejoradas"""
        try:
            df = self.load_transactions()
            if df.empty:
                logger.warning("No hay transacciones para entrenar")
                return False

            # Usar todas las transacciones si hay pocas
            if len(df) < MIN_TRAIN_SAMPLES * 2:
                logger.warning(f"Usando todas las transacciones ({len(df)}) para entrenamiento")
                X = df[self.features]
            else:
                X = df[~df['is_flagged']][self.features]

            if len(X) < MIN_TRAIN_SAMPLES:
                logger.error(f"No hay suficientes datos para entrenar ({len(X)}/{MIN_TRAIN_SAMPLES})")
                return False

            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled)

            # Guardar modelo
            dump(self.model, MODEL_PATH)
            dump(self.scaler, SCALER_PATH)
            logger.info(f"Modelo entrenado con {len(X)} transacciones")
            return True

        except Exception as e:
            logger.error(f"Error entrenando modelo: {str(e)}")
            return False

    def detect_fraud(self, transaction_data: Dict[str, Any]) -> bool:
        """Detecta fraude en una transacción"""
        try:
            if not self.loaded and not self._load_or_train_model():
                return False

            # Preparar datos
            tx_date = transaction_data.get('date', datetime.now())
            if isinstance(tx_date, str):
                tx_date = datetime.strptime(tx_date, '%Y-%m-%d %H:%M:%S')

            tx_df = pd.DataFrame([{
                'amount': float(transaction_data.get('amount', 0)),
                'date': tx_date
            }])

            tx_df = self._extract_features(tx_df)
            if tx_df.empty:
                return False

            # Predecir
            X = tx_df[self.features]
            X_scaled = self.scaler.transform(X)
            prediction = self.model.predict(X_scaled)
            return prediction[0] == -1

        except Exception as e:
            logger.error(f"Error detectando fraude: {str(e)}")
            return False

    def _load_or_train_model(self) -> bool:
        """Intenta cargar modelo o entrenar uno nuevo"""
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            try:
                self.model = load(MODEL_PATH)
                self.scaler = load(SCALER_PATH)
                self.loaded = True
                return True
            except Exception as e:
                logger.error(f"Error cargando modelo: {str(e)}")

        return self.train_model()
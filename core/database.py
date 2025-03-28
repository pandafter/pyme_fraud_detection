from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pathlib import Path
import os

# Configuración de rutas
BASE_DIR = Path(__file__).parent.parent  # Raíz del proyecto (pyme_fraud_detection)
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_PATH = os.path.join(DATA_DIR, "transactions.db")

# Crear la carpeta 'data' si no existe
os.makedirs(DATA_DIR, exist_ok=True)

# Configuración de la base de datos
engine = create_engine(f'sqlite:///{DATABASE_PATH}')
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Función para inicializar la DB (crear tablas si no existen)
def init_db():
    Base.metadata.create_all(engine)
    print(f"✅ Base de datos creada en: {DATABASE_PATH}")

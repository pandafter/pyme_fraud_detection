from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from core.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    password_hash = Column(String(100))
    role = Column(String(20))

    # Relación con transacciones
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    amount = Column(Float)
    date = Column(DateTime)
    payment_method = Column(String(50))
    is_flagged = Column(Boolean, default=False)

    # Relación con usuario
    user = relationship("User", back_populates="transactions")

    def __repr__(self):
        return f"Transacción ID: {self.id}, Monto: ${self.amount}, Fecha: {self.date.strftime('%Y-%m-%d %H:%M:%S')}"

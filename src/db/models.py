from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean
from .database import Base
import datetime


class BankData(Base):
    """Modèle pour les données bancaires hebdomadaires"""
    __tablename__ = "bank_data"

    id = Column(Integer, primary_key=True, index=True)
    agence = Column(String, index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    montant = Column(Float, nullable=False)
    nombre_transactions = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"<BankData(agence='{self.agence}', date='{self.date}', montant={self.montant})>"


class User(Base):
    """Modèle pour les utilisateurs de l'API"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>" 
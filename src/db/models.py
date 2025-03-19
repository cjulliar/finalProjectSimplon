from sqlalchemy import Column, Integer, String, Float, Date
from .database import Base


class BankData(Base):
    """Modèle pour les données bancaires hebdomadaires"""
    __tablename__ = "bank_data"

    id = Column(Integer, primary_key=True, index=True)
    agence = Column(String, index=True)
    date = Column(Date, index=True)
    montant = Column(Float)
    nombre_transactions = Column(Integer)

    def __repr__(self):
        return f"<BankData(agence='{self.agence}', date='{self.date}')>" 
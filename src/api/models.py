"""
Modèles Pydantic pour l'API.
"""
from typing import List, Optional, Union
from datetime import date, datetime
from pydantic import BaseModel


class BankDataBase(BaseModel):
    """Modèle de base pour les données bancaires."""
    agence: str
    date: date
    montant: float
    nombre_transactions: int


class BankDataCreate(BankDataBase):
    """Modèle pour la création de données bancaires."""
    pass


class BankDataResponse(BankDataBase):
    """Modèle pour la réponse de l'API."""
    id: int
    created_at: datetime

    class Config:
        """Configuration Pydantic."""
        from_attributes = True


class UserBase(BaseModel):
    """Modèle de base pour les utilisateurs."""
    username: str
    email: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Modèle pour la création d'utilisateurs."""
    password: str


class UserResponse(UserBase):
    """Modèle pour la réponse de l'API concernant les utilisateurs."""
    id: int

    class Config:
        """Configuration Pydantic."""
        from_attributes = True


class Token(BaseModel):
    """Modèle pour le token d'authentification."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Modèle pour les données du token."""
    username: Optional[str] = None 
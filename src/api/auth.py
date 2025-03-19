"""
Module d'authentification pour l'API.
"""
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.api.models import TokenData
from src.db.models import User

# Configuration
SECRET_KEY = os.getenv("API_SECRET_KEY", "secret-key-for-dev-only-change-in-production")
ALGORITHM = os.getenv("API_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("API_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Outils de sécurité
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


def verify_password(plain_password, hashed_password):
    """Vérifier si le mot de passe correspond au hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Générer un hash à partir d'un mot de passe."""
    return pwd_context.hash(password)


def get_user(db: Session, username: str):
    """Récupérer un utilisateur par son nom d'utilisateur."""
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    """Authentifier un utilisateur avec son nom d'utilisateur et son mot de passe."""
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Créer un token d'accès JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Obtenir l'utilisateur actuel à partir du token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identification invalide",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user 
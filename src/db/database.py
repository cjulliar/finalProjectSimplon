"""
Configuration de la base de données SQLite.
"""
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration SQLite - Base consolidée
SQLALCHEMY_DATABASE_URL = "sqlite:///./bankreports.db"
connect_args = {"check_same_thread": False}  # Nécessaire pour SQLite
DATABASE_TYPE = "SQLite"

logger.info(f"🗄️ Base de données: SQLite consolidée (./bankreports.db)")

# Création du moteur SQLAlchemy
try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True,  # Vérification automatique des connexions
        pool_recycle=3600    # Recyclage des connexions après 1h
    )
    
    # Test de la connexion finale
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    
    logger.info(f"✅ Moteur de base de données initialisé avec succès ({DATABASE_TYPE})")
    
except Exception as e:
    logger.error(f"❌ Impossible d'initialiser la base de données: {e}")
    raise

# Création de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

def get_db():
    """Générateur de session de base de données."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_database_info():
    """Retourne des informations sur la base de données utilisée."""
    return {
        "type": DATABASE_TYPE,
        "url": SQLALCHEMY_DATABASE_URL,
        "status": "Connected"
    }
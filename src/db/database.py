"""
Configuration de la base de données.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Récupérer les variables d'environnement pour la connexion à PostgreSQL
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Déterminer l'URL de la base de données en fonction de l'environnement
# Utiliser PostgreSQL uniquement si toutes les variables d'environnement sont définies
# et si la variable USE_POSTGRES est définie à "true"
USE_POSTGRES = os.getenv("USE_POSTGRES", "false").lower() == "true"

if USE_POSTGRES and all([POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD]):
    # Utiliser PostgreSQL si les variables d'environnement sont définies
    SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
    connect_args = {}
    print(f"Utilisation de PostgreSQL: {SQLALCHEMY_DATABASE_URL}")
else:
    # Utiliser SQLite par défaut
    SQLALCHEMY_DATABASE_URL = "sqlite:///./bankreports.db"
    connect_args = {"check_same_thread": False}  # Nécessaire pour SQLite
    print(f"Utilisation de SQLite: {SQLALCHEMY_DATABASE_URL}")

# Création du moteur SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args
)

# Création de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Création de la base pour les modèles
Base = declarative_base()


def get_db():
    """Fonction pour obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
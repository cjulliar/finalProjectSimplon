from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Utilisation de SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./bankreports.db"

# Création du moteur SQLite avec support des clés étrangères
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
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
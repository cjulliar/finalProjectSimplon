"""
Configuration de la base de données avec fallback automatique.
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

# Récupérer les variables d'environnement pour PostgreSQL
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

def test_postgres_connection():
    """Test la connexion PostgreSQL et retourne True si disponible."""
    if not all([POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD]):
        logger.info("Variables PostgreSQL manquantes - utilisation de SQLite")
        return False
    
    try:
        # Test de connexion PostgreSQL
        postgres_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
        test_engine = create_engine(postgres_url, connect_args={})
        
        # Test simple de connexion
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        test_engine.dispose()
        logger.info(f"✅ Connexion PostgreSQL réussie: {POSTGRES_HOST}")
        return True
        
    except SQLAlchemyError as e:
        logger.warning(f"❌ Connexion PostgreSQL échouée: {e}")
        logger.info("🔄 Basculement automatique vers SQLite")
        return False
    except Exception as e:
        logger.warning(f"❌ Erreur inattendue PostgreSQL: {e}")
        logger.info("🔄 Basculement automatique vers SQLite")
        return False

# Déterminer automatiquement la base de données à utiliser
USE_POSTGRES = os.getenv("USE_POSTGRES", "true").lower() == "true"

if USE_POSTGRES and test_postgres_connection():
    # Utiliser PostgreSQL si disponible et fonctionnel
    SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
    connect_args = {}
    DATABASE_TYPE = "PostgreSQL"
    logger.info(f"🐘 Base de données: PostgreSQL ({POSTGRES_HOST})")
else:
    # Utiliser SQLite comme fallback
    SQLALCHEMY_DATABASE_URL = "sqlite:///./bankreports.db"
    connect_args = {"check_same_thread": False}  # Nécessaire pour SQLite
    DATABASE_TYPE = "SQLite"
    logger.info(f"🗄️ Base de données: SQLite (./bankreports.db)")

# Création du moteur SQLAlchemy avec gestion d'erreur
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
    # Dernière tentative avec SQLite en cas d'échec total
    if DATABASE_TYPE != "SQLite":
        logger.info("🔄 Tentative finale avec SQLite...")
        SQLALCHEMY_DATABASE_URL = "sqlite:///./bankreports.db"
        connect_args = {"check_same_thread": False}
        DATABASE_TYPE = "SQLite"
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args=connect_args
        )
        logger.info("✅ Fallback SQLite activé")
    else:
        raise

# Création de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Création de la base pour les modèles
Base = declarative_base()

def get_db():
    """Fonction pour obtenir une session de base de données avec gestion d'erreur."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erreur de session de base de données: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def get_database_info():
    """Retourne des informations sur la base de données utilisée."""
    return {
        "type": DATABASE_TYPE,
        "url": SQLALCHEMY_DATABASE_URL.replace(POSTGRES_PASSWORD or "", "****") if POSTGRES_PASSWORD else SQLALCHEMY_DATABASE_URL,
        "status": "Connected"
    }
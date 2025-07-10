#!/usr/bin/env python3
"""
Script de test pour vérifier le système de planification Celery.
"""
import time
import logging
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.celery_app import app
from src.tasks.report_tasks import generate_weekly_report, cleanup_old_reports
from src.db.database import SessionLocal, engine, Base
from src.db.models import BankData
from datetime import datetime, timedelta

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_celery_connection():
    """Test la connexion à Redis/Celery."""
    try:
        # Test de connexion de base
        result = app.control.inspect().ping()
        if result:
            logger.info("✅ Connexion Celery établie")
            return True
        else:
            logger.warning("⚠️ Aucun worker Celery détecté")
            return False
    except Exception as e:
        logger.error(f"❌ Erreur de connexion Celery: {e}")
        return False

def test_task_execution():
    """Test l'exécution d'une tâche simple."""
    try:
        logger.info("🧪 Test d'exécution d'une tâche...")
        
        # Tester la tâche de génération de rapport en mode local
        result = generate_weekly_report.apply(args=['Paris', '2025-01-15', '2025-01-21'])
        
        if result.successful():
            logger.info("✅ Tâche exécutée avec succès")
            logger.info(f"Résultat: {result.result}")
            return True
        else:
            logger.error(f"❌ Échec de la tâche: {result.result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution de la tâche: {e}")
        return False

def test_task_cleanup():
    """Test la tâche de nettoyage."""
    try:
        logger.info("🧹 Test de la tâche de nettoyage...")
        
        result = cleanup_old_reports.apply(args=[7])  # Nettoyer les fichiers de plus de 7 jours
        
        if result.successful():
            logger.info("✅ Tâche de nettoyage exécutée avec succès")
            logger.info(f"Résultat: {result.result}")
            return True
        else:
            logger.error(f"❌ Échec de la tâche de nettoyage: {result.result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur lors du nettoyage: {e}")
        return False

def test_with_sample_data():
    """Ajoute des données de test et lance les tâches"""
    print("\n📊 Ajout de données de test")
    
    # Créer les tables si elles n'existent pas
    Base.metadata.create_all(bind=engine)
    logger.info("🗄️ Tables de base de données créées/vérifiées")
    
    # Créer des données de test pour la semaine actuelle
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    
    sample_data = [
        BankData(
            agence="Paris",
            date=start_of_week,
            montant=15000.50,
            nombre_transactions=45
        ),
        BankData(
            agence="Paris", 
            date=start_of_week + timedelta(days=1),
            montant=22000.75,
            nombre_transactions=62
        ),
        BankData(
            agence="Lyon",
            date=start_of_week,
            montant=18500.25,
            nombre_transactions=38
        ),
        BankData(
            agence="Marseille",
            date=start_of_week + timedelta(days=2),
            montant=12000.00,
            nombre_transactions=28
        )
    ]
    
    try:
        with SessionLocal() as session:
            # Vérifier si des données existent déjà
            existing_count = session.query(BankData).count()
            if existing_count == 0:
                session.add_all(sample_data)
                session.commit()
                logger.info(f"✅ {len(sample_data)} enregistrements de test ajoutés")
            else:
                logger.info(f"📊 {existing_count} enregistrements déjà présents dans la base")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'ajout des données: {e}")
        return False
    
    return True

def main():
    logger.info("🚀 Début des tests du système Celery")
    
    celery_ok = test_celery_connection()
    
    # Ajouter des données de test
    test_with_sample_data()
    
    task_ok = test_task_execution()
    cleanup_ok = test_task_cleanup()
    
    print("\n📊 RÉSUMÉ DES TESTS")
    logger.info(f"Connexion Celery: {'✅' if celery_ok else '❌'}")
    logger.info(f"Exécution de tâche: {'✅' if task_ok else '❌'}")  
    logger.info(f"Tâche de nettoyage: {'✅' if cleanup_ok else '❌'}")
    
    if task_ok and cleanup_ok:
        logger.info("🎉 Tous les tests sont passés!")
    else:
        logger.warning("⚠️ Certains tests ont échoué")

if __name__ == "__main__":
    main() 
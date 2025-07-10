#!/usr/bin/env python3
"""
Configuration Celery pour l'automatisation des rapports bancaires.
"""
import os
import logging
from celery import Celery
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL Redis par défaut
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Créer l'instance Celery
app = Celery('bank_reports')

# Configuration Celery
app.conf.update(
    # Broker et résultats
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    
    # Sérialisation
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Timezone
    timezone='Europe/Paris',
    enable_utc=True,
    
    # Routes des tâches
    task_routes={
        'src.tasks.*': {'queue': 'reports'},
    },
    
    # Configuration des tâches périodiques (sera configuré via Django admin)
    beat_schedule={},
    
    # Configuration des workers
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Configuration des résultats
    result_expires=3600,  # 1 heure
    
    # Configuration des tâches
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Configuration de la concurrence
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Auto-découverte des tâches
app.autodiscover_tasks(['src.tasks'])

# Configuration pour Django si disponible
try:
    import django
    from django.conf import settings
    
    # Vérifier si Django est configuré
    if settings.configured and hasattr(settings, 'CELERY_TIMEZONE'):
        app.conf.timezone = settings.CELERY_TIMEZONE
        logger.info("Configuration Celery avec Django détectée")
        
except (ImportError, Exception) as e:
    logger.info("Configuration Celery standalone (sans Django)")

@app.task(bind=True)
def debug_task(self):
    """Tâche de débogage pour tester Celery."""
    print(f'Request: {self.request!r}')
    return 'Debug task executed successfully'

if __name__ == '__main__':
    app.start() 
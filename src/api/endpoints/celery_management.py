"""
Endpoints API pour la gestion des tâches Celery.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

# Import conditionnel de Celery
try:
    from celery_app import app as celery_app
    from tasks.report_tasks import (
        generate_weekly_report, 
        send_report_email, 
        generate_and_send_report,
        cleanup_old_reports
    )
    CELERY_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Celery non disponible: {e}")
    CELERY_AVAILABLE = False
    celery_app = None

from api.auth import get_current_user
from db.models import User

router = APIRouter(prefix="/celery", tags=["Gestion Celery"])

# Fonction helper pour vérifier la disponibilité de Celery
def check_celery_available():
    if not CELERY_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Service Celery non disponible. Vérifiez la configuration Redis et Celery."
        )

# Modèles Pydantic pour les requêtes
class TaskRequest(BaseModel):
    task_name: str = Field(..., description="Nom de la tâche à exécuter")
    args: List[Any] = Field(default=[], description="Arguments de la tâche")
    kwargs: Dict[str, Any] = Field(default={}, description="Arguments nommés")
    eta: Optional[datetime] = Field(None, description="Date/heure d'exécution prévue")

class ReportTaskRequest(BaseModel):
    agence: Optional[str] = Field(None, description="Agence à analyser")
    start_date: str = Field(..., description="Date de début (YYYY-MM-DD)")
    end_date: str = Field(..., description="Date de fin (YYYY-MM-DD)")
    recipients: Optional[List[str]] = Field(None, description="Destinataires email")

class ScheduledTaskResponse(BaseModel):
    task_id: str
    task_name: str
    status: str
    result: Optional[Any] = None
    date_created: datetime
    eta: Optional[datetime] = None

@router.get("/status", summary="État du système Celery")
async def get_celery_status():
    """Récupère l'état général du système Celery."""
    if not CELERY_AVAILABLE:
        return {
            "status": "unavailable",
            "message": "Celery non installé ou configuré",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # Vérifier la connexion au broker
        inspect = celery_app.control.inspect()
        active = inspect.active()
        registered = inspect.registered()
        stats = inspect.stats()
        
        return {
            "status": "connected" if active is not None else "disconnected",
            "active_tasks": active or {},
            "registered_tasks": registered or {},
            "worker_stats": stats or {},
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/tasks", summary="Liste des tâches en cours")
async def get_active_tasks():
    """Récupère la liste des tâches actives."""
    try:
        inspect = celery_app.control.inspect()
        active = inspect.active()
        scheduled = inspect.scheduled()
        
        return {
            "active_tasks": active or {},
            "scheduled_tasks": scheduled or {},
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des tâches: {str(e)}")

@router.get("/task/{task_id}", summary="État d'une tâche spécifique")
async def get_task_status(task_id: str):
    """Récupère l'état d'une tâche spécifique."""
    try:
        result = celery_app.AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result,
            "traceback": result.traceback,
            "date_done": result.date_done.isoformat() if result.date_done else None,
            "successful": result.successful(),
            "failed": result.failed()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la tâche: {str(e)}")

@router.post("/task/execute", summary="Exécuter une tâche immédiatement")
async def execute_task(task_request: TaskRequest, current_user: User = Depends(get_current_user)):
    """Exécute une tâche Celery immédiatement ou programme son exécution."""
    
    check_celery_available()  # Vérifier que Celery est disponible
    
    # Mapping des noms de tâches vers les fonctions
    task_mapping = {
        "generate_weekly_report": generate_weekly_report,
        "send_report_email": send_report_email,
        "generate_and_send_report": generate_and_send_report,
        "cleanup_old_reports": cleanup_old_reports
    }
    
    if task_request.task_name not in task_mapping:
        raise HTTPException(
            status_code=400, 
            detail=f"Tâche inconnue: {task_request.task_name}. Tâches disponibles: {list(task_mapping.keys())}"
        )
    
    try:
        task_func = task_mapping[task_request.task_name]
        
        # Exécuter la tâche avec ou sans ETA
        if task_request.eta:
            result = task_func.apply_async(
                args=task_request.args,
                kwargs=task_request.kwargs,
                eta=task_request.eta
            )
        else:
            result = task_func.apply_async(
                args=task_request.args,
                kwargs=task_request.kwargs
            )
        
        return {
            "task_id": result.id,
            "task_name": task_request.task_name,
            "status": "queued",
            "eta": task_request.eta.isoformat() if task_request.eta else None,
            "message": f"Tâche {task_request.task_name} programmée avec succès"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'exécution de la tâche: {str(e)}")

@router.post("/reports/generate", summary="Générer un rapport hebdomadaire")
async def generate_report(request: ReportTaskRequest, current_user: User = Depends(get_current_user)):
    """Lance la génération d'un rapport hebdomadaire."""
    
    try:
        # Valider les dates
        try:
            datetime.strptime(request.start_date, '%Y-%m-%d')
            datetime.strptime(request.end_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD")
        
        # Lancer la tâche appropriée
        if request.recipients:
            # Générer et envoyer
            result = generate_and_send_report.apply_async(
                args=[request.agence, request.start_date, request.end_date, request.recipients]
            )
            action = "généré et envoyé"
        else:
            # Générer seulement
            result = generate_weekly_report.apply_async(
                args=[request.agence, request.start_date, request.end_date]
            )
            action = "généré"
        
        return {
            "task_id": result.id,
            "status": "queued",
            "message": f"Rapport sera {action} pour l'agence {request.agence or 'toutes'} du {request.start_date} au {request.end_date}",
            "agence": request.agence,
            "period": f"{request.start_date} - {request.end_date}",
            "recipients": request.recipients
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la programmation du rapport: {str(e)}")

@router.post("/cleanup", summary="Nettoyer les anciens rapports")
async def cleanup_reports(days_old: int = 7, current_user: User = Depends(get_current_user)):
    """Lance le nettoyage des rapports plus anciens que X jours."""
    
    if days_old < 1:
        raise HTTPException(status_code=400, detail="Le nombre de jours doit être positif")
    
    try:
        result = cleanup_old_reports.apply_async(args=[days_old])
        
        return {
            "task_id": result.id,
            "status": "queued",
            "message": f"Nettoyage des rapports plus anciens que {days_old} jours programmé",
            "days_old": days_old
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la programmation du nettoyage: {str(e)}")

@router.delete("/task/{task_id}", summary="Annuler une tâche")
async def cancel_task(task_id: str, current_user: User = Depends(get_current_user)):
    """Annule une tâche en cours ou programmée."""
    
    try:
        celery_app.control.revoke(task_id, terminate=True)
        
        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": f"Tâche {task_id} annulée avec succès"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'annulation de la tâche: {str(e)}")

@router.get("/workers", summary="État des workers Celery")
async def get_workers_status():
    """Récupère l'état des workers Celery."""
    
    try:
        inspect = celery_app.control.inspect()
        active = inspect.active()
        stats = inspect.stats()
        registered = inspect.registered()
        
        workers_info = {}
        
        if stats:
            for worker_name, worker_stats in stats.items():
                workers_info[worker_name] = {
                    "status": "online",
                    "stats": worker_stats,
                    "active_tasks": active.get(worker_name, []) if active else [],
                    "registered_tasks": list(registered.get(worker_name, [])) if registered else []
                }
        
        return {
            "workers": workers_info,
            "total_workers": len(workers_info),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "workers": {},
            "total_workers": 0,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/test", summary="Tester la connectivité Celery")
async def test_celery_connection():
    """Teste la connectivité du système Celery."""
    
    try:
        # Test simple avec la tâche de nettoyage
        result = cleanup_old_reports.apply_async(args=[999])  # Nettoyage fictif
        
        # Attendre un peu pour voir si la tâche est acceptée
        import time
        time.sleep(1)
        
        task_result = celery_app.AsyncResult(result.id)
        
        return {
            "connectivity": "success",
            "test_task_id": result.id,
            "test_task_status": task_result.status,
            "message": "Connexion Celery fonctionnelle",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "connectivity": "failed",
            "error": str(e),
            "message": "Erreur de connexion Celery",
            "timestamp": datetime.now().isoformat()
        } 
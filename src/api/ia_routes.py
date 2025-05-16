"""
Routes de l'API pour l'IA.
"""
import os
import uuid
import json
import time
from typing import List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, EmailStr

from src.db.database import get_db
from src.db.models import BankData, User, Analysis, Visualization as DBVisualization, ScheduledReport
from src.api.auth import get_current_user
from src.api.ia_models import (
    AnalysisRequest, 
    AnalysisResponse, 
    Visualization, 
    AnalysisMetadata,
    SavedAnalysis,
    SavedAnalysisList
)
from src.ia.ai_service import ai_service

# Créer un router pour les routes d'IA
router = APIRouter(prefix="/ai", tags=["ai"])

# Modèles pour les nouvelles fonctionnalités
class EmailRequest(BaseModel):
    """Requête pour envoyer un rapport par email."""
    analysis_id: str
    recipients: List[EmailStr]
    subject: Optional[str] = None


class ScheduleRequest(BaseModel):
    """Requête pour planifier un rapport périodique."""
    schedule_type: str = "weekly"  # daily, weekly, monthly
    day: int = 1  # jour de la semaine (0-6) ou du mois (1-31)
    recipients: List[EmailStr]
    agence: Optional[str] = None
    include_visualizations: bool = True


class EmailResponse(BaseModel):
    """Réponse après envoi d'un email."""
    sent: bool
    message: Optional[str] = None
    recipients: Optional[List[str]] = None


class ScheduleResponse(BaseModel):
    """Réponse après planification d'un rapport."""
    scheduled: bool
    message: Optional[str] = None
    schedule_id: Optional[str] = None


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_bank_data(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyser les données bancaires avec l'IA et générer un rapport.
    
    - **start_date**: Date de début pour l'analyse (optionnelle)
    - **end_date**: Date de fin pour l'analyse (optionnelle)
    - **agence**: Nom de l'agence à analyser (toutes si non spécifié)
    - **format**: Format du rapport (markdown ou html)
    - **include_visualizations**: Inclure des visualisations
    """
    start_time = time.time()
    
    # Paramètres par défaut
    if not request.start_date:
        request.start_date = datetime.now().date() - timedelta(days=30)
    if not request.end_date:
        request.end_date = datetime.now().date()
    
    # Construire la requête pour extraire les données
    query = db.query(BankData).filter(
        BankData.date >= request.start_date,
        BankData.date <= request.end_date
    )
    
    if request.agence:
        query = query.filter(BankData.agence == request.agence)
    
    # Récupérer les données
    bank_data = query.all()
    
    if not bank_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune donnée trouvée pour les critères spécifiés"
        )
    
    # Convertir les modèles SQLAlchemy en dictionnaires
    data_dicts = [
        {
            "agence": item.agence,
            "date": item.date,
            "montant": item.montant,
            "nombre_transactions": item.nombre_transactions
        }
        for item in bank_data
    ]
    
    try:
        # Appeler le service d'IA pour analyser les données
        result = ai_service.analyze_bank_data(data_dicts)
        
        # Formater les visualisations pour la réponse
        visualizations = []
        if request.include_visualizations and "visualizations" in result:
            for viz in result["visualizations"]:
                # Ajouter une URL pour accéder à l'image
                viz_id = str(uuid.uuid4())
                visualizations.append(Visualization(
                    path=viz["path"],
                    title=viz["title"],
                    type=viz["type"],
                    url=f"/api/ai/visualizations/{viz_id}"
                ))
        
        # Calculer le temps d'exécution
        execution_time = time.time() - start_time
        
        # Créer l'ID unique pour cette analyse
        analysis_id = str(uuid.uuid4())
        
        # Préparer la réponse
        response = AnalysisResponse(
            report=result["report"],
            visualizations=visualizations,
            metadata=AnalysisMetadata(
                timestamp=datetime.fromisoformat(result["metadata"]["timestamp"]),
                data_points=result["metadata"]["data_points"],
                date_range=result["metadata"]["date_range"],
                agencies=result["metadata"]["agencies"],
                execution_time=execution_time,
                model_used="GPT-3.5" if not ai_service.use_alternative_api else "Mistral-7B"
            ),
            id=analysis_id
        )
        
        # Stocker l'analyse dans la base de données
        db_analysis = Analysis(
            id=analysis_id,
            user_id=current_user.id,
            created_at=datetime.now(),
            query_parameters=json.dumps({
                "start_date": request.start_date.isoformat() if request.start_date else None,
                "end_date": request.end_date.isoformat() if request.end_date else None,
                "agence": request.agence,
                "format": request.format,
                "include_visualizations": request.include_visualizations
            }),
            report=result["report"],
            analysis_metadata=json.dumps({
                "timestamp": response.metadata.timestamp.isoformat(),
                "data_points": response.metadata.data_points,
                "date_range": response.metadata.date_range,
                "agencies": response.metadata.agencies,
                "execution_time": response.metadata.execution_time,
                "model_used": response.metadata.model_used
            })
        )
        db.add(db_analysis)
        
        # Stocker les visualisations dans la base de données
        for viz in visualizations:
            db_viz = DBVisualization(
                id=str(uuid.uuid4()),
                analysis_id=analysis_id,
                path=viz.path,
                title=viz.title,
                type=viz.type,
                created_at=datetime.now()
            )
            db.add(db_viz)
        
        db.commit()
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'analyse des données: {str(e)}"
        )


@router.post("/email", response_model=EmailResponse)
async def send_report_email(
    request: EmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Envoyer un rapport d'analyse par email.
    
    - **analysis_id**: ID de l'analyse à envoyer
    - **recipients**: Liste des adresses email des destinataires
    - **subject**: Sujet de l'email (optionnel)
    """
    # Récupérer l'analyse depuis la base de données
    analysis = db.query(Analysis).filter(Analysis.id == request.analysis_id).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analyse non trouvée"
        )
    
    # Vérifier que l'utilisateur a accès à cette analyse
    if analysis.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à accéder à cette analyse"
        )
    
    try:
        # Récupérer les visualisations
        visualizations = db.query(DBVisualization).filter(DBVisualization.analysis_id == analysis.id).all()
        viz_list = [{"path": viz.path, "title": viz.title, "type": viz.type} for viz in visualizations]
        
        # Préparer les données du rapport
        report_data = {
            "report": analysis.report,
            "visualizations": viz_list,
            "metadata": json.loads(analysis.analysis_metadata)
        }
        
        # Envoyer l'email
        result = ai_service.send_report_by_email(
            report_data=report_data,
            recipients=request.recipients,
            subject=request.subject
        )
        
        return EmailResponse(
            sent=result.get("sent", False),
            message=result.get("message"),
            recipients=result.get("recipients")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'envoi de l'email: {str(e)}"
        )


@router.post("/schedule", response_model=ScheduleResponse)
async def schedule_periodic_report(
    request: ScheduleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Planifier un rapport périodique.
    
    - **schedule_type**: Type de planification ('daily', 'weekly', 'monthly')
    - **day**: Jour d'envoi (0-6 pour weekly, 1-31 pour monthly)
    - **recipients**: Liste des adresses email des destinataires
    - **agence**: Nom de l'agence à analyser (toutes si non spécifié)
    - **include_visualizations**: Inclure des visualisations
    """
    try:
        # Générer un ID unique pour cette planification
        schedule_id = str(uuid.uuid4())
        
        # Créer l'entrée de planification dans la base de données
        db_schedule = ScheduledReport(
            id=schedule_id,
            user_id=current_user.id,
            schedule_type=request.schedule_type,
            day=request.day,
            recipients=json.dumps(request.recipients),
            agence=request.agence,
            include_visualizations=request.include_visualizations,
            is_active=True,
            created_at=datetime.now()
        )
        db.add(db_schedule)
        db.commit()
        
        # Planifier le rapport
        result = ai_service.schedule_periodic_report(
            schedule_type=request.schedule_type,
            day=request.day,
            recipients=request.recipients
        )
        
        return ScheduleResponse(
            scheduled=True,
            message="Rapport planifié avec succès",
            schedule_id=schedule_id
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la planification du rapport: {str(e)}"
        )


@router.get("/analyses", response_model=SavedAnalysisList)
async def list_analyses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lister les analyses précédemment générées.
    """
    # Récupérer les analyses de l'utilisateur depuis la base de données
    db_analyses = db.query(Analysis).filter(Analysis.user_id == current_user.id).all()
    
    # Convertir en modèle de réponse
    analyses = []
    for analysis in db_analyses:
        try:
            query_params = json.loads(analysis.query_parameters)
            metadata = json.loads(analysis.analysis_metadata)
            
            analyses.append(SavedAnalysis(
                id=analysis.id,
                created_at=analysis.created_at,
                query_parameters=AnalysisRequest(**query_params),
                metadata=AnalysisMetadata(**metadata)
            ))
        except Exception as e:
            # Ignorer les analyses avec des données invalides
            continue
    
    return SavedAnalysisList(
        analyses=analyses,
        count=len(analyses)
    )


@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str = Path(..., description="ID de l'analyse à récupérer"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupérer une analyse précédemment générée.
    
    - **analysis_id**: ID unique de l'analyse
    """
    # Récupérer l'analyse depuis la base de données
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analyse non trouvée"
        )
    
    # Vérifier que l'utilisateur a accès à cette analyse
    if analysis.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à accéder à cette analyse"
        )
    
    # Récupérer les visualisations
    visualizations = db.query(DBVisualization).filter(DBVisualization.analysis_id == analysis.id).all()
    viz_list = [
        Visualization(
            path=viz.path,
            title=viz.title,
            type=viz.type,
            url=f"/api/ai/visualizations/{viz.id}"
        )
        for viz in visualizations
    ]
    
    # Convertir en modèle de réponse
    metadata = json.loads(analysis.analysis_metadata)
    
    return AnalysisResponse(
        report=analysis.report,
        visualizations=viz_list,
        metadata=AnalysisMetadata(**metadata),
        id=analysis.id
    )


@router.get("/visualizations/{visualization_id}")
async def get_visualization(
    visualization_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupérer une visualisation par son ID.
    
    - **visualization_id**: ID unique de la visualisation
    """
    # Récupérer la visualisation depuis la base de données
    visualization = db.query(DBVisualization).filter(DBVisualization.id == visualization_id).first()
    
    if not visualization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visualisation non trouvée"
        )
    
    # Récupérer l'analyse associée pour vérifier les droits d'accès
    analysis = db.query(Analysis).filter(Analysis.id == visualization.analysis_id).first()
    
    if not analysis or analysis.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à accéder à cette visualisation"
        )
    
    # Vérifier que le fichier existe
    if not os.path.exists(visualization.path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fichier de visualisation non trouvé"
        )
    
    return FileResponse(visualization.path) 
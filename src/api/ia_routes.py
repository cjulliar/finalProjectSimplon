"""
Routes de l'API pour l'IA.
"""
import uuid
import time
from typing import List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.db.database import get_db
from src.db.models import BankData, User
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

# Dictionnaire en mémoire pour stocker les analyses (dans un vrai système, ce serait en base de données)
analyses_store = {}


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
        
        # Stocker l'analyse pour référence future
        analyses_store[analysis_id] = {
            "id": analysis_id,
            "created_at": datetime.now(),
            "query_parameters": request.dict(),
            "result": response.dict(),
            "user_id": current_user.id
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'analyse des données: {str(e)}"
        )


@router.get("/analyses", response_model=SavedAnalysisList)
async def list_analyses(
    current_user: User = Depends(get_current_user)
):
    """
    Lister les analyses précédemment générées.
    """
    # Filtrer les analyses pour l'utilisateur courant
    user_analyses = [
        SavedAnalysis(
            id=analysis["id"],
            created_at=analysis["created_at"],
            query_parameters=AnalysisRequest(**analysis["query_parameters"]),
            metadata=AnalysisMetadata(**analysis["result"]["metadata"])
        )
        for analysis_id, analysis in analyses_store.items()
        if analysis["user_id"] == current_user.id
    ]
    
    return SavedAnalysisList(
        analyses=user_analyses,
        count=len(user_analyses)
    )


@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str = Path(..., description="ID de l'analyse à récupérer"),
    current_user: User = Depends(get_current_user)
):
    """
    Récupérer une analyse précédemment générée.
    
    - **analysis_id**: ID unique de l'analyse
    """
    if analysis_id not in analyses_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analyse non trouvée"
        )
    
    analysis = analyses_store[analysis_id]
    
    # Vérifier que l'utilisateur a accès à cette analyse
    if analysis["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à accéder à cette analyse"
        )
    
    return AnalysisResponse(**analysis["result"])


@router.get("/visualizations/{visualization_id}")
async def get_visualization(
    visualization_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Récupérer une visualisation par son ID.
    
    - **visualization_id**: ID unique de la visualisation
    """
    # Cette fonction est simplifiée et ne fonctionne pas réellement avec l'ID
    # Dans une implémentation réelle, nous stockerions l'association entre
    # l'ID de visualisation et le chemin de fichier
    
    # Pour l'instant, nous retournons simplement la première visualisation trouvée pour l'utilisateur
    for analysis_id, analysis in analyses_store.items():
        if analysis["user_id"] == current_user.id:
            for viz in analysis["result"].get("visualizations", []):
                # Ici on ne vérifie pas l'ID, juste le premier fichier trouvé
                return FileResponse(viz["path"])
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Visualisation non trouvée"
    ) 
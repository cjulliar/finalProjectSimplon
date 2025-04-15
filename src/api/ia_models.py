"""
Modèles Pydantic pour l'API d'IA.
"""
from typing import List, Dict, Optional, Any, Union
from datetime import date, datetime
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """
    Modèle pour une demande d'analyse par IA.
    """
    start_date: Optional[date] = Field(None, description="Date de début pour l'analyse")
    end_date: Optional[date] = Field(None, description="Date de fin pour l'analyse")
    agence: Optional[str] = Field(None, description="Nom de l'agence à analyser (toutes les agences si non spécifié)")
    format: Optional[str] = Field("markdown", description="Format du rapport (markdown ou html)")
    include_visualizations: Optional[bool] = Field(True, description="Inclure des visualisations dans l'analyse")


class Visualization(BaseModel):
    """
    Modèle pour une visualisation générée par l'IA.
    """
    path: str = Field(..., description="Chemin d'accès à l'image générée")
    title: str = Field(..., description="Titre de la visualisation")
    type: str = Field(..., description="Type de visualisation (bar_chart, line_chart, etc.)")
    url: Optional[str] = Field(None, description="URL publique pour accéder à la visualisation (si disponible)")


class AnalysisMetadata(BaseModel):
    """
    Modèle pour les métadonnées d'une analyse.
    """
    timestamp: datetime = Field(..., description="Horodatage de l'analyse")
    data_points: int = Field(..., description="Nombre de points de données analysés")
    date_range: Dict[str, str] = Field(..., description="Plage de dates analysée")
    agencies: List[str] = Field(..., description="Liste des agences analysées")
    execution_time: Optional[float] = Field(None, description="Temps d'exécution de l'analyse en secondes")
    model_used: Optional[str] = Field(None, description="Modèle d'IA utilisé pour l'analyse")


class AnalysisResponse(BaseModel):
    """
    Modèle pour la réponse d'analyse par IA.
    """
    report: str = Field(..., description="Rapport d'analyse généré")
    visualizations: List[Visualization] = Field([], description="Liste des visualisations générées")
    metadata: AnalysisMetadata = Field(..., description="Métadonnées de l'analyse")
    id: Optional[str] = Field(None, description="Identifiant unique de l'analyse")


class SavedAnalysis(BaseModel):
    """
    Modèle pour une analyse sauvegardée.
    """
    id: str = Field(..., description="Identifiant unique de l'analyse")
    created_at: datetime = Field(..., description="Date de création de l'analyse")
    query_parameters: AnalysisRequest = Field(..., description="Paramètres de la requête")
    metadata: AnalysisMetadata = Field(..., description="Métadonnées de l'analyse")


class SavedAnalysisList(BaseModel):
    """
    Modèle pour une liste d'analyses sauvegardées.
    """
    analyses: List[SavedAnalysis] = Field(..., description="Liste des analyses sauvegardées")
    count: int = Field(..., description="Nombre total d'analyses disponibles") 
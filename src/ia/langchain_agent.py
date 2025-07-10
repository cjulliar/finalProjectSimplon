#!/usr/bin/env python3
"""
Agent IA basé sur LangChain pour l'analyse des données bancaires.
Ce module fournit un agent capable d'analyser les données, de générer des rapports
et d'envoyer des emails automatiquement.
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Importations LangChain conditionnelles
try:
    from langchain.agents import AgentType, initialize_agent, Tool
    from langchain.memory import ConversationBufferMemory
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    from langchain.chat_models import ChatOpenAI
    from langchain.llms import HuggingFaceHub
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️ LangChain non disponible - utilisation du mode de secours")

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Configuration des API
OPENAI_API_KEY = os.getenv("LLM_API_KEY", "")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

# Par défaut, utiliser Hugging Face au lieu d'OpenAI pour éviter les coûts
# Cela peut être remplacé par un paramètre d'environnement
USE_HUGGINGFACE = os.getenv("USE_HUGGINGFACE", "true").lower() == "true"
USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"

# Si USE_OPENAI est explicitement défini à true, on l'utilise quand même
USE_ALTERNATIVE_API = USE_HUGGINGFACE or not OPENAI_API_KEY or OPENAI_API_KEY == "your-api-key-here" or OPENAI_API_KEY == "dummy-openai-key"
if USE_OPENAI:
    USE_ALTERNATIVE_API = False


class AIAgent:
    """Agent IA basé sur LangChain pour l'analyse des données bancaires."""
    
    def __init__(self, use_alternative_api: bool = USE_ALTERNATIVE_API):
        """
        Initialiser l'agent IA.
        
        Args:
            use_alternative_api (bool): Si True, utilise HuggingFace au lieu d'OpenAI
        """
        self.use_alternative_api = use_alternative_api
        
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain non disponible - Agent initialisé en mode de secours")
            self.llm = None
            self.agent = None
            return
            
        logger.info(f"Agent IA initialisé (API alternative: {use_alternative_api})")
        
        # Initialiser le LLM
        if not use_alternative_api and OPENAI_API_KEY and OPENAI_API_KEY not in ["your-api-key-here", "dummy-openai-key"]:
            try:
                self.llm = ChatOpenAI(
                    model_name="gpt-3.5-turbo",
                    temperature=0.7,
                    openai_api_key=OPENAI_API_KEY
                )
                logger.info("Utilisation de l'API OpenAI")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation d'OpenAI: {e}")
                self.llm = None
        else:
            # Utiliser HuggingFace comme alternative
            if HUGGINGFACE_API_KEY and HUGGINGFACE_API_KEY not in ["your-api-key-here", "dummy-huggingface-key"]:
                try:
                    self.llm = HuggingFaceHub(
                        repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                        huggingfacehub_api_token=HUGGINGFACE_API_KEY
                    )
                    logger.info("Utilisation de l'API HuggingFace")
                except Exception as e:
                    logger.error(f"Erreur lors de l'initialisation de HuggingFace: {e}")
                    self.llm = None
            else:
                # Fallback sur un mode simulé
                logger.warning("Aucune clé API valide trouvée, utilisation du mode simulé")
                self.llm = None
        
        # Initialiser la mémoire
        if LANGCHAIN_AVAILABLE:
            self.memory = ConversationBufferMemory(memory_key="chat_history")
            
            # Initialiser les outils
            self.tools = self._create_tools()
            
            # Initialiser l'agent
            if self.llm:
                self.agent = self._create_agent()
            else:
                self.agent = None
                logger.warning("Agent non initialisé en raison de l'absence de LLM valide")
        else:
            self.memory = None
            self.tools = []
            self.agent = None
    
    def _create_tools(self) -> List[Any]:
        """
        Créer les outils pour l'agent.
        
        Returns:
            Liste d'outils LangChain
        """
        if not LANGCHAIN_AVAILABLE:
            return []
            
        tools = [
            Tool(
                name="analyze_data",
                func=self._analyze_data_tool,
                description="Analyser des données bancaires et générer des statistiques"
            ),
            Tool(
                name="generate_visualizations",
                func=self._generate_visualizations_tool,
                description="Générer des visualisations à partir des données bancaires"
            ),
            Tool(
                name="get_historical_data",
                func=self._get_historical_data_tool,
                description="Récupérer des données historiques pour comparer avec les données actuelles"
            )
        ]
        
        # Ajouter l'outil d'envoi d'email si configuré
        if os.getenv("SMTP_SERVER") and os.getenv("SMTP_USERNAME") and os.getenv("SMTP_PASSWORD"):
            tools.append(
                Tool(
                    name="send_email",
                    func=self._send_email_tool,
                    description="Envoyer un email contenant le rapport et les visualisations"
                )
            )
        
        return tools
    
    def _create_agent(self):
        """
        Créer l'agent LangChain.
        
        Returns:
            Agent LangChain initialisé
        """
        if not LANGCHAIN_AVAILABLE:
            return None
            
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True
        )
    
    def analyze_bank_data(self, data: Union[pd.DataFrame, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Analyser les données bancaires avec l'agent IA.
        
        Args:
            data: Données bancaires sous forme de DataFrame pandas ou liste de dictionnaires
            
        Returns:
            Dict contenant le rapport et des métadonnées associées
        """
        # Convertir en DataFrame si nécessaire
        if not isinstance(data, pd.DataFrame):
            df = pd.DataFrame(data)
        else:
            df = data
        
        # Vérifier que les colonnes nécessaires sont présentes
        required_columns = ["agence", "date", "montant", "nombre_transactions"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Colonnes manquantes dans les données : {missing_columns}")
        
        # Convertir la colonne date en datetime si ce n'est pas déjà fait
        if not pd.api.types.is_datetime64_any_dtype(df["date"]):
            df["date"] = pd.to_datetime(df["date"])
        
        # Si LangChain n'est pas disponible, utiliser une réponse simulée
        if not LANGCHAIN_AVAILABLE or self.agent is None:
            logger.info("Utilisation d'une réponse simulée (LangChain non disponible)")
            return self._generate_fallback_response(df)
        
        try:
            # Sauvegarder temporairement les données pour les outils
            self._current_data = df
            
            # Calculer les statistiques de base
            stats = self._analyze_data_tool(df)
            
            # Générer les visualisations
            visualizations = self._generate_visualizations_tool(df)
            
            # Créer le prompt pour l'agent
            prompt = self._create_analysis_prompt(stats)
            
            # Exécuter l'agent pour générer le rapport
            response = self.agent.run(prompt)
            
            # Préparer la réponse
            result = {
                "report": response,
                "visualizations": visualizations,
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "data_points": len(df),
                    "date_range": {
                        "start": df["date"].min().isoformat(),
                        "end": df["date"].max().isoformat()
                    },
                    "agencies": df["agence"].unique().tolist(),
                    "execution_time": 0.0
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse avec LangChain: {e}")
            # Fallback sur une réponse simulée
            return self._generate_fallback_response(df)
    
    def _analyze_data_tool(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Outil pour analyser les données bancaires.
        
        Args:
            df: DataFrame contenant les données bancaires
            
        Returns:
            Dict contenant les statistiques calculées
        """
        # Calculer les statistiques de base
        stats = {
            "total_transactions": len(df),
            "total_amount": df["montant"].sum(),
            "average_amount": df["montant"].mean(),
            "min_amount": df["montant"].min(),
            "max_amount": df["montant"].max(),
            "total_volume": df["nombre_transactions"].sum(),
            "average_volume": df["nombre_transactions"].mean(),
            "agencies": df["agence"].unique().tolist(),
            "date_range": {
                "start": df["date"].min().isoformat(),
                "end": df["date"].max().isoformat()
            }
        }
        
        # Statistiques par agence
        agency_stats = df.groupby("agence").agg({
            "montant": ["sum", "mean", "count"],
            "nombre_transactions": ["sum", "mean"]
        }).round(2)
        
        stats["agency_breakdown"] = agency_stats.to_dict()
        
        return stats
    
    def _generate_visualizations_tool(self, df: pd.DataFrame) -> List[Dict[str, str]]:
        """
        Outil pour générer des visualisations.
        
        Args:
            df: DataFrame contenant les données bancaires
            
        Returns:
            Liste des visualisations générées
        """
        visualizations = []
        
        try:
            # Créer le dossier de sortie s'il n'existe pas
            output_dir = Path("output/visualizations")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 1. Évolution des montants dans le temps
            plt.figure(figsize=(12, 6))
            df.groupby("date")["montant"].sum().plot(kind="line")
            plt.title("Évolution des montants dans le temps")
            plt.xlabel("Date")
            plt.ylabel("Montant total")
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            viz_path = output_dir / "evolution_montants.png"
            plt.savefig(viz_path, dpi=300, bbox_inches="tight")
            plt.close()
            
            visualizations.append({
                "path": str(viz_path),
                "title": "Évolution des montants dans le temps",
                "type": "line_chart"
            })
            
            # 2. Répartition par agence
            plt.figure(figsize=(10, 6))
            df.groupby("agence")["montant"].sum().plot(kind="bar")
            plt.title("Répartition des montants par agence")
            plt.xlabel("Agence")
            plt.ylabel("Montant total")
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            viz_path = output_dir / "repartition_agences.png"
            plt.savefig(viz_path, dpi=300, bbox_inches="tight")
            plt.close()
            
            visualizations.append({
                "path": str(viz_path),
                "title": "Répartition des montants par agence",
                "type": "bar_chart"
            })
            
            # 3. Distribution des montants
            plt.figure(figsize=(10, 6))
            df["montant"].hist(bins=30, edgecolor="black")
            plt.title("Distribution des montants")
            plt.xlabel("Montant")
            plt.ylabel("Fréquence")
            plt.tight_layout()
            
            viz_path = output_dir / "distribution_montants.png"
            plt.savefig(viz_path, dpi=300, bbox_inches="tight")
            plt.close()
            
            visualizations.append({
                "path": str(viz_path),
                "title": "Distribution des montants",
                "type": "histogram"
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des visualisations: {e}")
        
        return visualizations
    
    def _get_historical_data_tool(self, period: str = "last_month") -> Dict[str, Any]:
        """
        Outil pour récupérer des données historiques.
        
        Args:
            period: Période pour les données historiques
            
        Returns:
            Dict contenant les données historiques
        """
        # Pour l'instant, retourner des données simulées
        return {
            "period": period,
            "data_points": 100,
            "trend": "stable",
            "comparison": "similar_to_current"
        }
    
    def _send_email_tool(self, recipient: str, subject: str, content: str, attachments: List[str] = None) -> Dict[str, Any]:
        """
        Outil pour envoyer des emails.
        
        Args:
            recipient: Destinataire de l'email
            subject: Sujet de l'email
            content: Contenu de l'email
            attachments: Liste des pièces jointes
            
        Returns:
            Dict contenant le statut de l'envoi
        """
        # Pour l'instant, simuler l'envoi
        return {
            "sent": True,
            "recipient": recipient,
            "subject": subject,
            "message": "Email simulé envoyé avec succès"
        }
    
    def _create_analysis_prompt(self, stats: Dict[str, Any]) -> str:
        """
        Créer le prompt pour l'analyse.
        
        Args:
            stats: Statistiques calculées
            
        Returns:
            Prompt pour l'agent
        """
        prompt = f"""
        Analysez les données bancaires suivantes et générez un rapport détaillé :
        
        Statistiques générales :
        - Nombre total de transactions : {stats['total_transactions']}
        - Montant total : {stats['total_amount']:,.2f}
        - Montant moyen : {stats['average_amount']:,.2f}
        - Volume total : {stats['total_volume']}
        - Volume moyen : {stats['average_volume']:,.2f}
        
        Agences impliquées : {', '.join(stats['agencies'])}
        Période : Du {stats['date_range']['start']} au {stats['date_range']['end']}
        
        Veuillez fournir :
        1. Un résumé exécutif
        2. Une analyse des tendances
        3. Des recommandations
        4. Des points d'attention
        """
        
        return prompt
    
    def _generate_fallback_response(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Générer une réponse de secours sans LangChain.
        
        Args:
            df: DataFrame contenant les données bancaires
            
        Returns:
            Dict contenant le rapport et des métadonnées associées
        """
        # Calculer les statistiques de base
        total_amount = df["montant"].sum()
        avg_amount = df["montant"].mean()
        total_transactions = len(df)
        agencies = df["agence"].unique()
        
        # Générer un rapport simple
        report = f"""
        # Rapport d'Analyse Bancaire (Mode de Secours)
        
        ## Résumé Exécutif
        Analyse effectuée sur {total_transactions} transactions pour un montant total de {total_amount:,.2f}€.
        
        ## Statistiques Clés
        - **Montant total** : {total_amount:,.2f}€
        - **Montant moyen** : {avg_amount:,.2f}€
        - **Nombre de transactions** : {total_transactions}
        - **Agences impliquées** : {len(agencies)}
        
        ## Agences Analysées
        {', '.join(agencies)}
        
        ## Recommandations
        - Continuer le monitoring des transactions
        - Analyser les tendances par agence
        - Maintenir la surveillance des montants élevés
        
        *Note : Ce rapport a été généré en mode de secours sans IA avancée.*
        """
        
        # Générer des visualisations de base
        visualizations = self._generate_visualizations_tool(df)
        
        return {
            "report": report,
            "visualizations": visualizations,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "data_points": len(df),
                "date_range": {
                    "start": df["date"].min().isoformat(),
                    "end": df["date"].max().isoformat()
                },
                "agencies": df["agence"].unique().tolist(),
                "execution_time": 0.0,
                "mode": "fallback"
            }
        }


# Créer une instance globale de l'agent
ai_agent = AIAgent() 
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

# Importations LangChain
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.llms import HuggingFaceHub

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
        logger.info(f"Agent IA initialisé (API alternative: {use_alternative_api})")
        
        # Initialiser le LLM
        if not use_alternative_api and OPENAI_API_KEY and OPENAI_API_KEY not in ["your-api-key-here", "dummy-openai-key"]:
            self.llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.7,
                openai_api_key=OPENAI_API_KEY
            )
            logger.info("Utilisation de l'API OpenAI")
        else:
            # Utiliser HuggingFace comme alternative
            if HUGGINGFACE_API_KEY and HUGGINGFACE_API_KEY not in ["your-api-key-here", "dummy-huggingface-key"]:
                self.llm = HuggingFaceHub(
                    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                    huggingfacehub_api_token=HUGGINGFACE_API_KEY
                )
                logger.info("Utilisation de l'API HuggingFace")
            else:
                # Fallback sur un mode simulé
                logger.warning("Aucune clé API valide trouvée, utilisation du mode simulé")
                self.llm = None
        
        # Initialiser la mémoire
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        
        # Initialiser les outils
        self.tools = self._create_tools()
        
        # Initialiser l'agent
        if self.llm:
            self.agent = self._create_agent()
        else:
            self.agent = None
            logger.warning("Agent non initialisé en raison de l'absence de LLM valide")
    
    def _create_tools(self) -> List[Tool]:
        """
        Créer les outils pour l'agent.
        
        Returns:
            Liste d'outils LangChain
        """
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
        
        try:
            # Sauvegarder temporairement les données pour les outils
            self._current_data = df
            
            # Calculer les statistiques de base
            stats = self._analyze_data_tool(df)
            
            # Générer les visualisations
            visualizations = self._generate_visualizations_tool(df)
            
            # Si aucun LLM n'est disponible, utiliser une réponse simulée
            if self.agent is None:
                logger.info("Utilisation d'une réponse simulée (pas de LLM disponible)")
                return self._generate_fallback_response(df)
            
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
                    "execution_time": None,  # Sera rempli par l'appelant
                    "model_used": "GPT-3.5" if not self.use_alternative_api else "Mistral-7B"
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des données: {e}")
            # Générer un rapport de secours
            return self._generate_fallback_response(df)
        finally:
            # Nettoyer les données temporaires
            self._current_data = None
    
    def _analyze_data_tool(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Outil pour analyser les données et générer des statistiques.
        
        Args:
            df: DataFrame contenant les données bancaires
            
        Returns:
            Dict contenant les statistiques
        """
        try:
            # Statistiques globales
            total_montant = df["montant"].sum()
            total_transactions = df["nombre_transactions"].sum()
            moyenne_montant = df["montant"].mean()
            
            # Statistiques par agence
            stats_by_agency = {}
            for agence in df["agence"].unique():
                agence_df = df[df["agence"] == agence]
                stats_by_agency[agence] = {
                    "total_montant": agence_df["montant"].sum(),
                    "total_transactions": agence_df["nombre_transactions"].sum(),
                    "moyenne_montant": agence_df["montant"].mean(),
                    "nombre_entrees": len(agence_df)
                }
            
            # Analyse temporelle
            df_sorted = df.sort_values("date")
            temporal_analysis = {
                "first_date": df_sorted["date"].iloc[0].isoformat(),
                "last_date": df_sorted["date"].iloc[-1].isoformat(),
                "trend": "stable"  # Simplification, à améliorer avec une vraie analyse de tendance
            }
            
            # Calculer l'évolution semaine par semaine
            today = datetime.now().date()
            seven_days_ago = today - timedelta(days=7)
            fourteen_days_ago = today - timedelta(days=14)
            
            # Sélectionner les données des dernières semaines
            last_week_data = df[df["date"] >= pd.Timestamp(seven_days_ago)]
            previous_week_data = df[
                (df["date"] < pd.Timestamp(seven_days_ago)) & 
                (df["date"] >= pd.Timestamp(fourteen_days_ago))
            ]
            
            # Calculer l'évolution
            last_week_montant = last_week_data["montant"].sum() if not last_week_data.empty else 0
            previous_week_montant = previous_week_data["montant"].sum() if not previous_week_data.empty else 1
            evolution_percentage = ((last_week_montant - previous_week_montant) / previous_week_montant) * 100 if previous_week_montant else 0
            
            # Résultat final
            return {
                "global": {
                    "total_montant": total_montant,
                    "total_transactions": total_transactions,
                    "moyenne_montant": moyenne_montant,
                    "evolution_percentage": evolution_percentage
                },
                "by_agency": stats_by_agency,
                "temporal": temporal_analysis
            }
            
        except Exception as e:
            logger.error(f"Erreur dans l'outil d'analyse de données: {e}")
            return {
                "global": {
                    "total_montant": 0,
                    "total_transactions": 0,
                    "moyenne_montant": 0,
                    "evolution_percentage": 0
                },
                "by_agency": {},
                "temporal": {
                    "first_date": "",
                    "last_date": "",
                    "trend": "unknown"
                }
            }
    
    def _generate_visualizations_tool(self, df: pd.DataFrame) -> List[Dict[str, str]]:
        """
        Outil pour générer des visualisations à partir des données.
        
        Args:
            df: DataFrame contenant les données bancaires
            
        Returns:
            Liste de dictionnaires contenant les chemins et titres des visualisations générées
        """
        # Créer un répertoire pour les visualisations si nécessaire
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Timestamp unique pour les fichiers
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        visualizations = []
        
        try:
            # Agrégation par agence
            agg_by_agency = df.groupby("agence").agg({
                "montant": "sum",
                "nombre_transactions": "sum"
            }).reset_index()
            
            # 1. Graphique à barres des montants par agence
            plt.figure(figsize=(10, 6))
            plt.bar(agg_by_agency["agence"], agg_by_agency["montant"])
            plt.title("Montant total par agence")
            plt.ylabel("Montant (€)")
            plt.xticks(rotation=45)
            plt.tight_layout()
            montant_path = output_dir / f"montant_par_agence_{timestamp}.png"
            plt.savefig(montant_path)
            plt.close()
            visualizations.append({
                "path": str(montant_path),
                "title": "Montant total par agence",
                "type": "bar_chart"
            })
            
            # 2. Graphique à barres du nombre de transactions par agence
            plt.figure(figsize=(10, 6))
            plt.bar(agg_by_agency["agence"], agg_by_agency["nombre_transactions"])
            plt.title("Nombre de transactions par agence")
            plt.ylabel("Nombre de transactions")
            plt.xticks(rotation=45)
            plt.tight_layout()
            transactions_path = output_dir / f"transactions_par_agence_{timestamp}.png"
            plt.savefig(transactions_path)
            plt.close()
            visualizations.append({
                "path": str(transactions_path),
                "title": "Nombre de transactions par agence",
                "type": "bar_chart"
            })
            
            # 3. Tendance sur le temps pour chaque agence
            plt.figure(figsize=(12, 8))
            for agence in df["agence"].unique():
                agence_df = df[df["agence"] == agence]
                agence_df = agence_df.sort_values("date")
                plt.plot(agence_df["date"], agence_df["montant"], label=agence)
            
            plt.title("Évolution des montants par agence")
            plt.ylabel("Montant (€)")
            plt.xlabel("Date")
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            evolution_path = output_dir / f"evolution_montants_{timestamp}.png"
            plt.savefig(evolution_path)
            plt.close()
            visualizations.append({
                "path": str(evolution_path),
                "title": "Évolution des montants par agence",
                "type": "line_chart"
            })
            
            logger.info(f"Visualisations générées: {len(visualizations)}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des visualisations: {e}")
        
        return visualizations
    
    def _get_historical_data_tool(self, period: str = "last_month") -> Dict[str, Any]:
        """
        Outil pour récupérer des données historiques.
        
        Args:
            period: Période pour laquelle récupérer les données historiques
            
        Returns:
            Dict contenant les données historiques
        """
        # Cette fonction est un placeholder, dans une implémentation réelle,
        # elle récupérerait les données historiques de la base de données
        return {
            "period": period,
            "data_available": False,
            "message": "Fonctionnalité non implémentée"
        }
    
    def _send_email_tool(self, recipient: str, subject: str, content: str, attachments: List[str] = None) -> Dict[str, Any]:
        """
        Outil pour envoyer un email.
        
        Args:
            recipient: Adresse email du destinataire
            subject: Sujet de l'email
            content: Contenu de l'email
            attachments: Liste des chemins des pièces jointes
            
        Returns:
            Dict contenant le statut de l'envoi
        """
        # Cette fonction est un placeholder, à implémenter dans le module d'emails
        return {
            "sent": False,
            "message": "Fonctionnalité non implémentée"
        }
    
    def _create_analysis_prompt(self, stats: Dict[str, Any]) -> str:
        """
        Créer un prompt pour l'agent basé sur les statistiques, au format mail de compte rendu d'analyse.
        """
        global_stats = stats["global"]
        formatted_montant = f"{global_stats['total_montant']:,.2f} €"
        formatted_evolution = f"{global_stats['evolution_percentage']:.2f}%"
        subject = f"Compte rendu hebdomadaire – Semaine en cours"
        mail_body = f"""
Objet : {subject}

Bonjour,

Veuillez trouver ci-dessous le compte rendu détaillé de l'activité pour la semaine analysée.

---

**Synthèse des résultats :**
- Montant total : {formatted_montant}
- Transactions totales : {global_stats['total_transactions']}
- Montant moyen par transaction : {global_stats['moyenne_montant']:,.2f} €
- Évolution sur la semaine : {formatted_evolution}

**Détail par agence :**
"""
        for agence, data in stats["by_agency"].items():
            mail_body += f"""
Agence : {agence}
- Montant total : {data['total_montant']:,.2f} €
- Transactions totales : {data['total_transactions']}
- Montant moyen par transaction : {data['moyenne_montant']:,.2f} €
        """
        mail_body += """
---

**Analyse et recommandations :**
- [L'IA ou l'analyste doit ici synthétiser les points forts, les axes d'amélioration, les alertes éventuelles, et proposer des recommandations concrètes.]

---
Cordialement,
La Direction

*Ce mail est généré automatiquement à partir des données consolidées de la semaine. Pour toute question, contactez le service reporting.*
"""
        return mail_body
    
    def _generate_fallback_response(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Générer une réponse de secours en cas d'échec de l'agent ou d'absence de LLM.
        Cette méthode crée un rapport basé sur les données réelles sans utiliser de LLM.
        
        Args:
            df: DataFrame contenant les données bancaires
            
        Returns:
            Dict contenant le rapport et des métadonnées associées
        """
        logger.info("Génération d'un rapport de secours sans LLM")
        
        # Vérifier si le DataFrame est vide
        if df.empty:
            report = "# Rapport d'Analyse Bancaire\n\nAucune donnée disponible pour l'analyse."
            return {
                "report": report,
                "visualizations": [],
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "data_points": 0,
                    "date_range": {"start": "", "end": ""},
                    "agencies": [],
                    "execution_time": None,
                    "model_used": "Fallback (pas de LLM)"
                }
            }
        
        # Calculer des statistiques de base
        total_montant = df["montant"].sum()
        total_transactions = df["nombre_transactions"].sum()
        nb_agences = df["agence"].nunique()
        
        # Statistiques par agence
        agence_stats = df.groupby("agence").agg({
            "montant": ["sum", "mean"],
            "nombre_transactions": ["sum", "mean"]
        })
        
        # Trouver l'agence avec le plus grand montant
        top_agence = agence_stats["montant"]["sum"].idxmax() if not agence_stats.empty else "N/A"
        top_montant = agence_stats["montant"]["sum"].max() if not agence_stats.empty else 0
        
        # Trouver l'agence avec le plus grand nombre de transactions
        top_agence_trans = agence_stats["nombre_transactions"]["sum"].idxmax() if not agence_stats.empty else "N/A"
        top_transactions = agence_stats["nombre_transactions"]["sum"].max() if not agence_stats.empty else 0
        
        # Évolution dans le temps (si possible)
        date_min = df["date"].min()
        date_max = df["date"].max()
        period_days = (date_max - date_min).days + 1 if isinstance(date_min, pd.Timestamp) else 0
        
        # Générer le rapport
        report = f"""
# Rapport d'Analyse Bancaire

## Résumé

Période d'analyse: du {date_min.strftime('%d/%m/%Y') if isinstance(date_min, pd.Timestamp) else 'N/A'} au {date_max.strftime('%d/%m/%Y') if isinstance(date_max, pd.Timestamp) else 'N/A'} ({period_days} jours)

- **Montant total des transactions**: {total_montant:,.2f} €
- **Nombre total de transactions**: {total_transactions:,}
- **Nombre d'agences analysées**: {nb_agences}

## Performance des Agences

"""
        
        # Ajouter des détails pour chaque agence
        for agence, stats in agence_stats.iterrows():
            montant_sum = stats["montant"]["sum"]
            montant_mean = stats["montant"]["mean"]
            trans_sum = stats["nombre_transactions"]["sum"]
            trans_mean = stats["nombre_transactions"]["mean"]
            
            part_montant = (montant_sum / total_montant) * 100 if total_montant > 0 else 0
            
            report += f"""### Agence {agence}

- **Montant total**: {montant_sum:,.2f} € ({part_montant:.1f}% du total)
- **Montant moyen par jour**: {montant_mean:,.2f} €
- **Nombre total de transactions**: {trans_sum:,}
- **Nombre moyen de transactions par jour**: {trans_mean:.1f}

"""
        
        # Ajouter des observations
        report += f"""## Observations Clés

- L'agence **{top_agence}** a réalisé le plus grand volume financier avec **{top_montant:,.2f} €**.
- L'agence **{top_agence_trans}** a traité le plus grand nombre de transactions avec **{top_transactions:,}** opérations.

## Recommandations

1. **Partage des bonnes pratiques**: Organiser un échange entre les agences performantes et les autres pour partager les stratégies efficaces.
2. **Analyse approfondie**: Mener une analyse plus détaillée des facteurs de succès de l'agence {top_agence}.
3. **Suivi régulier**: Mettre en place un suivi hebdomadaire des indicateurs clés de performance pour chaque agence.

*Ce rapport a été généré automatiquement par le Système d'Automatisation des Rapports Bancaires en mode de secours (sans LLM).*
"""
        
        # Générer des visualisations
        visualizations = self._generate_visualizations_tool(df)
        
        # Préparer la réponse
        result = {
            "report": report,
            "visualizations": visualizations,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "data_points": len(df),
                "date_range": {
                    "start": date_min.isoformat() if isinstance(date_min, pd.Timestamp) else "",
                    "end": date_max.isoformat() if isinstance(date_max, pd.Timestamp) else ""
                },
                "agencies": df["agence"].unique().tolist(),
                "execution_time": None,  # Sera rempli par l'appelant
                "model_used": "Fallback (pas de LLM)"
            }
        }
        
        return result


# Instance singleton de l'agent
ai_agent = AIAgent() 
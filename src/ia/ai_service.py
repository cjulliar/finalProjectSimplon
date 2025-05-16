#!/usr/bin/env python3
"""
Service d'IA pour l'analyse des données bancaires.
Ce module fournit des fonctionnalités d'analyse de données bancaires utilisant
des modèles de langage (LLM) comme OpenAI ou HuggingFace via LangChain.
"""
import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import re

import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import requests
import numpy as np
import seaborn as sns
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import markdown

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import BankData, BankDataRaw, EmailReport

# Importation des services LangChain et Email
from src.ia.langchain_agent import ai_agent
from src.ia.email_service import email_service

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration de l'API OpenAI ou autre API LLM
API_KEY = os.getenv("LLM_API_KEY", "")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

# Par défaut, utiliser le mode de secours sans LLM pour éviter les coûts
USE_HUGGINGFACE = os.getenv("USE_HUGGINGFACE", "false").lower() == "true"
USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"
USE_FALLBACK_MODE = os.getenv("USE_FALLBACK_MODE", "true").lower() == "true"
USE_ALTERNATIVE_API = os.getenv("USE_ALTERNATIVE_API", "false").lower() == "true"

# Banques pour le développement
FILTERED_BANKS = ["Banque A", "Banque B", "Banque C", "Banque D"]

# Importer les modules conditionnellement pour éviter les erreurs si les clés ne sont pas configurées
if USE_OPENAI:
    try:
        import openai
        openai.api_key = API_KEY
        logger.info("OpenAI API activée")
    except ImportError:
        logger.warning("Module OpenAI non disponible, désactivation de l'API OpenAI")
        USE_OPENAI = False

if USE_HUGGINGFACE:
    try:
        from langchain_huggingface import HuggingFaceEndpoint
        logger.info("HuggingFace API activée")
    except ImportError:
        logger.warning("Module HuggingFace non disponible, désactivation de l'API HuggingFace")
        USE_HUGGINGFACE = False

# Si aucune API n'est disponible, activer le mode de secours
if not (USE_OPENAI or USE_HUGGINGFACE):
    logger.warning("Aucune API LLM disponible, activation du mode de secours")
    USE_FALLBACK_MODE = True

# Déterminer si on utilise une API alternative
USE_ALTERNATIVE_API = USE_HUGGINGFACE or not API_KEY or API_KEY in ["your-api-key-here", "dummy-openai-key"]

# Si USE_OPENAI est explicitement défini à true, on force l'utilisation d'OpenAI
if USE_OPENAI and API_KEY and API_KEY not in ["your-api-key-here", "dummy-openai-key"]:
    USE_ALTERNATIVE_API = False
    USE_FALLBACK_MODE = False

# Charger les variables d'environnement
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "localhost")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "25"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "noreply@example.com")

class AIAnalysisService:
    """Service d'analyse par IA des données bancaires."""
    
    def __init__(self, use_alternative_api: bool = USE_ALTERNATIVE_API, use_fallback_mode: bool = USE_FALLBACK_MODE):
        """
        Initialiser le service d'analyse IA.
        
        Args:
            use_alternative_api (bool): Si True, utilise une API alternative (HuggingFace)
                                       au lieu d'OpenAI.
            use_fallback_mode (bool): Si True, utilise un mode de secours sans LLM.
        """
        self.use_alternative_api = use_alternative_api
        self.use_fallback_mode = use_fallback_mode
        
        # Utiliser l'agent LangChain avec la même configuration
        self.agent = ai_agent
        
        # Utiliser le service d'emails
        self.email_service = email_service
        
        if self.use_fallback_mode:
            logger.info("Service d'analyse IA initialisé en mode de secours (sans LLM)")
        else:
            logger.info(f"Service d'analyse IA initialisé (API alternative: {use_alternative_api})")
    
    def analyze_bank_data(self, data: Union[pd.DataFrame, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Analyser les données bancaires avec un LLM et générer un rapport.
        
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
        
        # Mesurer le temps d'exécution
        start_time = time.time()
        
        try:
            # Si le mode de secours est activé, utiliser directement la méthode legacy
            if self.use_fallback_mode:
                logger.info("Utilisation du mode de secours (sans LLM)")
                result = self._legacy_analyze_bank_data(df)
                
                # Ajouter le temps d'exécution
                execution_time = time.time() - start_time
                result["metadata"]["execution_time"] = execution_time
                
                logger.info(f"Analyse terminée en {execution_time:.2f} secondes (mode de secours)")
                return result
            
            # Sinon, utiliser l'agent LangChain pour l'analyse
            logger.info("Analyse des données avec l'agent LangChain")
            result = self.agent.analyze_bank_data(df)
            
            # Ajouter le temps d'exécution
            execution_time = time.time() - start_time
            result["metadata"]["execution_time"] = execution_time
            
            logger.info(f"Analyse terminée en {execution_time:.2f} secondes")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse avec LangChain: {e}")
            # Fallback sur l'ancienne méthode
            return self._legacy_analyze_bank_data(df)
    
    def _legacy_analyze_bank_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Méthode d'analyse legacy (ancienne version) utilisée comme fallback.
        
        Args:
            df: DataFrame contenant les données bancaires
            
        Returns:
            Dict contenant le rapport et des métadonnées associées
        """
        logger.warning("Utilisation de la méthode d'analyse legacy (fallback)")
        
        # Générer rapport textuel
        prompt = self._prepare_prompt(df)
        report_text = self._generate_report(prompt)
        
        # Générer visualisations
        visualizations = self._generate_visualizations(df)
        
        # Préparer la réponse
        result = {
            "report": report_text,
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
                "model_used": "Legacy (OpenAI direct)" if not self.use_alternative_api else "Legacy (HuggingFace direct)"
            }
        }
        
        return result
    
    def send_report_by_email(self, report_data, recipients, subject=None, bank_name=None, user_id=None, scheduled_report_id=None):
        """
        Envoyer le rapport par email et l'enregistrer dans la base de données.
        
        Args:
            report_data (dict): Données du rapport
            recipients (list): Liste des destinataires
            subject (str, optional): Sujet de l'email
            bank_name (str, optional): Nom de la banque analysée
            user_id (int, optional): ID de l'utilisateur qui a demandé le rapport
            scheduled_report_id (str, optional): ID du rapport planifié associé
            
        Returns:
            dict: Résultat de l'envoi d'email
        """
        import uuid
        from src.db.models import EmailReport
        from src.db.database import get_db

        if not subject:
            subject = f"Rapport d'analyse bancaire - {datetime.now().strftime('%d/%m/%Y')}"
        
        if not bank_name and "metadata" in report_data:
            bank_name = report_data["metadata"].get("bank_name", "Toutes les banques")
        
        try:
            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = EMAIL_FROM
            msg['To'] = ", ".join(recipients)
            
            # Ajouter le contenu en texte brut
            text_content = report_data.get("report", "Rapport non disponible")
            msg.attach(MIMEText(text_content, 'plain'))
            
            # Convertir le markdown en HTML pour l'email
            html_content = markdown.markdown(text_content)
            msg.attach(MIMEText(html_content, 'html'))
            
            # Ajouter les visualisations en pièces jointes
            visualizations = report_data.get("visualizations", [])
            for viz in visualizations:
                with open(viz["path"], 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(viz["path"]))
                    msg.attach(img)
            
            # Simuler l'envoi d'email (pour le développement)
            logger.info(f"Simulation d'envoi d'email à {recipients}")
            logger.info(f"Sujet: {subject}")
            logger.info(f"Contenu: {text_content[:100]}...")
            logger.info(f"Pièces jointes: {[os.path.basename(viz['path']) for viz in visualizations]}")
            
            # Pour une implémentation réelle, décommenter le code suivant:
            """
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                if SMTP_USERNAME and SMTP_PASSWORD:
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(EMAIL_FROM, recipients, msg.as_string())
            """
            
            # Enregistrer le rapport dans la base de données
            email_report_id = str(uuid.uuid4())
            status = "sent"  # ou "simulated" en mode développement
            
            # Utiliser le contexte de base de données
            with get_db() as db:
                email_report = EmailReport(
                    id=email_report_id,
                    user_id=user_id if user_id else 1,  # Utilisateur par défaut si non spécifié
                    bank_name=bank_name if bank_name else "Non spécifié",
                    subject=subject,
                    recipients=recipients,
                    content=html_content,
                    sent_at=datetime.now(),
                    scheduled_report_id=scheduled_report_id,
                    status=status
                )
                db.add(email_report)
                db.commit()
                
                logger.info(f"Rapport email enregistré avec l'ID: {email_report_id}")
            
            return {
                "success": True,
                "message": f"Email envoyé avec succès à {len(recipients)} destinataires (simulation)",
                "email_report_id": email_report_id
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
            
            # Enregistrer l'échec dans la base de données si possible
            try:
                email_report_id = str(uuid.uuid4())
                with get_db() as db:
                    email_report = EmailReport(
                        id=email_report_id,
                        user_id=user_id if user_id else 1,
                        bank_name=bank_name if bank_name else "Non spécifié",
                        subject=subject,
                        recipients=recipients,
                        content="Erreur lors de l'envoi: " + str(e),
                        sent_at=datetime.now(),
                        scheduled_report_id=scheduled_report_id,
                        status="failed"
                    )
                    db.add(email_report)
                    db.commit()
                    logger.info(f"Échec du rapport email enregistré avec l'ID: {email_report_id}")
            except Exception as db_error:
                logger.error(f"Erreur lors de l'enregistrement de l'échec d'envoi: {str(db_error)}")
            
            return {
                "success": False,
                "message": f"Erreur lors de l'envoi de l'email: {str(e)}"
            }
    
    def schedule_periodic_report(self, 
                              schedule_type: str = "weekly",
                              day: int = 1,
                              recipients: List[str] = None) -> Dict[str, Any]:
        """
        Planifier un rapport périodique.
        
        Args:
            schedule_type: Type de planification ('daily', 'weekly', 'monthly')
            day: Jour d'envoi (dépend du type de planification)
            recipients: Liste des destinataires
            
        Returns:
            Dict contenant le statut de la planification
        """
        logger.info(f"Planification d'un rapport {schedule_type}")
        
        return self.email_service.schedule_report(
            schedule_type=schedule_type,
            day=day,
            recipients=recipients
        )
    
    # Les méthodes suivantes sont conservées pour la compatibilité avec l'ancienne version
    # et sont utilisées par la méthode legacy_analyze_bank_data
    
    def _prepare_prompt(self, df: pd.DataFrame) -> str:
        """
        Préparer le prompt pour l'IA en extrayant les statistiques des données.
        
        Args:
            df: DataFrame contenant les données bancaires
            
        Returns:
            str: Prompt formaté pour l'IA
        """
        # Préparation des statistiques essentielles pour l'analyse
        total_montant = df["montant"].sum() if not df.empty else 0
        total_transactions = df["nombre_transactions"].sum() if not df.empty else 0
        moyenne_montant = df["montant"].mean() if not df.empty else 0
        
        # Agrégations par agence
        if not df.empty:
            agg_by_agency = df.groupby("agence").agg({
                "montant": ["sum", "mean"],
                "nombre_transactions": ["sum", "mean"]
            })
            
            # Trouver l'agence la plus performante
            best_agency = agg_by_agency[("montant", "sum")].idxmax() if not agg_by_agency.empty else "Aucune"
        else:
            best_agency = "Aucune"
        
        # Pour l'analyse de l'évolution semaine par semaine, éviter les comparaisons directes
        # qui peuvent causer des problèmes de type entre date et datetime
        last_week_montant = 0
        previous_week_montant = 1  # Éviter division par zéro
        
        if not df.empty:
            # Traiter les données de date de manière sécurisée
            today = datetime.now().date()
            seven_days_ago = today - timedelta(days=7)
            fourteen_days_ago = today - timedelta(days=14)
            
            # Utiliser des chaînes de caractères pour les comparaisons pour éviter les problèmes de type
            df_with_str_dates = df.copy()
            df_with_str_dates['date_str'] = df_with_str_dates['date'].astype(str)
            seven_days_ago_str = seven_days_ago.isoformat()
            fourteen_days_ago_str = fourteen_days_ago.isoformat()
            
            # Sélectionner les données des dernières semaines en utilisant des comparaisons de chaînes
            last_week_data = df_with_str_dates[df_with_str_dates['date_str'] >= seven_days_ago_str]
            previous_week_data = df_with_str_dates[
                (df_with_str_dates['date_str'] < seven_days_ago_str) & 
                (df_with_str_dates['date_str'] >= fourteen_days_ago_str)
            ]
            
            # Calculer les montants par semaine
            last_week_montant = last_week_data["montant"].sum() if not last_week_data.empty else 0
            previous_week_montant = previous_week_data["montant"].sum() if not previous_week_data.empty else 1  # Éviter division par zéro
        
        # Calculer l'évolution en pourcentage
        evolution_percentage = ((last_week_montant - previous_week_montant) / previous_week_montant) * 100 if previous_week_montant else 0
        
        # Préparation des données pour le prompt
        stats = {
            "total_montant": f"{total_montant:,.2f} €",
            "total_transactions": total_transactions,
            "moyenne_montant": f"{moyenne_montant:,.2f} €",
            "meilleure_agence": best_agency,
            "evolution_semaine": f"{evolution_percentage:.2f}%"
        }
        
        # Statistiques par agence
        agency_stats = {}
        for agence in df["agence"].unique():
            agence_df = df[df["agence"] == agence]
            agency_stats[agence] = {
                "total_montant": f"{agence_df['montant'].sum():,.2f} €",
                "total_transactions": agence_df["nombre_transactions"].sum(),
                "moyenne_montant": f"{agence_df['montant'].mean():,.2f} €"
            }
        
        # Construction du prompt pour l'IA
        prompt = f"""
        Analyser les données bancaires suivantes et générer un rapport détaillé pour le directeur.
        
        STATISTIQUES GLOBALES:
        - Montant total: {stats['total_montant']}
        - Transactions totales: {stats['total_transactions']}
        - Montant moyen par transaction: {stats['moyenne_montant']}
        - Évolution sur la semaine: {stats['evolution_semaine']}
        
        STATISTIQUES PAR AGENCE:
        """
        
        for agence, data in agency_stats.items():
            prompt += f"""
        {agence}:
        - Montant total: {data['total_montant']}
        - Transactions totales: {data['total_transactions']}
        - Montant moyen par transaction: {data['moyenne_montant']}
        """
        
        prompt += """
        INSTRUCTIONS:
        1. Analyser les performances de chaque agence
        2. Identifier les tendances et anomalies
        3. Proposer des recommandations stratégiques
        4. Rédiger un rapport structuré en français, avec introduction, analyse et conclusion
        5. Le rapport doit être destiné au directeur du groupe bancaire
        """
        
        return prompt
    
    def _generate_report(self, prompt: str) -> str:
        """
        Générer un rapport à partir d'un prompt en utilisant un LLM.
        
        Args:
            prompt: Prompt à envoyer au LLM
            
        Returns:
            Rapport généré
        """
        # En mode de secours, générer un rapport factice
        if self.use_fallback_mode:
            logger.warning("Mode de secours activé, génération d'un rapport factice")
            return self._generate_fallback_report(prompt)
        
        # Sinon, essayer d'utiliser les LLM
        try:
            if not self.use_alternative_api:
                # Utiliser OpenAI
                if not API_KEY or API_KEY in ["your-api-key-here", "dummy-openai-key"]:
                    logger.warning("Clé API OpenAI non valide, utilisation du mode de secours")
                    return self._generate_fallback_report(prompt)
                
                logger.info("Génération du rapport avec OpenAI")
                return self._call_openai(prompt)
            else:
                # Utiliser une API alternative
                if not HUGGINGFACE_API_KEY or HUGGINGFACE_API_KEY in ["your-api-key-here", "dummy-huggingface-key"]:
                    logger.warning("Clé API HuggingFace non valide, utilisation du mode de secours")
                    return self._generate_fallback_report(prompt)
                
                logger.info("Génération du rapport avec l'API alternative")
                return self._call_alternative_llm(prompt)
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport: {e}")
            return self._generate_fallback_report(prompt)
    
    def _call_openai(self, prompt: str) -> str:
        """Appeler l'API OpenAI pour générer un rapport."""
        try:
            import openai
            openai.api_key = API_KEY
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Vous êtes un analyste financier expert spécialisé dans l'analyse de données bancaires."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à l'API OpenAI: {e}")
            return self._call_alternative_llm(prompt)
    
    def _call_alternative_llm(self, prompt: str) -> str:
        """Appeler une API alternative (HuggingFace) pour générer un rapport."""
        try:
            # Utilisation de l'API HuggingFace comme alternative
            API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
            headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
            
            # Si pas de clé HuggingFace, utiliser la méthode de fallback
            if not HUGGINGFACE_API_KEY:
                logger.warning("Pas de clé API HuggingFace, fallback sur rapport simulé")
                return self._generate_fallback_report(prompt)
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 1024,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload)
            if response.status_code != 200:
                logger.error(f"Erreur API HuggingFace: {response.status_code} - {response.text}")
                return self._generate_fallback_report(prompt)
                
            return response.json()[0]["generated_text"]
            
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à l'API alternative: {e}")
            return self._generate_fallback_report(prompt)
    
    def _generate_fallback_report(self, prompt: str) -> str:
        """
        Générer un rapport de secours si les API ne sont pas disponibles.
        Cette méthode crée un rapport basé sur les statistiques extraites du prompt
        sans utiliser de LLM.
        
        Args:
            prompt: Prompt original contenant les statistiques
            
        Returns:
            str: Rapport simulé basé sur les statistiques disponibles
        """
        logger.warning("Génération d'un rapport de secours (fallback)")
        
        # Extraire quelques statistiques du prompt pour les inclure dans la réponse simulée
        lines = prompt.strip().split('\n')
        stats = {}
        
        # Extraire les statistiques globales
        for line in lines:
            if "Montant total:" in line:
                stats["montant_total"] = line.split(":")[1].strip()
            if "Évolution sur la semaine:" in line:
                stats["evolution"] = line.split(":")[1].strip()
            if "Nombre de transactions:" in line:
                stats["transactions"] = line.split(":")[1].strip()
        
        # Extraire les statistiques par agence
        agencies = []
        agency_section = False
        current_agency = None
        
        for line in lines:
            if "STATISTIQUES PAR AGENCE:" in line:
                agency_section = True
                continue
            
            if agency_section:
                if line.strip() and not line.startswith(" ") and ":" not in line:
                    current_agency = line.strip()
                    agencies.append({"name": current_agency, "stats": {}})
                elif current_agency and ":" in line:
                    key, value = line.split(":", 1)
                    agencies[-1]["stats"][key.strip()] = value.strip()
        
        # Créer une réponse simulée basée sur les statistiques extraites
        report = f"""
# Rapport d'Analyse Bancaire Hebdomadaire

## Introduction

Ce rapport présente l'analyse des performances des différentes agences bancaires pour la période écoulée. Le montant total des transactions s'élève à {stats.get("montant_total", "plusieurs millions d'euros")}, avec une évolution de {stats.get("evolution", "variation significative")} par rapport à la semaine précédente. Au total, {stats.get("transactions", "un nombre important de")} transactions ont été réalisées.

## Analyse des Performances par Agence
"""
        
        # Ajouter des détails pour chaque agence extraite du prompt
        if agencies:
            for agency in agencies:
                report += f"""
### {agency["name"]}
"""
                if "Montant total" in agency["stats"]:
                    report += f"- Montant total: {agency['stats']['Montant total']}\n"
                if "Nombre de transactions" in agency["stats"]:
                    report += f"- Nombre de transactions: {agency['stats']['Nombre de transactions']}\n"
                if "Évolution" in agency["stats"]:
                    report += f"- Évolution: {agency['stats']['Évolution']}\n"
                
                # Ajouter une analyse simulée pour chaque agence
                evolution = agency["stats"].get("Évolution", "").lower()
                if "hausse" in evolution:
                    report += f"""
L'agence {agency["name"]} montre une tendance à la hausse prometteuse. Sa stratégie d'acquisition de nouveaux clients paraît efficace et devrait être étudiée pour une possible application dans les autres agences.
"""
                elif "baisse" in evolution:
                    report += f"""
L'agence {agency["name"]} présente une baisse d'activité qui mérite une attention particulière. Une analyse des facteurs contribuant à cette diminution devrait être menée rapidement.
"""
                else:
                    report += f"""
L'agence {agency["name"]} maintient des performances stables. Sa stratégie de fidélisation client semble porter ses fruits, comme en témoigne la régularité des transactions.
"""
        else:
            # Si aucune agence n'a été extraite, utiliser un texte générique
            report += """
### Performances générales
Les performances des agences sont variables, avec certaines montrant une croissance stable tandis que d'autres présentent des fluctuations plus importantes.
"""
        
        # Ajouter des recommandations génériques
        report += """
## Recommandations Stratégiques

1. **Partage des bonnes pratiques** : Organiser un workshop entre les responsables d'agences pour partager les stratégies qui fonctionnent.

2. **Diversification des portefeuilles clients** : Les agences présentant une volatilité importante pourraient bénéficier d'une diversification de leur clientèle.

3. **Analyse des tendances** : Mettre en place un suivi plus détaillé des tendances par segment de clientèle pour identifier les opportunités de croissance.

## Conclusion

Les performances globales montrent des signes encourageants malgré quelques variations entre les agences. La mise en œuvre des recommandations proposées devrait permettre d'optimiser les résultats à court et moyen terme.

*Ce rapport a été généré automatiquement par le Système d'Automatisation des Rapports Bancaires en mode de secours (sans LLM).*
"""
        
        return report
    
    def _generate_visualizations(self, df: pd.DataFrame) -> List[Dict[str, str]]:
        """
        Générer des visualisations à partir des données.
        
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

    def analyze_bank_by_name(self, bank_name):
        """
        Analyser les données d'une banque spécifique.
        
        Args:
            bank_name (str): Nom de la banque à analyser
            
        Returns:
            dict: Rapport d'analyse avec métadonnées
        """
        start_time = datetime.now()
        
        try:
            # Récupérer les données depuis la base de données
            from sqlalchemy.orm import Session
            from src.db.database import engine
            
            db = Session(engine)
            try:
                query = db.query(BankDataRaw).filter(BankDataRaw.bank_name == bank_name)
                data = query.order_by(BankDataRaw.week_id).all()
            finally:
                db.close()
            
            if not data:
                return {
                    "report": f"Aucune donnée trouvée pour la banque {bank_name}.",
                    "metadata": {
                        "error": f"Aucune donnée pour {bank_name}",
                        "bank_name": bank_name,
                        "execution_time": (datetime.now() - start_time).total_seconds()
                    }
                }
            
            # Convertir les données en DataFrame
            df_rows = []
            for item in data:
                row = {
                    "week_id": item.week_id,
                    "group_name": item.group_name,
                    "bank_name": item.bank_name,
                }
                
                # Gérer le cas où raw_data est une chaîne JSON ou un dictionnaire
                if isinstance(item.raw_data, str):
                    try:
                        row.update(json.loads(item.raw_data))
                    except json.JSONDecodeError as e:
                        logger.error(f"Erreur de décodage JSON pour {bank_name}, week_id {item.week_id}: {str(e)}")
                        continue
                elif isinstance(item.raw_data, dict):
                    row.update(item.raw_data)
                else:
                    logger.error(f"Format de données non pris en charge pour {bank_name}, week_id {item.week_id}: {type(item.raw_data)}")
                    continue
                
                df_rows.append(row)
            
            if not df_rows:
                return {
                    "report": f"Aucune donnée utilisable trouvée pour la banque {bank_name}.",
                    "metadata": {
                        "error": f"Aucune donnée utilisable pour {bank_name}",
                        "bank_name": bank_name,
                        "execution_time": (datetime.now() - start_time).total_seconds()
                    }
                }
            
            df = pd.DataFrame(df_rows)
            
            # Générer des visualisations
            visualizations = self._generate_bank_visualizations(df, bank_name)
            
            # Générer le rapport textuel
            report_text = self._generate_bank_report_text(df, bank_name, visualizations)
            
            # Préparer les métadonnées
            metadata = {
                "bank_name": bank_name,
                "data_points": len(df),
                "date_range": {
                    "start": f"Semaine {df['week_id'].min()}",
                    "end": f"Semaine {df['week_id'].max()}"
                },
                "group_name": df["group_name"].iloc[0] if not df["group_name"].empty else "N/A",
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "model_used": "Statistical Analysis",
                "visualizations": [v["path"] for v in visualizations] if visualizations else []
            }
            
            return {
                "report": report_text,
                "metadata": metadata,
                "visualizations": visualizations
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des données pour {bank_name}: {str(e)}")
            return {
                "report": f"Une erreur est survenue lors de l'analyse de {bank_name}: {str(e)}",
                "metadata": {
                    "error": str(e),
                    "bank_name": bank_name,
                    "execution_time": (datetime.now() - start_time).total_seconds()
                }
            }

    def analyze_all_filtered_banks(self):
        """
        Analyser toutes les banques filtrées et compiler les résultats.
        
        Returns:
            dict: Rapport d'analyse compilé avec métadonnées
        """
        start_time = datetime.now()
        results = {}
        
        for bank in FILTERED_BANKS:
            results[bank] = self.analyze_bank_by_name(bank)
        
        # Compiler les résultats
        compiled_report = "# Rapport d'analyse des banques filtrées\n\n"
        compiled_report += f"Date: {datetime.now().strftime('%d/%m/%Y')}\n\n"
        
        # Résumé global
        compiled_report += "## Résumé global\n\n"
        total_data_points = sum(r.get("metadata", {}).get("data_points", 0) for r in results.values() if "error" not in r.get("metadata", {}))
        banks_with_data = sum(1 for r in results.values() if "error" not in r.get("metadata", {}))
        
        compiled_report += f"Ce rapport compile l'analyse de {banks_with_data} banques sur {len(FILTERED_BANKS)} banques filtrées.\n"
        compiled_report += f"Total de points de données analysés: {total_data_points}\n\n"
        
        # Tableau comparatif
        compiled_report += "## Tableau comparatif\n\n"
        compiled_report += "| Banque | Groupe | Montant Part. | Montant Pro. | Occ. Part. | Occ. Pro. | Tendance Part. | Tendance Pro. |\n"
        compiled_report += "|--------|--------|--------------|-------------|------------|-----------|----------------|---------------|\n"
        
        for bank, result in results.items():
            if "error" in result.get("metadata", {}):
                compiled_report += f"| {bank} | N/A | N/A | N/A | N/A | N/A | N/A | N/A |\n"
            else:
                # Extraire les informations du rapport texte
                report_text = result.get("report", "")
                
                # Extraire le groupe (peut varier selon la structure du rapport)
                group_match = re.search(r"\*\*Groupe\*\*: ([^\n]+)", report_text)
                group = group_match.group(1) if group_match else "N/A"
                
                # Extraire les montants
                montant_part_match = re.search(r"\*\*Montant total \(particuliers\)\*\*: ([^\n]+)", report_text)
                montant_part = montant_part_match.group(1) if montant_part_match else "N/A"
                
                montant_pro_match = re.search(r"\*\*Montant total \(professionnels\)\*\*: ([^\n]+)", report_text)
                montant_pro = montant_pro_match.group(1) if montant_pro_match else "N/A"
                
                # Extraire les occurrences
                occ_part_match = re.search(r"\*\*Nombre d'occurrences \(particuliers\)\*\*: ([^\n]+)", report_text)
                occ_part = occ_part_match.group(1) if occ_part_match else "N/A"
                
                occ_pro_match = re.search(r"\*\*Nombre d'occurrences \(professionnels\)\*\*: ([^\n]+)", report_text)
                occ_pro = occ_pro_match.group(1) if occ_pro_match else "N/A"
                
                # Extraire les tendances
                trend_part_match = re.search(r"Les montants pour les particuliers sont ([^\n\.]+)", report_text)
                trend_part = trend_part_match.group(1) if trend_part_match else "N/A"
                
                trend_pro_match = re.search(r"Les montants pour les professionnels sont ([^\n\.]+)", report_text)
                trend_pro = trend_pro_match.group(1) if trend_pro_match else "N/A"
                
                compiled_report += f"| {bank} | {group} | {montant_part} | {montant_pro} | {occ_part} | {occ_pro} | {trend_part} | {trend_pro} |\n"
        
        # Rapports individuels
        compiled_report += "\n## Rapports individuels\n\n"
        for bank, result in results.items():
            compiled_report += f"### {bank}\n\n"
            if "error" in result.get("metadata", {}):
                compiled_report += f"**Erreur**: {result['metadata']['error']}\n\n"
            else:
                # Inclure un résumé du rapport individuel
                report_lines = result.get("report", "").split("\n")
                summary_lines = []
                in_summary = False
                
                for line in report_lines:
                    if "## Résumé" in line:
                        in_summary = True
                        summary_lines.append(line)
                    elif in_summary and line.startswith("##"):
                        in_summary = False
                    elif in_summary:
                        summary_lines.append(line)
                
                # Ajouter le résumé et un lien vers le rapport complet
                if summary_lines:
                    compiled_report += "\n".join(summary_lines) + "\n\n"
                
                # Ajouter les liens vers les visualisations
                visualizations = result.get("visualizations", [])
                if visualizations:
                    compiled_report += "#### Visualisations\n\n"
                    for viz in visualizations:
                        compiled_report += f"- [{viz['title']}]({viz['path']})\n"
                    compiled_report += "\n"
                
                # Ajouter un lien vers le rapport complet
                if "metadata" in result and "visualizations" in result["metadata"]:
                    report_file = result["metadata"].get("report_file", "")
                    if report_file:
                        compiled_report += f"[Voir le rapport complet]({report_file})\n\n"
        
        # Préparer les métadonnées compilées
        metadata = {
            "banks_analyzed": len(results),
            "banks_with_data": banks_with_data,
            "total_data_points": total_data_points,
            "execution_time": (datetime.now() - start_time).total_seconds(),
            "individual_reports": {bank: r.get("metadata", {}) for bank, r in results.items()}
        }
        
        # Sauvegarder le rapport compilé
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        report_file = output_dir / f"rapport_global_{timestamp}.markdown"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(compiled_report)
        
        metadata["report_file"] = str(report_file)
        
        metadata_file = output_dir / f"metadata_global_{timestamp}.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)
        
        return {
            "report": compiled_report,
            "metadata": metadata,
            "individual_reports": results
        }

    def _generate_bank_visualizations(self, df, bank_name):
        """
        Générer des visualisations pour une banque spécifique.
        
        Args:
            df (DataFrame): Données de la banque
            bank_name (str): Nom de la banque
            
        Returns:
            list: Liste des visualisations générées
        """
        visualizations = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        try:
            # 1. Évolution des montants (particuliers vs professionnels)
            plt.figure(figsize=(12, 6))
            plt.plot(df["week_id"], df["SOMME_PART"], marker='o', label="Particuliers")
            plt.plot(df["week_id"], df["SOMME_PRO"], marker='s', label="Professionnels")
            plt.title(f"Évolution des montants - {bank_name}")
            plt.xlabel("Semaine")
            plt.ylabel("Montant (€)")
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # Sauvegarder la figure
            fig_path = output_dir / f"evolution_montants_{bank_name}_{timestamp}.png"
            plt.savefig(fig_path)
            plt.close()
            
            visualizations.append({
                "title": f"Évolution des montants - {bank_name}",
                "description": "Évolution des montants pour les clients particuliers et professionnels",
                "path": str(fig_path),
                "type": "line_chart"
            })
            
            # 2. Occurrences (particuliers vs professionnels)
            plt.figure(figsize=(12, 6))
            plt.plot(df["week_id"], df["OCC_PART"], marker='o', label="Particuliers")
            plt.plot(df["week_id"], df["OCC_PRO"], marker='s', label="Professionnels")
            plt.title(f"Évolution des occurrences - {bank_name}")
            plt.xlabel("Semaine")
            plt.ylabel("Nombre d'occurrences")
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # Sauvegarder la figure
            fig_path = output_dir / f"evolution_occurrences_{bank_name}_{timestamp}.png"
            plt.savefig(fig_path)
            plt.close()
            
            visualizations.append({
                "title": f"Évolution des occurrences - {bank_name}",
                "description": "Évolution du nombre d'occurrences pour les clients particuliers et professionnels",
                "path": str(fig_path),
                "type": "line_chart"
            })
            
            # 3. Montant moyen par occurrence
            plt.figure(figsize=(12, 6))
            montant_moyen_part = df["SOMME_PART"] / df["OCC_PART"].replace(0, np.nan)
            montant_moyen_pro = df["SOMME_PRO"] / df["OCC_PRO"].replace(0, np.nan)
            
            plt.plot(df["week_id"], montant_moyen_part, marker='o', label="Particuliers")
            plt.plot(df["week_id"], montant_moyen_pro, marker='s', label="Professionnels")
            plt.title(f"Montant moyen par occurrence - {bank_name}")
            plt.xlabel("Semaine")
            plt.ylabel("Montant moyen (€)")
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # Sauvegarder la figure
            fig_path = output_dir / f"montant_moyen_{bank_name}_{timestamp}.png"
            plt.savefig(fig_path)
            plt.close()
            
            visualizations.append({
                "title": f"Montant moyen par occurrence - {bank_name}",
                "description": "Évolution du montant moyen par occurrence pour les clients particuliers et professionnels",
                "path": str(fig_path),
                "type": "line_chart"
            })
            
            return visualizations
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des visualisations pour {bank_name}: {str(e)}")
            return []

    def _generate_bank_report_text(self, df, bank_name, visualizations):
        """
        Générer le texte du rapport pour une banque spécifique.
        
        Args:
            df (DataFrame): Données de la banque
            bank_name (str): Nom de la banque
            visualizations (list): Liste des visualisations générées
            
        Returns:
            str: Texte du rapport au format Markdown
        """
        # Calculer les statistiques
        total_part = df["SOMME_PART"].sum()
        total_pro = df["SOMME_PRO"].sum()
        total_occ_part = df["OCC_PART"].sum()
        total_occ_pro = df["OCC_PRO"].sum()
        
        avg_part = total_part / total_occ_part if total_occ_part > 0 else 0
        avg_pro = total_pro / total_occ_pro if total_occ_pro > 0 else 0
        
        # Tendances
        trend_part = "en hausse" if df["SOMME_PART"].iloc[-1] > df["SOMME_PART"].iloc[0] else "en baisse"
        trend_pro = "en hausse" if df["SOMME_PRO"].iloc[-1] > df["SOMME_PRO"].iloc[0] else "en baisse"
        
        # Générer le rapport
        report = f"# Rapport d'analyse - {bank_name}\n\n"
        report += f"Date: {datetime.now().strftime('%d/%m/%Y')}\n\n"
        report += f"## Résumé\n\n"
        report += f"Ce rapport présente l'analyse des données de {bank_name} sur une période de {len(df)} semaines.\n\n"
        
        report += f"## Statistiques globales\n\n"
        report += f"- **Groupe**: {df['group_name'].iloc[0]}\n"
        report += f"- **Montant total (particuliers)**: {total_part:,.2f} €\n"
        report += f"- **Montant total (professionnels)**: {total_pro:,.2f} €\n"
        report += f"- **Nombre d'occurrences (particuliers)**: {total_occ_part}\n"
        report += f"- **Nombre d'occurrences (professionnels)**: {total_occ_pro}\n"
        report += f"- **Montant moyen par occurrence (particuliers)**: {avg_part:,.2f} €\n"
        report += f"- **Montant moyen par occurrence (professionnels)**: {avg_pro:,.2f} €\n\n"
        
        report += f"## Tendances\n\n"
        report += f"- Les montants pour les particuliers sont {trend_part} sur la période étudiée.\n"
        report += f"- Les montants pour les professionnels sont {trend_pro} sur la période étudiée.\n\n"
        
        # Ajouter les références aux visualisations
        if visualizations:
            report += f"## Visualisations\n\n"
            for i, viz in enumerate(visualizations):
                report += f"### {viz['title']}\n\n"
                report += f"{viz['description']}\n\n"
                report += f"![{viz['title']}]({viz['path']})\n\n"
        
        return report

# Instance singleton du service
ai_service = AIAnalysisService() 
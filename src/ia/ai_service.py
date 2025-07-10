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
        Préparer le prompt pour l'IA en extrayant les statistiques des données, au format mail de compte rendu d'analyse.
        """
        total_montant = df["montant"].sum() if not df.empty else 0
        total_transactions = df["nombre_transactions"].sum() if not df.empty else 0
        moyenne_montant = df["montant"].mean() if not df.empty else 0
        subject = "Compte rendu hebdomadaire – Semaine en cours"
        prompt = f"""Objet : {subject}

Bonjour,

Veuillez trouver ci-dessous le compte rendu détaillé de l'activité pour la semaine analysée.

---

**Synthèse des résultats :**
- Montant total : {total_montant:,.2f} €
- Transactions totales : {total_transactions}
- Montant moyen par transaction : {moyenne_montant:,.2f} €
- Évolution sur la semaine : ...

**Détail par agence :**
Agence : ...
- Montant total : ...
- Transactions totales : ...
- Montant moyen par transaction : ...
...

---

**Analyse et recommandations :**
- [À compléter par l'IA ou l'analyste]

---

Cordialement,
La Direction

*Ce mail est généré automatiquement à partir des données consolidées de la période. Pour toute question, contactez le service reporting.*
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

    def generer_rapport_hebdomadaire(self, transactions_data: List[Dict], agence: str = None, periode_debut=None, periode_fin=None) -> str:
        """
        Génère un rapport hebdomadaire en HTML à partir des données de transactions.
        
        Args:
            transactions_data: Liste des transactions
            agence: Nom de l'agence (optionnel)
            periode_debut: Date de début de la période
            periode_fin: Date de fin de la période
        
        Returns:
            str: Rapport HTML formaté
        """
        try:
            # Analyser les données
            analyse = self.analyze_bank_data(transactions_data)
            
            # Générer le contenu du rapport
            if self.use_fallback_mode:
                # Mode de secours avec analyse statistique basique
                rapport_contenu = self._generer_rapport_fallback(
                    transactions_data, analyse, agence, periode_debut, periode_fin
                )
            else:
                # Mode avec IA
                rapport_contenu = self._generer_rapport_ia(
                    transactions_data, analyse, agence, periode_debut, periode_fin
                )
            
            # Générer le HTML final
            html_rapport = self._formater_rapport_html(rapport_contenu, agence, periode_debut, periode_fin)
            
            return html_rapport
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
            return self._generer_rapport_erreur(str(e))

    def _generer_rapport_fallback(self, transactions_data: List[Dict], analyse: Dict, agence: str, periode_debut, periode_fin) -> Dict:
        """Génère un rapport en mode de secours (sans IA)."""
        
        # Calculs statistiques
        total_transactions = len(transactions_data)
        montant_total = sum(t['montant'] for t in transactions_data)
        montant_moyen = montant_total / total_transactions if total_transactions > 0 else 0
        
        # Analyse par type de transaction
        types_transactions = {}
        for transaction in transactions_data:
            type_t = transaction.get('type_transaction', 'Non spécifié')
            if type_t not in types_transactions:
                types_transactions[type_t] = {'count': 0, 'montant': 0}
            types_transactions[type_t]['count'] += 1
            types_transactions[type_t]['montant'] += transaction['montant']
        
        # Tendances simples
        if len(transactions_data) >= 7:
            # Comparer première et dernière semaine
            premiers_3_jours = transactions_data[:3] if len(transactions_data) >= 3 else transactions_data
            derniers_3_jours = transactions_data[-3:] if len(transactions_data) >= 3 else transactions_data
            
            montant_debut = sum(t['montant'] for t in premiers_3_jours)
            montant_fin = sum(t['montant'] for t in derniers_3_jours)
            
            if montant_debut > 0:
                evolution = ((montant_fin - montant_debut) / montant_debut) * 100
            else:
                evolution = 0
        else:
            evolution = 0
        
        return {
            'resume_executif': f"Analyse automatique pour la période du {periode_debut.strftime('%d/%m/%Y') if periode_debut else 'N/A'} au {periode_fin.strftime('%d/%m/%Y') if periode_fin else 'N/A'}",
            'statistiques_cles': {
                'total_transactions': total_transactions,
                'montant_total': montant_total,
                'montant_moyen': montant_moyen,
                'evolution': evolution
            },
            'analyse_transactions': types_transactions,
            'recommandations': [
                "Surveiller l'évolution des volumes de transactions",
                "Analyser les types de transactions les plus fréquents",
                "Vérifier la conformité des montants moyens"
            ],
            'points_attention': [
                "Analyse automatique sans intelligence artificielle",
                "Recommandations génériques basées sur les statistiques"
            ]
        }

    def _generer_rapport_ia(self, transactions_data: List[Dict], analyse: Dict, agence: str, periode_debut, periode_fin) -> Dict:
        """Génère un rapport avec analyse IA (quand disponible)."""
        
        # Pour l'instant, retourne le rapport de base
        # TODO: Implémenter l'analyse IA quand les LLM seront configurés
        return self._generer_rapport_fallback(transactions_data, analyse, agence, periode_debut, periode_fin)

    def _formater_rapport_html(self, contenu: Dict, agence: str, periode_debut, periode_fin) -> str:
        """Formate le rapport en HTML."""
        
        agence_text = f" - {agence}" if agence else ""
        periode_text = f"du {periode_debut.strftime('%d/%m/%Y')} au {periode_fin.strftime('%d/%m/%Y')}" if periode_debut and periode_fin else "Période non spécifiée"
        
        html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport Hebdomadaire Bancaire{agence_text}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #3498db; }}
        .stat-box {{ display: inline-block; background-color: #ecf0f1; padding: 10px; margin: 5px; border-radius: 5px; }}
        .warning {{ background-color: #fff3cd; border-color: #ffc107; }}
        .recommendation {{ background-color: #d4edda; border-color: #28a745; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Rapport Hebdomadaire Bancaire{agence_text}</h1>
        <p>{periode_text}</p>
    </div>

    <div class="section">
        <h2>📊 Résumé Exécutif</h2>
        <p>{contenu['resume_executif']}</p>
    </div>

    <div class="section">
        <h2>🔢 Statistiques Clés</h2>
        <div class="stat-box">
            <strong>Total Transactions:</strong> {contenu['statistiques_cles']['total_transactions']}
        </div>
        <div class="stat-box">
            <strong>Montant Total:</strong> {contenu['statistiques_cles']['montant_total']:,.2f} €
        </div>
        <div class="stat-box">
            <strong>Montant Moyen:</strong> {contenu['statistiques_cles']['montant_moyen']:,.2f} €
        </div>
        <div class="stat-box">
            <strong>Évolution:</strong> {contenu['statistiques_cles']['evolution']:+.1f}%
        </div>
    </div>

    <div class="section">
        <h2>📈 Analyse des Transactions</h2>
        <table>
            <thead>
                <tr>
                    <th>Type de Transaction</th>
                    <th>Nombre</th>
                    <th>Montant Total</th>
                    <th>Montant Moyen</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for type_t, data in contenu['analyse_transactions'].items():
            montant_moyen_type = data['montant'] / data['count'] if data['count'] > 0 else 0
            html += f"""
                <tr>
                    <td>{type_t}</td>
                    <td>{data['count']}</td>
                    <td>{data['montant']:,.2f} €</td>
                    <td>{montant_moyen_type:,.2f} €</td>
                </tr>
            """
        
        html += """
            </tbody>
        </table>
    </div>

    <div class="section recommendation">
        <h2>💡 Recommandations</h2>
        <ul>
"""
        
        for rec in contenu['recommandations']:
            html += f"            <li>{rec}</li>\n"
        
        html += """
        </ul>
    </div>

    <div class="section warning">
        <h2>⚠️ Points d'Attention</h2>
        <ul>
"""
        
        for point in contenu['points_attention']:
            html += f"            <li>{point}</li>\n"
        
        html += f"""
        </ul>
    </div>

    <div class="section">
        <h2>📅 Informations du Rapport</h2>
        <p><strong>Généré le:</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
        <p><strong>Système:</strong> Plateforme d'Automatisation des Rapports Bancaires</p>
    </div>

</body>
</html>
        """
        
        return html

    def _generer_rapport_erreur(self, erreur: str) -> str:
        """Génère un rapport d'erreur en HTML."""
        
        return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Erreur - Rapport Bancaire</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .error {{ background-color: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="error">
        <h1>❌ Erreur lors de la génération du rapport</h1>
        <p><strong>Détails de l'erreur:</strong> {erreur}</p>
        <p><strong>Généré le:</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
    </div>
</body>
</html>
        """

# Instance singleton du service
ai_service = AIAnalysisService() 
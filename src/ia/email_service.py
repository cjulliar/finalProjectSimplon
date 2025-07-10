#!/usr/bin/env python3
"""
Service d'envoi d'emails pour les rapports d'analyse bancaire.
Ce module permet d'envoyer des emails avec les rapports générés par l'agent IA,
en incluant des pièces jointes comme les visualisations.
"""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
import markdown
from jinja2 import Template

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Charger également depuis smtp_config.env si il existe
try:
    with open('smtp_config.env', 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
except FileNotFoundError:
    pass

# Configuration SMTP
SMTP_SERVER = os.getenv("SMTP_SERVER", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "rapports@banque-auto.com")
EMAIL_SUBJECT_PREFIX = os.getenv("EMAIL_SUBJECT_PREFIX", "[Rapport Bancaire]")
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "").split(",")


class EmailService:
    """Service d'envoi d'emails pour les rapports d'analyse bancaire."""
    
    def __init__(self):
        """Initialiser le service d'emails."""
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.username = SMTP_USERNAME
        self.password = SMTP_PASSWORD
        self.from_email = EMAIL_FROM
        self.default_recipients = EMAIL_RECIPIENTS
        
        # Vérifier la configuration
        self.is_configured = all([self.smtp_server, self.username, self.password])
        if not self.is_configured:
            logger.warning("Service d'emails non configuré. Utilisez les variables d'environnement SMTP_*.")
    
    def send_report_email(self, 
                          report: str, 
                          visualizations: List[Dict[str, str]] = None,
                          metadata: Dict[str, Any] = None,
                          recipients: List[str] = None,
                          subject: str = None) -> Dict[str, Any]:
        """
        Envoyer un email contenant le rapport et les visualisations.
        
        Args:
            report: Contenu du rapport (format Markdown)
            visualizations: Liste des visualisations à inclure
            metadata: Métadonnées du rapport
            recipients: Liste des destinataires
            subject: Sujet de l'email
            
        Returns:
            Dict contenant le statut de l'envoi
        """
        if not self.is_configured:
            return {
                "sent": False,
                "message": "Service d'emails non configuré"
            }
        
        try:
            # Utiliser les destinataires par défaut si non spécifiés
            if not recipients:
                recipients = self.default_recipients
            
            # Utiliser un sujet par défaut si non spécifié
            if not subject:
                date_str = datetime.now().strftime("%d/%m/%Y")
                subject = f"{EMAIL_SUBJECT_PREFIX} Analyse du {date_str}"
            
            # Créer l'email
            msg = MIMEMultipart("related")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = ", ".join(recipients)
            
            # Partie HTML
            html_content = self._format_html_email(report, visualizations, metadata)
            html_part = MIMEMultipart("alternative")
            html_part.attach(MIMEText(html_content, "html"))
            msg.attach(html_part)
            
            # Ajouter les visualisations comme pièces jointes
            if visualizations:
                for i, viz in enumerate(visualizations):
                    if "path" in viz and Path(viz["path"]).exists():
                        with open(viz["path"], "rb") as f:
                            img = MIMEImage(f.read())
                            img.add_header("Content-Disposition", f"attachment; filename={Path(viz['path']).name}")
                            img.add_header("Content-ID", f"<image{i}>")
                            msg.attach(img)
            
            # Envoyer l'email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email envoyé à {len(recipients)} destinataires")
            return {
                "sent": True,
                "recipients": recipients,
                "subject": subject
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email: {e}")
            return {
                "sent": False,
                "message": str(e)
            }
    
    def _format_html_email(self, 
                          report: str, 
                          visualizations: List[Dict[str, str]] = None,
                          metadata: Dict[str, Any] = None) -> str:
        """
        Formater le contenu HTML de l'email.
        
        Args:
            report: Contenu du rapport (format Markdown ou HTML)
            visualizations: Liste des visualisations à inclure
            metadata: Métadonnées du rapport
            
        Returns:
            Contenu HTML formaté
        """
        # Détecter si le contenu est déjà du HTML complet ou du Markdown
        if report.strip().startswith('<html') and report.strip().endswith('</html>'):
            # C'est déjà du HTML complet, on l'utilise directement
            return report
        elif '<div' in report or '<h1>' in report:
            # C'est du HTML partiel, on l'utilise directement
            report_html = report
        else:
            # C'est du markdown, on le convertit
            report_html = markdown.markdown(report)
        
        # Template HTML pour l'email (uniquement pour markdown ou HTML partiel)
        template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                }
                h1 {
                    color: #0066cc;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 10px;
                }
                h2 {
                    color: #0066cc;
                    margin-top: 20px;
                }
                h3 {
                    color: #0066cc;
                }
                img {
                    max-width: 100%;
                    height: auto;
                    margin: 20px 0;
                    border: 1px solid #ddd;
                }
                .footer {
                    margin-top: 30px;
                    padding-top: 10px;
                    border-top: 1px solid #ddd;
                    font-size: 0.8em;
                    color: #666;
                }
                .metadata {
                    background-color: #f8f8f8;
                    padding: 10px;
                    border-radius: 5px;
                    margin-top: 20px;
                    font-size: 0.8em;
                }
                .visualization {
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <h1>Rapport d'Analyse Bancaire</h1>
            
            <div class="report">
                {{ report_html }}
            </div>
            
            {% if visualizations %}
            <h2>Visualisations</h2>
            <div class="visualizations">
                {% for viz in visualizations %}
                <div class="visualization">
                    <h3>{{ viz.title }}</h3>
                    <img src="cid:image{{ loop.index0 }}" alt="{{ viz.title }}">
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if metadata %}
            <div class="metadata">
                <p><strong>Généré le:</strong> {{ metadata.timestamp }}</p>
                <p><strong>Points de données:</strong> {{ metadata.data_points }}</p>
                <p><strong>Période:</strong> {{ metadata.date_range.start }} à {{ metadata.date_range.end }}</p>
                <p><strong>Agences analysées:</strong> {{ metadata.agencies|join(", ") }}</p>
                <p><strong>Modèle utilisé:</strong> {{ metadata.model_used }}</p>
            </div>
            {% endif %}
            
            <div class="footer">
                <p>Ce rapport a été généré automatiquement par le Système d'Automatisation des Rapports Bancaires.</p>
                <p>Merci de ne pas répondre directement à cet email.</p>
            </div>
        </body>
        </html>
        """)
        
        # Rendre le template
        html_content = template.render(
            report_html=report_html,
            visualizations=visualizations,
            metadata=metadata
        )
        
        return html_content
    
    def schedule_report(self, 
                       schedule_type: str = "weekly", 
                       day: int = 1,  # 0 = Lundi, 6 = Dimanche pour weekly, jour du mois pour monthly
                       recipients: List[str] = None) -> Dict[str, Any]:
        """
        Planifier l'envoi automatique de rapports.
        
        Args:
            schedule_type: Type de planification ('daily', 'weekly', 'monthly')
            day: Jour d'envoi (dépend du type de planification)
            recipients: Liste des destinataires
            
        Returns:
            Dict contenant le statut de la planification
        """
        # Cette fonction est un placeholder, à implémenter avec un système de planification comme celery
        return {
            "scheduled": False,
            "message": "Fonctionnalité de planification non implémentée"
        }


# Instance singleton du service d'emails
email_service = EmailService() 
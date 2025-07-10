#!/usr/bin/env python3
"""
Tâches Celery pour la génération et l'envoi automatique de rapports bancaires.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from celery import shared_task
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def generate_weekly_report(self, agence: str = None, start_date: str = None, end_date: str = None) -> Dict:
    """
    Génère un rapport hebdomadaire pour une agence spécifique.
    
    Args:
        agence: Nom de l'agence (optionnel, génère pour toutes si None)
        start_date: Date de début au format YYYY-MM-DD
        end_date: Date de fin au format YYYY-MM-DD
    
    Returns:
        Dict avec le statut et le chemin du rapport généré
    """
    try:
        logger.info(f"🚀 Début génération rapport hebdomadaire pour agence: {agence}")
        
        # Importer les modules nécessaires
        from src.ia.ai_service import AIAnalysisService
        from src.db.database import SessionLocal
        from src.db.models import BankData
        from datetime import datetime, timedelta
        
        # Définir les dates par défaut (semaine dernière)
        if not start_date:
            end_date_obj = datetime.now()
            start_date_obj = end_date_obj - timedelta(days=7)
        else:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') if end_date else start_date_obj + timedelta(days=7)
        
        # Connexion à la base de données
        with SessionLocal() as session:
            # Construire la requête
            query = session.query(BankData).filter(
                BankData.date >= start_date_obj,
                BankData.date <= end_date_obj
            )
            
            # Filtrer par agence si spécifiée
            if agence:
                query = query.filter(BankData.agence == agence)
            
            # Récupérer les données
            data = query.all()
            
            if not data:
                logger.warning(f"⚠️ Aucune donnée trouvée pour la période {start_date_obj} - {end_date_obj}")
                return {
                    'status': 'warning',
                    'message': 'Aucune donnée trouvée pour la période spécifiée',
                    'agence': agence,
                    'period': f"{start_date_obj.strftime('%Y-%m-%d')} - {end_date_obj.strftime('%Y-%m-%d')}"
                }
            
            logger.info(f"📊 {len(data)} enregistrements trouvés")
            
            # Préparer les données pour l'analyse IA
            transactions_data = []
            for item in data:
                transactions_data.append({
                    'date': item.date.strftime('%Y-%m-%d'),
                    'montant': float(item.montant),
                    'nombre_transactions': item.nombre_transactions,
                    'agence': item.agence
                })
            
            # Générer le rapport avec l'IA
            logger.info("🤖 Génération du rapport avec l'IA...")
            ai_service = AIAnalysisService()
            report_html = ai_service.generer_rapport_hebdomadaire(
                transactions_data=transactions_data,
                agence=agence,
                periode_debut=start_date_obj,
                periode_fin=end_date_obj
            )
            
            # Sauvegarder le rapport
            output_dir = os.path.join(os.getcwd(), "output", "reports")
            os.makedirs(output_dir, exist_ok=True)
            
            report_filename = f"rapport_{agence}_{start_date_obj.strftime('%Y%m%d')}_{end_date_obj.strftime('%Y%m%d')}.html"
            report_path = os.path.join(output_dir, report_filename)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_html)
            
            logger.info(f"📄 Rapport sauvegardé: {report_path}")
            
            return {
                'status': 'success',
                'message': f'Rapport généré avec succès pour {agence}',
                'agence': agence,
                'period': f"{start_date_obj.strftime('%Y-%m-%d')} - {end_date_obj.strftime('%Y-%m-%d')}",
                'report_path': report_path,
                'data_count': len(data)
            }
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de la génération du rapport: {str(e)}")
        
        # Relancer la tâche si on n'a pas atteint le maximum de tentatives
        if self.request.retries < self.max_retries:
            logger.info(f"🔄 Nouvelle tentative ({self.request.retries + 1}/{self.max_retries}) dans 60 secondes...")
            raise self.retry(countdown=60)
        
        return {
            'status': 'error',
            'message': f'Erreur lors de la génération du rapport: {str(e)}',
            'agence': agence
        }

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 30})
def send_report_email(self, filepath: str, recipients: List[str], agence: str = None, subject: str = None) -> Dict:
    """
    Envoie un rapport par email.
    
    Args:
        filepath: Chemin vers le fichier rapport
        recipients: Liste des adresses email destinataires
        agence: Nom de l'agence (pour personnaliser l'email)
        subject: Sujet personnalisé (optionnel)
    
    Returns:
        Dict avec le statut de l'envoi
    """
    try:
        logger.info(f"📧 Envoi du rapport par email: {filepath}")
        
        # Pour l'instant, simuler l'envoi (le service d'email sera créé dans la prochaine étape)
        logger.info(f"📧 Simulation envoi email pour {len(recipients)} destinataires")
        
        # Vérifier que le fichier existe
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Le fichier rapport n'existe pas: {filepath}")
        
        # Préparer le sujet par défaut
        if not subject:
            agence_text = f" - {agence}" if agence else ""
            today = datetime.now().strftime('%d/%m/%Y')
            subject = f"Rapport Hebdomadaire Bancaire{agence_text} - {today}"
        
        # Simuler l'envoi réussi (sera remplacé par le vrai service d'email)
        logger.info(f"✅ Simulation: Email envoyé avec succès à {len(recipients)} destinataires")
        
        return {
            'status': 'success',
            'message': f'Rapport envoyé avec succès à {len(recipients)} destinataires (simulé)',
            'recipients_count': len(recipients),
            'failed_count': 0,
            'subject': subject
        }
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'envoi du rapport: {str(e)}")
        
        # Relancer la tâche si on n'a pas atteint le maximum de tentatives
        if self.request.retries < self.max_retries:
            logger.info(f"🔄 Nouvelle tentative d'envoi ({self.request.retries + 1}/{self.max_retries}) dans 30 secondes...")
            raise self.retry(countdown=30)
        
        return {
            'status': 'error',
            'message': f'Erreur l\'envoi du rapport: {str(e)}'
        }

@shared_task(bind=True)
def generate_and_send_report(
    self, 
    agence: str = None, 
    recipients: List[str] = None, 
    start_date: str = None, 
    end_date: str = None
) -> Dict:
    """
    Tâche combinée: génère un rapport et l'envoie par email.
    
    Args:
        agence: Nom de l'agence
        recipients: Liste des destinataires
        start_date: Date de début au format YYYY-MM-DD
        end_date: Date de fin au format YYYY-MM-DD
    
    Returns:
        Dict avec le statut global de l'opération
    """
    try:
        logger.info(f"🎯 Début génération et envoi de rapport pour agence: {agence}")
        
        # Étape 1: Générer le rapport
        generation_result = generate_weekly_report.apply(
            args=[agence, start_date, end_date]
        ).get()
        
        if generation_result['status'] != 'success':
            return {
                'status': 'error',
                'message': f"Échec de la génération: {generation_result['message']}",
                'generation_result': generation_result
            }
        
        # Étape 2: Envoyer le rapport si des destinataires sont spécifiés
        if recipients:
            filepath = generation_result['report_path']
            email_result = send_report_email.apply(
                args=[filepath, recipients, agence]
            ).get()
            
            return {
                'status': 'success',
                'message': 'Rapport généré et envoyé avec succès',
                'generation_result': generation_result,
                'email_result': email_result
            }
        else:
            return {
                'status': 'success',
                'message': 'Rapport généré avec succès (aucun destinataire spécifié)',
                'generation_result': generation_result
            }
            
    except Exception as e:
        logger.error(f"❌ Erreur dans la tâche combinée: {str(e)}")
        return {
            'status': 'error',
            'message': f'Erreur dans la tâche combinée: {str(e)}'
        }

@shared_task(bind=True)
def cleanup_old_reports(self, days_to_keep: int = 30) -> Dict:
    """
    Nettoie les anciens rapports pour libérer l'espace disque.
    
    Args:
        days_to_keep: Nombre de jours de rapports à conserver
    
    Returns:
        Dict avec le statut du nettoyage
    """
    try:
        logger.info(f"🧹 Nettoyage des rapports plus anciens que {days_to_keep} jours")
        
        output_dir = Path("/app/output")
        if not output_dir.exists():
            return {
                'status': 'success',
                'message': 'Répertoire de sortie inexistant, rien à nettoyer'
            }
        
        # Calculer la date limite
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Parcourir les fichiers
        deleted_count = 0
        total_size_freed = 0
        
        for file_path in output_dir.glob("rapport_*.html"):
            # Vérifier la date de modification du fichier
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            if file_mtime < cutoff_date:
                file_size = file_path.stat().st_size
                file_path.unlink()  # Supprimer le fichier
                deleted_count += 1
                total_size_freed += file_size
                logger.info(f"🗑️ Fichier supprimé: {file_path.name}")
        
        # Convertir la taille en MB
        size_mb = total_size_freed / (1024 * 1024)
        
        logger.info(f"✅ Nettoyage terminé: {deleted_count} fichiers supprimés, {size_mb:.2f} MB libérés")
        
        return {
            'status': 'success',
            'message': f'{deleted_count} fichiers supprimés, {size_mb:.2f} MB libérés',
            'deleted_count': deleted_count,
            'size_freed_mb': round(size_mb, 2)
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du nettoyage: {str(e)}")
        return {
            'status': 'error',
            'message': f'Erreur lors du nettoyage: {str(e)}'
        } 
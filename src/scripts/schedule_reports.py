#!/usr/bin/env python3
"""
Script pour planifier l'exécution hebdomadaire des rapports bancaires.
Ce script configure un planificateur qui exécutera automatiquement
l'analyse des données bancaires et l'envoi des rapports par email.
"""
import argparse
import sys
import os
import logging
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import schedule
import time
import subprocess
import sqlite3

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("reports_scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("reports_scheduler")


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description="Planifier l'exécution hebdomadaire des rapports bancaires.")
    parser.add_argument(
        "--day", "-d",
        type=str,
        choices=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
        default="monday",
        help="Jour de la semaine pour l'exécution (par défaut: monday)"
    )
    parser.add_argument(
        "--time", "-t",
        type=str,
        default="08:00",
        help="Heure d'exécution au format HH:MM (par défaut: 08:00)"
    )
    parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["markdown", "html"],
        default="markdown",
        help="Format des rapports (par défaut: markdown)"
    )
    parser.add_argument(
        "--recipients", "-r",
        type=str,
        help="Liste des destinataires des emails, séparés par des virgules"
    )
    parser.add_argument(
        "--subject", "-s",
        type=str,
        default="Rapport hebdomadaire des banques",
        help="Sujet des emails"
    )
    parser.add_argument(
        "--test", "-T",
        action="store_true",
        help="Exécuter immédiatement une fois pour tester"
    )
    return parser.parse_args()


def log_execution(status, message, details=None):
    """
    Enregistrer l'exécution du rapport planifié dans la base de données.
    
    Args:
        status (str): Statut de l'exécution ('success', 'error', 'warning')
        message (str): Message décrivant l'exécution
        details (dict, optional): Détails supplémentaires à enregistrer
    
    Returns:
        bool: True si l'enregistrement a réussi, False sinon
    """
    try:
        # Chemin vers la base de données
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'bankreports.db')
        
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si la table existe, sinon la créer
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS execution_logs (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL,
            message TEXT NOT NULL,
            details TEXT
        )
        """)
        
        # Générer un ID unique
        log_id = str(uuid.uuid4())
        
        # Préparer les détails en JSON
        details_json = json.dumps(details) if details else None
        
        # Insérer l'enregistrement
        cursor.execute(
            "INSERT INTO execution_logs (id, timestamp, status, message, details) VALUES (?, ?, ?, ?, ?)",
            (log_id, datetime.now().isoformat(), status, message, details_json)
        )
        
        # Valider la transaction
        conn.commit()
        
        # Fermer la connexion
        conn.close()
        
        logger.info(f"Exécution enregistrée avec l'ID: {log_id}")
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de l'exécution: {str(e)}")
        return False


def run_import():
    """Exécuter l'importation des données bancaires."""
    logger.info("Démarrage de l'importation des données bancaires...")
    
    try:
        result = subprocess.run(
            ["python", "src/scripts/import_bank_dataset.py", "--filter-banks"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Importation terminée avec succès: {result.stdout}")
        log_execution("success", "Importation des données bancaires réussie")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de l'importation: {e}")
        logger.error(f"Sortie standard: {e.stdout}")
        logger.error(f"Sortie d'erreur: {e.stderr}")
        log_execution("error", "Échec de l'importation des données bancaires", 
                     {"stdout": e.stdout, "stderr": e.stderr})
        return False


def run_individual_reports(format="markdown", email=False, recipients=None, subject=None):
    """Exécuter la génération des rapports individuels."""
    logger.info("Démarrage de la génération des rapports individuels...")
    
    cmd = ["python", "src/scripts/analyze_filtered_banks.py", f"--format={format}"]
    
    if email and recipients:
        cmd.extend(["--email", f"--recipients={recipients}"])
        if subject:
            cmd.append(f"--subject={subject}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Génération des rapports individuels terminée avec succès")
        log_execution("success", "Génération des rapports individuels réussie", 
                     {"format": format, "email": email, "recipients": recipients})
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de la génération des rapports individuels: {e}")
        logger.error(f"Sortie standard: {e.stdout}")
        logger.error(f"Sortie d'erreur: {e.stderr}")
        log_execution("error", "Échec de la génération des rapports individuels", 
                     {"stdout": e.stdout, "stderr": e.stderr, "format": format})
        return False


def run_global_report(format="markdown", email=False, recipients=None, subject=None):
    """Exécuter la génération du rapport global."""
    logger.info("Démarrage de la génération du rapport global...")
    
    cmd = ["python", "src/scripts/generate_global_report.py", f"--format={format}"]
    
    if email and recipients:
        cmd.extend(["--email", f"--recipients={recipients}"])
        if subject:
            cmd.append(f"--subject={subject}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Génération du rapport global terminée avec succès")
        log_execution("success", "Génération du rapport global réussie", 
                     {"format": format, "email": email, "recipients": recipients})
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de la génération du rapport global: {e}")
        logger.error(f"Sortie standard: {e.stdout}")
        logger.error(f"Sortie d'erreur: {e.stderr}")
        log_execution("error", "Échec de la génération du rapport global", 
                     {"stdout": e.stdout, "stderr": e.stderr, "format": format})
        return False


def run_weekly_task(format="markdown", email=False, recipients=None, subject=None):
    """Exécuter la tâche hebdomadaire complète."""
    logger.info("Démarrage de la tâche hebdomadaire...")
    start_time = datetime.now()
    
    # Enregistrer le début de l'exécution
    log_execution("info", "Début de la tâche hebdomadaire", 
                 {"format": format, "email": email, "recipients": recipients})
    
    # Étape 1: Importer les données
    if not run_import():
        logger.error("Échec de l'importation des données, arrêt de la tâche hebdomadaire")
        log_execution("error", "Échec de la tâche hebdomadaire - Importation échouée")
        return False
    
    # Étape 2: Générer les rapports individuels
    if not run_individual_reports(format, email, recipients, subject):
        logger.error("Échec de la génération des rapports individuels")
        log_execution("warning", "Avertissement - Échec des rapports individuels")
        # Continuer malgré l'échec
    
    # Étape 3: Générer le rapport global
    if not run_global_report(format, email, recipients, subject):
        logger.error("Échec de la génération du rapport global")
        log_execution("error", "Échec de la tâche hebdomadaire - Rapport global échoué")
        return False
    
    # Calculer la durée d'exécution
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info(f"Tâche hebdomadaire terminée avec succès en {duration:.2f} secondes")
    log_execution("success", "Tâche hebdomadaire terminée avec succès", 
                 {"duration": duration, "start": start_time.isoformat(), "end": end_time.isoformat()})
    return True


def main():
    """Point d'entrée principal."""
    args = parse_arguments()
    
    # Configurer les paramètres
    day = args.day.lower()
    time_parts = args.time.split(":")
    if len(time_parts) != 2:
        logger.error(f"Format d'heure invalide: {args.time}, utilisation de 08:00")
        hour, minute = 8, 0
    else:
        try:
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                logger.error(f"Heure invalide: {args.time}, utilisation de 08:00")
                hour, minute = 8, 0
        except ValueError:
            logger.error(f"Format d'heure invalide: {args.time}, utilisation de 08:00")
            hour, minute = 8, 0
    
    time_str = f"{hour:02d}:{minute:02d}"
    
    # Configurer l'email
    email = bool(args.recipients)
    recipients = args.recipients
    subject = args.subject
    
    # Si l'option de test est activée, exécuter immédiatement une fois
    if args.test:
        logger.info("Mode test activé, exécution immédiate...")
        run_weekly_task(args.format, email, recipients, subject)
        return 0
    
    # Planifier la tâche hebdomadaire
    logger.info(f"Planification de la tâche hebdomadaire: chaque {day} à {time_str}")
    
    # Configurer la planification avec schedule
    if day == "monday":
        schedule.every().monday.at(time_str).do(
            run_weekly_task, format=args.format, email=email, recipients=recipients, subject=subject
        )
    elif day == "tuesday":
        schedule.every().tuesday.at(time_str).do(
            run_weekly_task, format=args.format, email=email, recipients=recipients, subject=subject
        )
    elif day == "wednesday":
        schedule.every().wednesday.at(time_str).do(
            run_weekly_task, format=args.format, email=email, recipients=recipients, subject=subject
        )
    elif day == "thursday":
        schedule.every().thursday.at(time_str).do(
            run_weekly_task, format=args.format, email=email, recipients=recipients, subject=subject
        )
    elif day == "friday":
        schedule.every().friday.at(time_str).do(
            run_weekly_task, format=args.format, email=email, recipients=recipients, subject=subject
        )
    elif day == "saturday":
        schedule.every().saturday.at(time_str).do(
            run_weekly_task, format=args.format, email=email, recipients=recipients, subject=subject
        )
    elif day == "sunday":
        schedule.every().sunday.at(time_str).do(
            run_weekly_task, format=args.format, email=email, recipients=recipients, subject=subject
        )
    
    # Enregistrer la configuration du planificateur
    log_execution("info", f"Planificateur configuré: {day} à {time_str}", 
                 {"day": day, "time": time_str, "format": args.format, 
                  "email": email, "recipients": recipients})
    
    # Afficher le temps restant jusqu'à la prochaine exécution
    next_run = schedule.next_run()
    if next_run:
        time_until_next = next_run - datetime.now()
        hours, remainder = divmod(time_until_next.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        logger.info(f"Prochaine exécution dans {int(hours)}h {int(minutes)}m {int(seconds)}s")
    
    # Boucle principale
    logger.info("Démarrage du planificateur (Ctrl+C pour arrêter)...")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérifier toutes les minutes
    except KeyboardInterrupt:
        logger.info("Arrêt du planificateur")
        log_execution("info", "Arrêt manuel du planificateur")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
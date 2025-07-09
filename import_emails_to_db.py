#!/usr/bin/env python3
"""
Script pour importer les emails générés par LLM dans la base de données.
Lit tous les fichiers de llm_responses et les insère dans la table email_reports.
"""

import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def get_database_connection():
    """Obtenir une connexion à la base de données."""
    return sqlite3.connect("bankreports.db")

def extract_email_info(content):
    """
    Extraire les informations de l'email depuis le contenu.
    Retourne un tuple (subject, body)
    """
    lines = content.strip().split('\n')
    
    # Chercher l'objet du mail
    subject = ""
    body_start = 0
    
    for i, line in enumerate(lines):
        if line.startswith("Objet") or line.startswith("Objet du mail"):
            subject = line.split(":", 1)[1].strip() if ":" in line else line
            body_start = i + 1
            break
    
    # Si pas d'objet trouvé, utiliser la première ligne
    if not subject and lines:
        subject = lines[0].strip()
        body_start = 1
    
    # Le corps du mail commence après l'objet
    body = '\n'.join(lines[body_start:]).strip()
    
    return subject, body

def insert_email_to_db(conn, bank_name, subject, content, week_id="2025_28"):
    """
    Insérer un email dans la table email_reports.
    """
    try:
        cursor = conn.cursor()
        
        # Générer un ID unique
        email_id = f"email_{bank_name}_{week_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Préparer les données
        data = {
            'id': email_id,
            'user_id': 1,  # Utilisateur par défaut
            'bank_name': bank_name,
            'subject': subject,
            'recipients': json.dumps([f"directeur@{bank_name.lower().replace(' ', '')}.com"]),
            'content': content,
            'sent_at': datetime.now().isoformat(),
            'scheduled_report_id': f"report_{bank_name}_{week_id}",
            'status': 'generated'
        }
        
        # Insérer dans la base
        cursor.execute("""
            INSERT INTO email_reports 
            (id, user_id, bank_name, subject, recipients, content, sent_at, scheduled_report_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['id'], data['user_id'], data['bank_name'], data['subject'],
            data['recipients'], data['content'], data['sent_at'],
            data['scheduled_report_id'], data['status']
        ))
        
        conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'insertion de l'email pour {bank_name}: {str(e)}")
        return False

def import_emails_to_database():
    """Importer tous les emails générés dans la base de données."""
    
    responses_dir = Path("prompts_analysis/llm_responses")
    
    if not responses_dir.exists():
        logger.error(f"Le dossier {responses_dir} n'existe pas")
        return
    
    # Lister tous les fichiers de réponses
    response_files = list(responses_dir.glob("mail_*_semaine_2025_28.txt"))
    logger.info(f"Trouvé {len(response_files)} fichiers d'emails à importer")
    
    conn = get_database_connection()
    imported_count = 0
    error_count = 0
    
    try:
        for file_path in response_files:
            try:
                # Extraire le nom de la banque du nom de fichier
                filename = file_path.stem  # mail_Banque_A_semaine_2025_28
                bank_name = filename.replace("mail_", "").replace("_semaine_2025_28", "")
                
                # Lire le contenu du fichier
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                # Vérifier que le fichier n'est pas vide
                if not content:
                    logger.warning(f"  ⚠️  Fichier vide: {file_path.name}")
                    continue
                
                # Extraire l'objet et le corps de l'email
                subject, body = extract_email_info(content)
                
                # Insérer en base
                if insert_email_to_db(conn, bank_name, subject, body):
                    imported_count += 1
                    logger.info(f"  ✅ Email importé: {bank_name}")
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                logger.error(f"  ❌ Erreur lors du traitement de {file_path.name}: {str(e)}")
    
    finally:
        conn.close()
    
    logger.info(f"\n=== RÉSUMÉ DE L'IMPORT ===")
    logger.info(f"Emails importés avec succès: {imported_count}")
    logger.info(f"Erreurs: {error_count}")
    logger.info(f"Total fichiers traités: {len(response_files)}")
    
    if imported_count > 0:
        logger.info(f"\n🎯 PROCHAINES ÉTAPES:")
        logger.info(f"1. Les emails sont maintenant en base dans la table 'email_reports'")
        logger.info(f"2. Ils peuvent être affichés dans le front-end")
        logger.info(f"3. Ils peuvent être envoyés automatiquement si nécessaire")

if __name__ == "__main__":
    import_emails_to_database() 
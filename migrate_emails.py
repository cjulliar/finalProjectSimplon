#!/usr/bin/env python3
"""
Script pour migrer les emails en gérant les différences de structure
"""

import sqlite3
import json
from datetime import datetime

def migrate_emails():
    """Migre les emails de l'ancienne base vers la nouvelle"""
    
    print("📧 MIGRATION DES EMAILS")
    print("=" * 30)
    
    # Connexion aux bases
    old_conn = sqlite3.connect("bankreports_backup.db")
    new_conn = sqlite3.connect("bankreports.db")
    
    old_cursor = old_conn.cursor()
    new_cursor = new_conn.cursor()
    
    try:
        # Récupérer les emails de l'ancienne base
        old_cursor.execute("SELECT * FROM email_reports")
        emails = old_cursor.fetchall()
        
        if not emails:
            print("ℹ️  Aucun email à migrer")
            return
        
        print(f"📋 {len(emails)} emails trouvés dans l'ancienne base")
        
        # Vider la table email_reports de la nouvelle base
        new_cursor.execute("DELETE FROM email_reports")
        
        # Récupérer la structure de l'ancienne table
        old_cursor.execute("PRAGMA table_info(email_reports)")
        old_columns = [col[1] for col in old_cursor.fetchall()]
        
        # Récupérer la structure de la nouvelle table
        new_cursor.execute("PRAGMA table_info(email_reports)")
        new_columns = [col[1] for col in new_cursor.fetchall()]
        
        print(f"📊 Colonnes ancienne table: {old_columns}")
        print(f"📊 Colonnes nouvelle table: {new_columns}")
        
        # Migrer chaque email
        for i, email in enumerate(emails, 1):
            print(f"\n📧 Migration email {i}/{len(emails)}")
            
            # Créer un dictionnaire avec les données
            email_dict = dict(zip(old_columns, email))
            
            # Adapter les données pour la nouvelle structure
            new_data = {
                'id': i,  # Nouveau ID auto-incrémenté
                'user_id': email_dict.get('user_id', 1),
                'bank_name': email_dict.get('bank_name', 'Banque inconnue'),
                'subject': email_dict.get('subject', 'Rapport bancaire'),
                'recipients': email_dict.get('recipients', '[]'),  # JSON string
                'content': email_dict.get('content', ''),
                'sent_at': email_dict.get('sent_at', datetime.now().isoformat()),
                'scheduled_report_id': email_dict.get('scheduled_report_id', None),
                'status': email_dict.get('status', 'sent')
            }
            
            # Convertir recipients en string si c'est un JSON
            if isinstance(new_data['recipients'], str):
                try:
                    # Vérifier si c'est déjà un JSON valide
                    json.loads(new_data['recipients'])
                except:
                    # Si ce n'est pas un JSON valide, le convertir
                    new_data['recipients'] = json.dumps([new_data['recipients']])
            
            # Insérer dans la nouvelle base
            insert_sql = """
                INSERT INTO email_reports 
                (id, user_id, bank_name, subject, recipients, content, sent_at, scheduled_report_id, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            new_cursor.execute(insert_sql, (
                new_data['id'],
                new_data['user_id'],
                new_data['bank_name'],
                new_data['subject'],
                new_data['recipients'],
                new_data['content'],
                new_data['sent_at'],
                new_data['scheduled_report_id'],
                new_data['status']
            ))
            
            print(f"   ✅ Email migré: {new_data['subject']}")
        
        # Valider les changements
        new_conn.commit()
        
        # Vérifier le résultat
        new_cursor.execute("SELECT COUNT(*) FROM email_reports")
        count = new_cursor.fetchone()[0]
        print(f"\n🎉 Migration terminée: {count} emails dans la nouvelle base")
        
        # Afficher un exemple
        new_cursor.execute("SELECT id, bank_name, subject, sent_at FROM email_reports LIMIT 1")
        example = new_cursor.fetchone()
        if example:
            print(f"📋 Exemple d'email migré:")
            print(f"   ID: {example[0]}")
            print(f"   Banque: {example[1]}")
            print(f"   Sujet: {example[2]}")
            print(f"   Date: {example[3]}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False
    finally:
        old_conn.close()
        new_conn.close()
    
    return True

if __name__ == "__main__":
    migrate_emails() 
#!/usr/bin/env python3
"""
Importe tous les emails générés par LLM dans la table email_reports de la base consolidée.
"""
import os
import sqlite3
from datetime import datetime
import re
import json

DB_PATH = "bankreports.db"
LLM_DIR = "prompts_analysis/llm_responses"

# Générer un destinataire fictif à partir du nom de la banque
def get_recipient(bank_name):
    return f"directeur@{bank_name.lower().replace(' ', '').replace('_', '')}.com"

def parse_email_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if not lines:
        return None
    # Sujet
    subject_line = lines[0].strip()
    subject = subject_line.replace('Objet du mail :', '').strip()
    # Corps
    content = ''.join(lines[2:]).strip()  # Sauter la ligne vide après l'objet
    return subject, content

def main():
    print(f"📥 Import des emails générés depuis {LLM_DIR} vers {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    files = [f for f in os.listdir(LLM_DIR) if f.endswith('.txt')]
    print(f"   {len(files)} fichiers trouvés.")
    count = 0
    for filename in files:
        filepath = os.path.join(LLM_DIR, filename)
        match = re.match(r"mail_Banque_([A-Z_]+)_semaine_([0-9_]+)\.txt", filename)
        if not match:
            print(f"   ⚠️  Fichier ignoré (nom inattendu): {filename}")
            continue
        bank_name = match.group(1).replace('_', ' ')
        week_id = match.group(2)
        subject, content = parse_email_file(filepath)
        if not subject or not content:
            print(f"   ⚠️  Email vide ou mal formaté: {filename}")
            continue
        recipients = json.dumps([get_recipient(bank_name)])
        sent_at = datetime.now().isoformat()
        status = 'generated'
        user_id = 1  # Par défaut
        scheduled_report_id = None
        # Insérer dans la BDD sans l'id (auto-incrément)
        cursor.execute("""
            INSERT INTO email_reports
            (user_id, bank_name, subject, recipients, content, sent_at, scheduled_report_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            bank_name,
            subject,
            recipients,
            content,
            sent_at,
            scheduled_report_id,
            status
        ))
        count += 1
        print(f"   ✅ Email importé: {subject} ({bank_name})")
    conn.commit()
    print(f"\n🎉 {count} emails importés dans la base {DB_PATH}")
    conn.close()

if __name__ == "__main__":
    main() 
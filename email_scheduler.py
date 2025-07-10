#!/usr/bin/env python3
"""
Planificateur automatique d'envoi d'emails bancaires.
À exécuter via cron pour envoi hebdomadaire.
"""
import sys
import os
from datetime import datetime

# Ajouter le répertoire du projet au path
sys.path.append('/Users/cyriljulliard/simplon/finalProjectSimplon')

def main():
    """Fonction principale du planificateur."""
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Démarrage envoi planifié")
    
    try:
        from deploy_full_email_system import send_to_all_banks
        
        success, total = send_to_all_banks()
        
        print(f"✅ Envoi planifié terminé: {success}/{total} emails")
        
        # Log du résultat
        with open('/Users/cyriljulliard/simplon/finalProjectSimplon/email_logs.txt', 'a') as f:
            f.write(f"{datetime.now()}: {success}/{total} emails envoyés\n")
        
    except Exception as e:
        print(f"❌ Erreur planificateur: {e}")
        
        # Log de l'erreur
        with open('/Users/cyriljulliard/simplon/finalProjectSimplon/email_logs.txt', 'a') as f:
            f.write(f"{datetime.now()}: ERREUR - {e}\n")

if __name__ == "__main__":
    main()

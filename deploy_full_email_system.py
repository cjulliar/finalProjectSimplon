#!/usr/bin/env python3
"""
Déploiement complet du système d'emails bancaires enrichis.
Envoi à toutes les 74 banques + planification automatique.
"""
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta
import time

def get_all_bank_agencies():
    """Récupérer toutes les agences bancaires."""
    conn = sqlite3.connect("bankreports.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT agence 
        FROM bank_data_enriched 
        WHERE agence IS NOT NULL 
        ORDER BY agence
    """)
    
    agencies = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return agencies

def send_to_all_banks():
    """Envoyer des emails à toutes les banques."""
    print("🚀 DÉPLOIEMENT COMPLET - TOUTES LES BANQUES")
    print("=" * 60)
    
    agencies = get_all_bank_agencies()
    
    print(f"📊 {len(agencies)} banques détectées")
    print(f"📧 Envoi à toutes vos adresses Gmail+")
    
    # Importer et utiliser le système d'envoi
    try:
        from send_enriched_bank_report import send_reports_to_multiple_banks
        
        print(f"\n⏳ Début envoi massif...")
        results = send_reports_to_multiple_banks(agencies)
        
        success_count = len([r for r in results if "✅" in r["status"]])
        
        print(f"\n🎯 RÉSULTAT FINAL:")
        print(f"   📧 Emails envoyés: {success_count}/{len(agencies)}")
        print(f"   📈 Taux de réussite: {success_count/len(agencies)*100:.1f}%")
        print(f"   📬 Vérifiez votre Gmail: cyrjulliard@gmail.com")
        
        return success_count, len(agencies)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 0, len(agencies)

def create_scheduler_script():
    """Créer un script de planification automatique."""
    scheduler_code = '''#!/usr/bin/env python3
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
            f.write(f"{datetime.now()}: {success}/{total} emails envoyés\\n")
        
    except Exception as e:
        print(f"❌ Erreur planificateur: {e}")
        
        # Log de l'erreur
        with open('/Users/cyriljulliard/simplon/finalProjectSimplon/email_logs.txt', 'a') as f:
            f.write(f"{datetime.now()}: ERREUR - {e}\\n")

if __name__ == "__main__":
    main()
'''
    
    with open('email_scheduler.py', 'w') as f:
        f.write(scheduler_code)
    
    print("📅 Script planificateur créé: email_scheduler.py")

def create_cron_instructions():
    """Créer les instructions pour configurer cron."""
    cron_content = f"""
# CONFIGURATION CRON POUR EMAILS BANCAIRES AUTOMATIQUES
# =====================================================

# 1. Ouvrir crontab
# crontab -e

# 2. Ajouter cette ligne pour envoi tous les lundis à 9h00 :
0 9 * * 1 cd /Users/cyriljulliard/simplon/finalProjectSimplon && /Users/cyriljulliard/simplon/finalProjectSimplon/venv/bin/python email_scheduler.py >> email_cron.log 2>&1

# 3. Sauvegarder et quitter

# AUTRES FRÉQUENCES POSSIBLES :
# Tous les jours à 8h30 :     30 8 * * * 
# Tous les vendredis à 17h :  0 17 * * 5
# Le 1er de chaque mois :     0 9 1 * *

# VÉRIFIER LES LOGS :
# tail -f /Users/cyriljulliard/simplon/finalProjectSimplon/email_cron.log
# tail -f /Users/cyriljulliard/simplon/finalProjectSimplon/email_logs.txt

# TESTER MANUELLEMENT :
# cd /Users/cyriljulliard/simplon/finalProjectSimplon
# python email_scheduler.py
"""
    
    with open('cron_setup_instructions.txt', 'w') as f:
        f.write(cron_content)
    
    print("📋 Instructions cron créées: cron_setup_instructions.txt")

def create_admin_dashboard():
    """Créer un tableau de bord admin simple."""
    dashboard_code = '''#!/usr/bin/env python3
"""
Tableau de bord administrateur pour le système d'emails bancaires.
"""
import sqlite3
from datetime import datetime, timedelta
import os

def show_email_stats():
    """Afficher les statistiques d'envoi."""
    print("📊 TABLEAU DE BORD EMAILS BANCAIRES")
    print("=" * 50)
    
    # Statistiques base de données
    conn = sqlite3.connect("bankreports.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(DISTINCT agence) FROM bank_data_enriched")
    total_banks = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE email LIKE '%directeur%'")
    total_directors = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM bank_data_enriched")
    total_records = cursor.fetchone()[0]
    
    print(f"🏦 Banques configurées: {total_banks}")
    print(f"👤 Directeurs créés: {total_directors}")
    print(f"📊 Enregistrements données: {total_records:,}")
    
    # Logs d'envoi récents
    if os.path.exists('email_logs.txt'):
        print(f"\\n📧 LOGS D'ENVOI RÉCENTS:")
        print("-" * 30)
        with open('email_logs.txt', 'r') as f:
            lines = f.readlines()
            for line in lines[-5:]:  # 5 dernières lignes
                print(f"   {line.strip()}")
    else:
        print(f"\\n📧 Aucun log d'envoi trouvé")
    
    # Test de configuration
    print(f"\\n🔧 TESTS DE CONFIGURATION:")
    print("-" * 30)
    
    # Test SMTP
    if os.path.exists('smtp_config.env'):
        print("   ✅ Configuration SMTP: OK")
    else:
        print("   ❌ Configuration SMTP: MANQUANTE")
    
    # Test base de données
    try:
        cursor.execute("SELECT 1 FROM bank_data_enriched LIMIT 1")
        print("   ✅ Base de données: OK")
    except:
        print("   ❌ Base de données: ERREUR")
    
    conn.close()

def manual_send_test():
    """Envoyer un test manuel."""
    print(f"\\n🧪 TEST ENVOI MANUEL")
    print("-" * 30)
    
    try:
        from send_enriched_bank_report import send_reports_to_multiple_banks
        
        test_banks = ["Banque A"]
        results = send_reports_to_multiple_banks(test_banks)
        
        if results and "✅" in results[0]["status"]:
            print("   ✅ Test réussi !")
        else:
            print("   ❌ Test échoué")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def main():
    """Menu principal."""
    while True:
        print(f"\\n" + "="*50)
        print("🎛️  ADMIN DASHBOARD - EMAILS BANCAIRES")
        print("="*50)
        print("1. 📊 Voir statistiques")
        print("2. 🧪 Test envoi manuel")
        print("3. 🚀 Envoyer à toutes les banques")
        print("4. 📋 Voir logs")
        print("5. ❌ Quitter")
        
        choice = input("\\nChoix: ").strip()
        
        if choice == "1":
            show_email_stats()
        elif choice == "2":
            manual_send_test()
        elif choice == "3":
            from deploy_full_email_system import send_to_all_banks
            send_to_all_banks()
        elif choice == "4":
            if os.path.exists('email_logs.txt'):
                with open('email_logs.txt', 'r') as f:
                    print(f.read())
            else:
                print("Aucun log trouvé")
        elif choice == "5":
            print("👋 Au revoir !")
            break
        else:
            print("❌ Choix invalide")

if __name__ == "__main__":
    main()
'''
    
    with open('admin_dashboard.py', 'w') as f:
        f.write(dashboard_code)
    
    print("🎛️ Dashboard admin créé: admin_dashboard.py")

def main():
    """Fonction principale."""
    print("🚀 DÉPLOIEMENT SYSTÈME COMPLET D'EMAILS BANCAIRES")
    print("=" * 60)
    
    agencies = get_all_bank_agencies()
    
    print(f"📊 Configuration détectée:")
    print(f"   🏦 {len(agencies)} banques")
    print(f"   📧 Emails Gmail+ configurés")
    print(f"   🎯 Prompts IA enrichis (29 indicateurs)")
    
    print(f"\n🛠️ Création des outils de gestion...")
    
    # Créer les scripts de gestion
    create_scheduler_script()
    create_cron_instructions()
    create_admin_dashboard()
    
    print(f"\n📋 FICHIERS CRÉÉS:")
    print(f"   📅 email_scheduler.py - Planificateur automatique")
    print(f"   📋 cron_setup_instructions.txt - Instructions cron")
    print(f"   🎛️ admin_dashboard.py - Tableau de bord admin")
    
    print(f"\n🎯 PROCHAINES ÉTAPES:")
    print(f"   1. 🧪 Tester: python admin_dashboard.py")
    print(f"   2. 🚀 Envoyer à toutes: option 3 du dashboard")
    print(f"   3. 📅 Planifier: suivre cron_setup_instructions.txt")
    
    # Proposer un test immédiat
    response = input(f"\n❓ Voulez-vous tester le dashboard maintenant ? (o/n): ").lower()
    
    if response == 'o':
        print(f"\n🚀 Lancement du dashboard...")
        subprocess.run([sys.executable, 'admin_dashboard.py'])
    else:
        print(f"\n✅ Déploiement terminé !")
        print(f"   Lancez: python admin_dashboard.py")

if __name__ == "__main__":
    main() 
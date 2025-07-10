#!/usr/bin/env python3
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
        print(f"\n📧 LOGS D'ENVOI RÉCENTS:")
        print("-" * 30)
        with open('email_logs.txt', 'r') as f:
            lines = f.readlines()
            for line in lines[-5:]:  # 5 dernières lignes
                print(f"   {line.strip()}")
    else:
        print(f"\n📧 Aucun log d'envoi trouvé")
    
    # Test de configuration
    print(f"\n🔧 TESTS DE CONFIGURATION:")
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
    print(f"\n🧪 TEST ENVOI MANUEL")
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
        print(f"\n" + "="*50)
        print("🎛️  ADMIN DASHBOARD - EMAILS BANCAIRES")
        print("="*50)
        print("1. 📊 Voir statistiques")
        print("2. 🧪 Test envoi manuel")
        print("3. 🚀 Envoyer à toutes les banques")
        print("4. 📋 Voir logs")
        print("5. ❌ Quitter")
        
        choice = input("\nChoix: ").strip()
        
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

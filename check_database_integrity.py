#!/usr/bin/env python3
"""
Script de monitoring pour vérifier l'intégrité de la base de données
"""

import os
import sys
import django

# Ajouter le répertoire frontend au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'frontend'))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')
django.setup()

from django.contrib.auth.models import User

def check_database_integrity():
    """Vérifie l'intégrité de la base de données"""
    
    print("🔍 VÉRIFICATION DE L'INTÉGRITÉ DE LA BASE DE DONNÉES")
    print("=" * 50)
    
    # 1. Vérifier les bases multiples
    bankreports_dbs = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.db') and 'bankreports' in file:
                full_path = os.path.join(root, file)
                if not full_path.startswith('./old_databases_backup_'):
                    bankreports_dbs.append(full_path)
    
    if len(bankreports_dbs) > 1:
        print("❌ PROBLÈME DÉTECTÉ : Plusieurs bases bankreports.db trouvées")
        for db in bankreports_dbs:
            print(f"   📄 {db}")
        print("   💡 Solution : Exécuter python cleanup_redundant_dbs.py")
        return False
    elif len(bankreports_dbs) == 1:
        print(f"✅ Base unique détectée : {bankreports_dbs[0]}")
    else:
        print("❌ Aucune base bankreports.db trouvée")
        return False
    
    # 2. Vérifier les utilisateurs
    total_users = User.objects.count()
    directeur_users = User.objects.filter(username__startswith='directeurBanque').count()
    
    print(f"👥 Utilisateurs : {total_users} total, {directeur_users} directeurs")
    
    if directeur_users < 70:
        print("⚠️  ATTENTION : Nombre de directeurs insuffisant")
        print("   💡 Solution : Exécuter python create_directeurs.py")
        return False
    
    # 3. Vérifier les emails
    import sqlite3
    try:
        conn = sqlite3.connect('bankreports.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM email_reports")
        email_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"📧 Emails : {email_count} enregistrements")
        
        if email_count < 50:
            print("⚠️  ATTENTION : Nombre d'emails insuffisant")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des emails : {e}")
        return False
    
    print("✅ Intégrité de la base de données OK")
    return True

if __name__ == '__main__':
    check_database_integrity()

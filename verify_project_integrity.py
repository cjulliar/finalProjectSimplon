#!/usr/bin/env python3
"""
Script de vérification complète de l'intégrité du projet
Vérifie que tout fonctionne avec la base SQLite de production
"""

import os
import sys
import django
import sqlite3
import requests
from datetime import datetime

# Ajouter le répertoire frontend au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'frontend'))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')
django.setup()

from django.contrib.auth.models import User
from django.conf import settings

def check_database_integrity():
    """Vérifie l'intégrité de la base de données"""
    
    print("🗄️ VÉRIFICATION DE LA BASE DE DONNÉES")
    print("=" * 50)
    
    # 1. Vérifier qu'il n'y a qu'une seule base active
    bankreports_dbs = []
    for root, dirs, files in os.walk('.'):
        # Exclure les dossiers de sauvegarde
        if 'backups' in root or 'old_databases_backup' in root:
            continue
        for file in files:
            if file.endswith('.db') and 'bankreports' in file:
                full_path = os.path.join(root, file)
                bankreports_dbs.append(full_path)
    
    if len(bankreports_dbs) == 1:
        print(f"✅ Base unique détectée : {bankreports_dbs[0]}")
        db_path = bankreports_dbs[0]
    else:
        print(f"❌ PROBLÈME : {len(bankreports_dbs)} bases trouvées")
        for db in bankreports_dbs:
            print(f"   📄 {db}")
        return False
    
    # 2. Vérifier que Django utilise la bonne base
    django_db_path = settings.DATABASES['default']['NAME']
    if os.path.abspath(django_db_path) == os.path.abspath(db_path):
        print("✅ Django utilise la bonne base de données")
    else:
        print(f"❌ PROBLÈME : Django utilise {django_db_path} au lieu de {db_path}")
        return False
    
    # 3. Vérifier les tables principales
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Tables Django
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'auth_%'")
        auth_tables = [row[0] for row in cursor.fetchall()]
        print(f"✅ Tables Django : {len(auth_tables)} tables d'authentification")
        
        # Tables métier
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'auth_%' AND name NOT LIKE 'django_%'")
        business_tables = [row[0] for row in cursor.fetchall()]
        print(f"✅ Tables métier : {len(business_tables)} tables")
        
        # Compter les données
        cursor.execute("SELECT COUNT(*) FROM auth_user")
        user_count = cursor.fetchone()[0]
        print(f"👥 Utilisateurs : {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM email_reports")
        email_count = cursor.fetchone()[0]
        print(f"📧 Emails : {email_count}")
        
        cursor.execute("SELECT COUNT(*) FROM bank_data_enriched")
        bank_data_count = cursor.fetchone()[0]
        print(f"🏦 Données bancaires : {bank_data_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification de la base : {e}")
        return False
    
    return True

def check_django_users():
    """Vérifie les utilisateurs Django"""
    
    print("\n👥 VÉRIFICATION DES UTILISATEURS DJANGO")
    print("=" * 40)
    
    total_users = User.objects.count()
    directeur_users = User.objects.filter(username__startswith='directeurBanque').count()
    admin_users = User.objects.filter(is_superuser=True).count()
    
    print(f"📊 Total utilisateurs : {total_users}")
    print(f"👨‍💼 Directeurs : {directeur_users}")
    print(f"🔑 Admins : {admin_users}")
    
    # Vérifier les emails des directeurs
    directeurs_with_wrong_email = User.objects.filter(
        username__startswith='directeurBanque'
    ).exclude(email='cyrjulliard@gmail.com').count()
    
    if directeurs_with_wrong_email == 0:
        print("✅ Tous les directeurs ont l'email cyrjulliard@gmail.com")
    else:
        print(f"❌ {directeurs_with_wrong_email} directeurs ont un email incorrect")
        return False
    
    # Tester l'authentification de quelques directeurs
    from django.contrib.auth import authenticate
    
    test_directeurs = User.objects.filter(username__startswith='directeurBanque')[:3]
    auth_success = 0
    
    for directeur in test_directeurs:
        user = authenticate(username=directeur.username, password='directeur123')
        if user and user.is_authenticated:
            auth_success += 1
            print(f"✅ {directeur.username} : authentification OK")
        else:
            print(f"❌ {directeur.username} : échec d'authentification")
    
    if auth_success == len(test_directeurs):
        print("✅ Authentification des directeurs OK")
    else:
        print("❌ Problème d'authentification des directeurs")
        return False
    
    return True

def check_web_services():
    """Vérifie que les services web fonctionnent"""
    
    print("\n🌐 VÉRIFICATION DES SERVICES WEB")
    print("=" * 35)
    
    services = [
        ("Django", "http://localhost:8080"),
        ("FastAPI", "http://localhost:8001")
    ]
    
    all_ok = True
    
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name} : accessible ({response.status_code})")
            else:
                print(f"⚠️  {service_name} : {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"❌ {service_name} : {e}")
            all_ok = False
    
    return all_ok

def check_email_access():
    """Vérifie l'accès aux emails par banque"""
    
    print("\n📧 VÉRIFICATION DE L'ACCÈS AUX EMAILS")
    print("=" * 40)
    
    try:
        conn = sqlite3.connect('bankreports.db')
        cursor = conn.cursor()
        
        # Compter les emails par banque
        cursor.execute("""
            SELECT bank_name, COUNT(*) as count 
            FROM email_reports 
            WHERE status = 'generated' 
            GROUP BY bank_name 
            ORDER BY count DESC
        """)
        
        results = cursor.fetchall()
        
        print(f"📊 Emails par banque :")
        for bank_name, count in results[:10]:  # Afficher les 10 premières
            print(f"   🏦 {bank_name} : {count} emails")
        
        if len(results) > 10:
            print(f"   ... et {len(results) - 10} autres banques")
        
        # Vérifier qu'il y a des emails pour les principales banques
        main_banks = ['A', 'B', 'C', 'D', 'E']
        missing_emails = []
        
        for bank in main_banks:
            cursor.execute("SELECT COUNT(*) FROM email_reports WHERE bank_name = ? AND status = 'generated'", (bank,))
            count = cursor.fetchone()[0]
            if count == 0:
                missing_emails.append(bank)
        
        if missing_emails:
            print(f"⚠️  Banques sans emails : {', '.join(missing_emails)}")
        else:
            print("✅ Toutes les principales banques ont des emails")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des emails : {e}")
        return False
    
    return True

def check_configuration():
    """Vérifie la configuration du projet"""
    
    print("\n⚙️  VÉRIFICATION DE LA CONFIGURATION")
    print("=" * 40)
    
    # Vérifier que Django utilise SQLite
    db_engine = settings.DATABASES['default']['ENGINE']
    if 'sqlite' in db_engine:
        print("✅ Django utilise SQLite")
    else:
        print(f"❌ Django utilise {db_engine} au lieu de SQLite")
        return False
    
    # Vérifier l'API URL
    api_url = getattr(settings, 'API_URL', None)
    if api_url:
        print(f"✅ API URL configurée : {api_url}")
    else:
        print("⚠️  API URL non configurée")
    
    # Vérifier le mode DEBUG
    if settings.DEBUG:
        print("✅ Mode DEBUG activé (développement)")
    else:
        print("✅ Mode DEBUG désactivé (production)")
    
    return True

def main():
    """Fonction principale de vérification"""
    
    print("🔍 VÉRIFICATION COMPLÈTE DE L'INTÉGRITÉ DU PROJET")
    print("=" * 60)
    print(f"📅 Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checks = [
        ("Base de données", check_database_integrity),
        ("Utilisateurs Django", check_django_users),
        ("Services web", check_web_services),
        ("Accès aux emails", check_email_access),
        ("Configuration", check_configuration)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Erreur lors de {check_name} : {e}")
            results.append((check_name, False))
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE LA VÉRIFICATION")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 Résultat : {passed}/{len(results)} vérifications réussies")
    
    if failed == 0:
        print("🎉 TOUTES LES VÉRIFICATIONS SONT PASSÉES !")
        print("✅ Le projet est prêt pour la production")
        return True
    else:
        print(f"⚠️  {failed} problème(s) détecté(s)")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 
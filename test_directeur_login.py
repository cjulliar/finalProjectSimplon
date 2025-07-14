#!/usr/bin/env python3
"""
Script pour tester la connexion des utilisateurs directeurBanqueX
et vérifier l'accès aux emails
"""

import os
import sys
import django
import requests
from django.contrib.auth import authenticate

# Ajouter le répertoire frontend au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'frontend'))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')
django.setup()

from django.contrib.auth.models import User

def test_directeur_authentication():
    """Teste l'authentification des utilisateurs directeurBanqueX"""
    
    print("🔐 TEST D'AUTHENTIFICATION DES DIRECTEURS")
    print("=" * 50)
    
    # Récupérer tous les utilisateurs directeurBanqueX
    directeurs = User.objects.filter(username__startswith='directeurBanque').order_by('username')
    
    print(f"📊 {directeurs.count()} directeurs trouvés")
    
    success_count = 0
    failed_count = 0
    
    for directeur in directeurs[:5]:  # Tester seulement les 5 premiers
        try:
            # Tester l'authentification
            user = authenticate(username=directeur.username, password='directeur123')
            
            if user and user.is_authenticated:
                print(f"✅ {directeur.username} : Authentification réussie")
                success_count += 1
                
                # Extraire le nom de la banque
                banque_name = directeur.username.replace('directeurBanque', '')
                print(f"   🏦 Banque : {banque_name}")
                
                # Vérifier s'il y a des emails pour cette banque
                import sqlite3
                conn = sqlite3.connect('bankreports.db')
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM email_reports WHERE bank_name = ? AND status = 'generated'", (banque_name,))
                email_count = cursor.fetchone()[0]
                conn.close()
                
                print(f"   📧 Emails disponibles : {email_count}")
                
            else:
                print(f"❌ {directeur.username} : Échec de l'authentification")
                failed_count += 1
                
        except Exception as e:
            print(f"❌ {directeur.username} : Erreur - {e}")
            failed_count += 1
    
    print(f"\n📊 Résumé des tests :")
    print(f"   ✅ Authentifications réussies : {success_count}")
    print(f"   ❌ Authentifications échouées : {failed_count}")
    
    return success_count > 0

def test_web_access():
    """Teste l'accès web aux pages"""
    
    print("\n🌐 TEST D'ACCÈS WEB")
    print("=" * 30)
    
    base_url = "http://localhost:8080"
    
    # Test de la page d'accueil
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Page d'accueil accessible")
        else:
            print(f"❌ Page d'accueil : {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur d'accès à la page d'accueil : {e}")
    
    # Test de la page de connexion
    try:
        response = requests.get(f"{base_url}/login/", timeout=5)
        if response.status_code == 200:
            print("✅ Page de connexion accessible")
        else:
            print(f"❌ Page de connexion : {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur d'accès à la page de connexion : {e}")

def show_connection_instructions():
    """Affiche les instructions de connexion"""
    
    print("\n📋 INSTRUCTIONS DE CONNEXION")
    print("=" * 40)
    print("🌐 Accédez à : http://localhost:8080")
    print("🔐 Identifiants disponibles :")
    print()
    
    # Afficher quelques exemples
    directeurs = User.objects.filter(username__startswith='directeurBanque').order_by('username')[:10]
    
    for directeur in directeurs:
        banque_name = directeur.username.replace('directeurBanque', '')
        print(f"   👤 {directeur.username}")
        print(f"      🔑 Mot de passe : directeur123")
        print(f"      🏦 Banque : {banque_name}")
        print()
    
    print("💡 Tous les utilisateurs directeurBanqueX ont le mot de passe : directeur123")
    print("📧 Chaque directeur verra les emails de sa banque respective")

if __name__ == '__main__':
    test_directeur_authentication()
    test_web_access()
    show_connection_instructions() 
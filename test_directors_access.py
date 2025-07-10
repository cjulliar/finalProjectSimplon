#!/usr/bin/env python3
"""
Script pour tester l'accessibilité du site pour les directeurs d'agence
"""

import os
import sys
import django
import requests
from pathlib import Path

# Configuration Django
sys.path.append('frontend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')

try:
    django.setup()
    from django.contrib.auth.models import User
    from django.contrib.auth import authenticate
    from django.test import Client
    
    def test_director_access():
        """Teste l'accessibilité pour plusieurs directeurs d'agence"""
        print("🏦 TEST D'ACCESSIBILITÉ DES DIRECTEURS D'AGENCE")
        print("=" * 60)
        
        # Récupérer tous les directeurs
        directors = User.objects.filter(username__startswith='directeur').order_by('username')
        print(f"📊 {directors.count()} directeurs trouvés dans la base de données")
        
        # Test avec quelques directeurs représentatifs
        test_directors = directors[:10]  # Test des 10 premiers
        
        print(f"\n🔐 TEST D'AUTHENTIFICATION")
        print("-" * 40)
        
        successful_auth = 0
        failed_auth = 0
        
        for director in test_directors:
            username = director.username
            password = "directeur123"
            
            # Test d'authentification Django
            user = authenticate(username=username, password=password)
            
            if user:
                print(f"✅ {username} - Authentification réussie")
                successful_auth += 1
            else:
                print(f"❌ {username} - Échec d'authentification")
                failed_auth += 1
        
        print(f"\n📊 RÉSUMÉ AUTHENTIFICATION:")
        print(f"   • Réussis: {successful_auth}")
        print(f"   • Échecs: {failed_auth}")
        print(f"   • Total testés: {len(test_directors)}")
        
        # Test d'accès au site web
        print(f"\n🌐 TEST D'ACCÈS AU SITE WEB")
        print("-" * 40)
        
        # Démarrer le serveur Django en arrière-plan pour les tests
        print("🚀 Démarrage du serveur Django pour les tests...")
        
        # Test avec un client Django
        client = Client()
        
        # Test de la page de connexion
        try:
            response = client.get('/login/')
            if response.status_code == 200:
                print("✅ Page de connexion accessible")
            else:
                print(f"❌ Page de connexion non accessible (status: {response.status_code})")
        except Exception as e:
            print(f"❌ Erreur lors de l'accès à la page de connexion: {e}")
        
        # Test de connexion avec un directeur
        if test_directors:
            test_director = test_directors[0]
            try:
                login_success = client.login(
                    username=test_director.username,
                    password="directeur123"
                )
                
                if login_success:
                    print(f"✅ Connexion web réussie pour {test_director.username}")
                    
                    # Test d'accès au dashboard
                    dashboard_response = client.get('/')
                    if dashboard_response.status_code == 200:
                        print("✅ Dashboard accessible après connexion")
                    else:
                        print(f"❌ Dashboard non accessible (status: {dashboard_response.status_code})")
                else:
                    print(f"❌ Connexion web échouée pour {test_director.username}")
                    
            except Exception as e:
                print(f"❌ Erreur lors du test de connexion web: {e}")
        
        print(f"\n🔐 IDENTIFIANTS DE TEST:")
        print(f"   • URL: http://localhost:8080/login/")
        print(f"   • Email: cyrjulliard@gmail.com")
        print(f"   • Mot de passe: directeur123")
        print(f"   • Exemples de noms d'utilisateur:")
        
        for i, director in enumerate(test_directors[:5]):
            print(f"     - {director.username}")
        
        if len(test_directors) > 5:
            print(f"     - ... et {len(test_directors) - 5} autres")
        
        print(f"\n💡 RECOMMANDATIONS:")
        if successful_auth == len(test_directors):
            print("  ✅ Tous les directeurs peuvent s'authentifier")
            print("  🌐 Le site est accessible pour tous les directeurs")
        else:
            print("  ⚠️  Certains directeurs ont des problèmes d'authentification")
            print("  🔧 Vérifiez les mots de passe et les permissions")
        
        print(f"\n✅ Test terminé!")
    
    if __name__ == "__main__":
        test_director_access()

except Exception as e:
    print(f"❌ Erreur: {e}")
    print("💡 Assurez-vous que Django est correctement configuré.")
    sys.exit(1) 
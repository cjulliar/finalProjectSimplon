#!/usr/bin/env python3
"""
Script final pour vérifier l'accessibilité du site pour tous les directeurs d'agence
"""

import os
import sys
import django
import requests
import time

# Configuration Django
sys.path.append('frontend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')

try:
    django.setup()
    from django.contrib.auth.models import User
    from django.contrib.auth import authenticate
    
    def verify_directors_access():
        """Vérifie l'accessibilité complète pour tous les directeurs d'agence"""
        print("🏦 VÉRIFICATION COMPLÈTE - ACCESSIBILITÉ DIRECTEURS D'AGENCE")
        print("=" * 70)
        
        # Vérifier que seuls les directeurs existent
        all_users = User.objects.all()
        directors = User.objects.filter(username__startswith='directeur')
        others = User.objects.exclude(username__startswith='directeur')
        
        print(f"📊 ÉTAT DES UTILISATEURS:")
        print(f"   • Total utilisateurs: {all_users.count()}")
        print(f"   • Directeurs d'agence: {directors.count()}")
        print(f"   • Autres utilisateurs: {others.count()}")
        
        if others.count() > 0:
            print(f"   ⚠️  ATTENTION: {others.count()} utilisateur(s) non-directeur détecté(s)")
            for user in others:
                print(f"      - {user.username} ({user.email})")
        else:
            print(f"   ✅ Parfait: Seuls les directeurs d'agence sont présents")
        
        # Test d'authentification pour tous les directeurs
        print(f"\n🔐 TEST D'AUTHENTIFICATION COMPLET")
        print("-" * 50)
        
        successful_auth = 0
        failed_auth = 0
        failed_users = []
        
        for director in directors:
            username = director.username
            password = "directeur123"
            
            user = authenticate(username=username, password=password)
            
            if user:
                successful_auth += 1
                if successful_auth <= 5:  # Afficher les 5 premiers
                    print(f"   ✅ {username}")
            else:
                failed_auth += 1
                failed_users.append(username)
                print(f"   ❌ {username}")
        
        if successful_auth > 5:
            print(f"   ... et {successful_auth - 5} autres directeurs authentifiés avec succès")
        
        print(f"\n📊 RÉSUMÉ AUTHENTIFICATION:")
        print(f"   • Réussis: {successful_auth}")
        print(f"   • Échecs: {failed_auth}")
        print(f"   • Taux de réussite: {(successful_auth/directors.count())*100:.1f}%")
        
        if failed_auth > 0:
            print(f"\n❌ DIRECTEURS EN ÉCHEC:")
            for username in failed_users[:10]:  # Afficher les 10 premiers échecs
                print(f"   • {username}")
            if len(failed_users) > 10:
                print(f"   • ... et {len(failed_users) - 10} autres")
        
        # Test d'accessibilité du site web
        print(f"\n🌐 TEST D'ACCESSIBILITÉ DU SITE WEB")
        print("-" * 50)
        
        base_url = "http://localhost:8080"
        
        # Test de la page de connexion
        try:
            response = requests.get(f"{base_url}/login/", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ Page de connexion accessible (status: {response.status_code})")
            else:
                print(f"   ❌ Page de connexion non accessible (status: {response.status_code})")
        except requests.RequestException as e:
            print(f"   ❌ Erreur d'accès à la page de connexion: {e}")
        
        # Test de la page d'accueil (doit rediriger vers login si non connecté)
        try:
            response = requests.get(f"{base_url}/", timeout=5, allow_redirects=False)
            if response.status_code in [200, 302]:  # 200 = connecté, 302 = redirection vers login
                print(f"   ✅ Page d'accueil accessible (status: {response.status_code})")
            else:
                print(f"   ❌ Page d'accueil non accessible (status: {response.status_code})")
        except requests.RequestException as e:
            print(f"   ❌ Erreur d'accès à la page d'accueil: {e}")
        
        # Test avec un directeur spécifique
        if directors.count() > 0:
            test_director = directors.first()
            print(f"\n🧪 TEST DE CONNEXION AVEC {test_director.username}")
            print("-" * 50)
            
            # Simuler une connexion
            session = requests.Session()
            try:
                # Récupérer le token CSRF
                login_page = session.get(f"{base_url}/login/")
                if login_page.status_code == 200:
                    print(f"   ✅ Page de connexion chargée")
                    
                    # Tenter la connexion
                    login_data = {
                        'username': test_director.username,
                        'password': 'directeur123',
                        'csrfmiddlewaretoken': 'test'  # Simplifié pour le test
                    }
                    
                    login_response = session.post(f"{base_url}/login/", data=login_data, allow_redirects=False)
                    
                    if login_response.status_code in [200, 302]:
                        print(f"   ✅ Tentative de connexion effectuée (status: {login_response.status_code})")
                    else:
                        print(f"   ❌ Échec de la tentative de connexion (status: {login_response.status_code})")
                else:
                    print(f"   ❌ Impossible de charger la page de connexion")
                    
            except requests.RequestException as e:
                print(f"   ❌ Erreur lors du test de connexion: {e}")
        
        # Résumé final
        print(f"\n📋 RÉSUMÉ FINAL")
        print("=" * 50)
        
        if successful_auth == directors.count() and others.count() == 0:
            print(f"🎉 EXCELLENT! Tous les directeurs d'agence peuvent accéder au site")
            print(f"   • {directors.count()} directeurs configurés")
            print(f"   • 100% d'authentification réussie")
            print(f"   • Aucun utilisateur non-directeur")
        elif successful_auth == directors.count():
            print(f"✅ BON! Tous les directeurs peuvent s'authentifier")
            print(f"   • {directors.count()} directeurs configurés")
            print(f"   • 100% d'authentification réussie")
            print(f"   • ⚠️  {others.count()} utilisateur(s) non-directeur présent(s)")
        elif successful_auth > directors.count() * 0.9:
            print(f"⚠️  ACCEPTABLE! La plupart des directeurs peuvent s'authentifier")
            print(f"   • {successful_auth}/{directors.count()} directeurs authentifiés")
            print(f"   • Taux de réussite: {(successful_auth/directors.count())*100:.1f}%")
        else:
            print(f"❌ PROBLÈME! Beaucoup de directeurs ne peuvent pas s'authentifier")
            print(f"   • {successful_auth}/{directors.count()} directeurs authentifiés")
            print(f"   • Taux de réussite: {(successful_auth/directors.count())*100:.1f}%")
        
        print(f"\n🔐 INFORMATIONS DE CONNEXION:")
        print(f"   • URL: {base_url}/login/")
        print(f"   • Email: cyrjulliard@gmail.com")
        print(f"   • Mot de passe: directeur123")
        print(f"   • Format username: directeurBanqueX (où X = nom de l'agence)")
        
        print(f"\n📊 AGENCES DISPONIBLES:")
        # Récupérer les agences depuis la base de données
        import sqlite3
        try:
            conn = sqlite3.connect('bankreports.db')
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT agence FROM bank_data_enriched ORDER BY agence')
            agences = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            print(f"   • {len(agences)} agences dans la base de données")
            for i, agence in enumerate(agences[:5]):
                username = f"directeur{agence.replace(' ', '')}"
                print(f"     - {agence} → {username}")
            
            if len(agences) > 5:
                print(f"     - ... et {len(agences) - 5} autres agences")
                
        except Exception as e:
            print(f"   • Erreur lors de la récupération des agences: {e}")
        
        print(f"\n✅ Vérification terminée!")
    
    if __name__ == "__main__":
        verify_directors_access()

except Exception as e:
    print(f"❌ Erreur: {e}")
    print("💡 Assurez-vous que Django est correctement configuré.")
    sys.exit(1) 
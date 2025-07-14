#!/usr/bin/env python3
"""
Script de test pour vérifier le bon fonctionnement du système bancaire
"""

import requests
import time
import sys

def test_service(url, name, expected_status=200):
    """Test un service et retourne le résultat"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == expected_status:
            print(f"✅ {name}: OK (Status: {response.status_code})")
            return True
        else:
            print(f"❌ {name}: ERREUR (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: ERREUR DE CONNEXION - {e}")
        return False

def main():
    print("🧪 TEST DU SYSTÈME BANCAIRE INTELLIGENT")
    print("=" * 50)
    
    # URLs à tester
    services = [
        ("http://localhost:8080/login/", "Frontend Django (Login)"),
        ("http://localhost:8080/", "Frontend Django (Accueil)"),
        ("http://localhost:8001/health", "API FastAPI (Health)"),
        ("http://localhost:8001/docs", "API FastAPI (Documentation)"),
    ]
    
    results = []
    
    for url, name in services:
        results.append(test_service(url, name))
        time.sleep(1)  # Pause entre les tests
    
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS DU TEST")
    print("=" * 50)
    
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print(f"🎉 TOUS LES SERVICES FONCTIONNENT ! ({success_count}/{total_count})")
        print("\n🌐 ACCÈS AUX SERVICES :")
        print("   • Frontend Django: http://localhost:8080")
        print("   • API FastAPI: http://localhost:8001")
        print("   • Documentation API: http://localhost:8001/docs")
        print("\n🔐 IDENTIFIANTS DE TEST :")
        print("   • Email: cyrjulliard@gmail.com")
        print("   • Mot de passe: directeur123")
        print("   • Utilisateurs: directeurBanqueAG, directeurBanqueBG, directeurBanqueC")
        return 0
    else:
        print(f"⚠️  CERTAINS SERVICES ONT DES PROBLÈMES ({success_count}/{total_count})")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
#!/usr/bin/env python3
"""
Script pour afficher les identifiants de connexion
"""

import os
import sys
import django
from pathlib import Path
import sqlite3

DB_PATH = os.environ.get('BANKREPORTS_DB_PATH', '/app/bankreports.db')

def show_credentials():
    """Affiche les identifiants de connexion"""
    print("🔐 IDENTIFIANTS DE CONNEXION - SYSTÈME BANCAIRE INTELLIGENT")
    print("=" * 60)
    
    # Configuration Django
    sys.path.append('frontend')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')
    
    try:
        django.setup()
        from django.conf import settings
        
        print("\n🌐 FRONTEND DJANGO (http://localhost:8080)")
        print("-" * 40)
        
        # Déterminer la base de données utilisée
        db_engine = settings.DATABASES['default']['ENGINE']
        
        if 'postgresql' in db_engine:
            print("🗄️ Base de données: PostgreSQL")
            print("👤 Utilisateur: admin")
            print("🔑 Mot de passe: hBtH_apEj3dP_baa")
            print("📧 Email: admin@example.com")
        else:
            print("🗄️ Base de données: SQLite")
            print("👤 Utilisateur: admin")
            print("🔑 Mot de passe: admin123")
            print("📧 Email: admin@example.com")
        
        print("\n🔌 API FASTAPI (http://localhost:8000)")
        print("-" * 40)
        print("📖 Documentation: http://localhost:8000/docs")
        print("👤 Utilisateur: admin")
        print("🔑 Mot de passe: hBtH_apEj3dP_baa")
        
        print("\n📊 MONITORING")
        print("-" * 40)
        print("📈 Prometheus: http://localhost:9090")
        print("📊 Grafana: http://localhost:3000")
        print("   👤 Utilisateur: admin")
        print("   🔑 Mot de passe: admin")
        
        print("\n🚀 COMMANDES DE DÉMARRAGE")
        print("-" * 40)
        print("1. Démarrer le projet complet:")
        print("   ./run_project.sh")
        print()
        print("2. Démarrer uniquement Django:")
        print("   cd frontend && python manage.py runserver 8080")
        print()
        print("3. Démarrer uniquement l'API:")
        print("   cd src && python -m uvicorn api.main:app --port 8000")
        
        print("\n✅ INFORMATIONS SUPPLÉMENTAIRES")
        print("-" * 40)
        print("• Le frontend Django est accessible sur http://localhost:8080")
        print("• L'API FastAPI est accessible sur http://localhost:8000")
        print("• La documentation API est sur http://localhost:8000/docs")
        print("• Les tests peuvent être lancés avec: python test_ci_cd.py")
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des identifiants: {e}")
        print("\n💡 Identifiants par défaut:")
        print("👤 Utilisateur: admin")
        print("🔑 Mot de passe: admin123")
        print("📧 Email: admin@example.com")

if __name__ == "__main__":
    show_credentials() 
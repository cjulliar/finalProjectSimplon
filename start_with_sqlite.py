#!/usr/bin/env python3
"""
Script pour démarrer Django avec SQLite
"""

import os
import sys
import subprocess

def start_django_with_sqlite():
    """Démarre Django en forçant l'utilisation de SQLite"""
    
    print("🗄️ DÉMARRAGE DE DJANGO AVEC SQLITE")
    print("=" * 50)
    
    # Forcer l'utilisation de SQLite
    os.environ['USE_POSTGRES'] = 'false'
    os.environ['POSTGRES_HOST'] = ''
    os.environ['POSTGRES_DB'] = ''
    os.environ['POSTGRES_USER'] = ''
    os.environ['POSTGRES_PASSWORD'] = ''
    
    print("✅ Variables d'environnement configurées pour SQLite")
    
    # Aller dans le dossier frontend
    os.chdir('frontend')
    
    print("🌐 Démarrage du serveur Django sur http://localhost:8080")
    print("🔐 Identifiants disponibles:")
    print("   • admin / hBtH_apEj3dP_baa")
    print("   • directeurBanqueA / directeur123")
    print("   • directeurBanqueBG / directeur123")
    print("   • testuser / test123")
    print("\n⏹️  Pour arrêter le serveur: Ctrl+C")
    print("=" * 50)
    
    # Démarrer le serveur Django
    try:
        subprocess.run(['python', 'manage.py', 'runserver', '0.0.0.0:8080'])
    except KeyboardInterrupt:
        print("\n👋 Serveur arrêté")

if __name__ == "__main__":
    start_django_with_sqlite() 
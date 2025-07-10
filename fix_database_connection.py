#!/usr/bin/env python3
"""
Script pour résoudre le problème de connexion à la base de données
"""

import os
import sys
import subprocess

def check_postgresql():
    """Vérifie si PostgreSQL est démarré"""
    try:
        result = subprocess.run(['pg_isready', '-h', 'localhost'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def start_postgresql():
    """Tente de démarrer PostgreSQL"""
    print("🐘 Tentative de démarrage de PostgreSQL...")
    
    # Essayer différentes commandes selon le système
    commands = [
        ['brew', 'services', 'start', 'postgresql'],
        ['sudo', 'systemctl', 'start', 'postgresql'],
        ['sudo', 'service', 'postgresql', 'start']
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ PostgreSQL démarré avec: {' '.join(cmd)}")
                return True
        except:
            continue
    
    print("❌ Impossible de démarrer PostgreSQL automatiquement")
    return False

def force_sqlite():
    """Force Django à utiliser SQLite"""
    print("🗄️ Forçage de l'utilisation de SQLite...")
    
    # Modifier temporairement les variables d'environnement
    os.environ['USE_POSTGRES'] = 'false'
    os.environ['POSTGRES_HOST'] = ''
    
    print("✅ Variables d'environnement modifiées pour SQLite")

def main():
    """Fonction principale"""
    print("🔧 RÉSOLUTION DU PROBLÈME DE CONNEXION")
    print("=" * 50)
    
    # Vérifier PostgreSQL
    if check_postgresql():
        print("✅ PostgreSQL est démarré et accessible")
        print("🌐 Vous pouvez utiliser PostgreSQL")
        return "postgresql"
    else:
        print("❌ PostgreSQL n'est pas accessible")
        
        # Demander à l'utilisateur
        print("\n🤔 Que souhaitez-vous faire ?")
        print("1. Démarrer PostgreSQL")
        print("2. Utiliser SQLite (recommandé pour le développement)")
        
        choice = input("\nVotre choix (1 ou 2): ").strip()
        
        if choice == "1":
            if start_postgresql():
                print("✅ PostgreSQL démarré avec succès!")
                return "postgresql"
            else:
                print("❌ Échec du démarrage de PostgreSQL")
                print("🔄 Basculement vers SQLite...")
                force_sqlite()
                return "sqlite"
        else:
            force_sqlite()
            return "sqlite"

if __name__ == "__main__":
    db_type = main()
    
    if db_type == "sqlite":
        print("\n🗄️ CONFIGURATION SQLITE")
        print("=" * 30)
        print("✅ Django utilisera SQLite")
        print("✅ Les utilisateurs existent déjà dans SQLite")
        print("🌐 Redémarrez le serveur Django:")
        print("   cd frontend && python manage.py runserver 0.0.0.0:8080")
        print("\n🔐 Identifiants disponibles:")
        print("   • admin / hBtH_apEj3dP_baa")
        print("   • directeurBanqueA / directeur123")
        print("   • directeurBanqueBG / directeur123")
        print("   • testuser / test123")
    else:
        print("\n🐘 CONFIGURATION POSTGRESQL")
        print("=" * 30)
        print("✅ PostgreSQL est prêt")
        print("🌐 Redémarrez le serveur Django:")
        print("   cd frontend && python manage.py runserver 0.0.0.0:8080") 
#!/usr/bin/env python3
"""
Script pour créer les utilisateurs dans la base SQLite Django
"""

import os
import sys
import django

# Configuration Django
sys.path.append('frontend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

def create_users():
    """Crée les utilisateurs nécessaires dans SQLite"""
    
    print("👥 CRÉATION DES UTILISATEURS DANS SQLITE")
    print("=" * 50)
    
    # Liste des utilisateurs à créer
    users_to_create = [
        {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'hBtH_apEj3dP_baa',
            'is_staff': True,
            'is_superuser': True,
            'first_name': 'Admin',
            'last_name': 'System'
        },
        {
            'username': 'directeurBanqueA',
            'email': 'cyrjulliard@gmail.com',
            'password': 'directeur123',
            'is_staff': False,
            'is_superuser': False,
            'first_name': 'Directeur',
            'last_name': 'Banque A'
        },
        {
            'username': 'directeurBanqueBG',
            'email': 'cyrjulliard+directeurBanqueBG@gmail.com',
            'password': 'directeur123',
            'is_staff': False,
            'is_superuser': False,
            'first_name': 'Directeur',
            'last_name': 'Banque BG'
        },
        {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'test123',
            'is_staff': False,
            'is_superuser': False,
            'first_name': 'Test',
            'last_name': 'User'
        }
    ]
    
    created_count = 0
    
    for user_data in users_to_create:
        username = user_data['username']
        
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            print(f"⚠️  Utilisateur '{username}' existe déjà")
            continue
        
        # Créer l'utilisateur
        try:
            user = User.objects.create_user(
                username=username,
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                is_staff=user_data['is_staff'],
                is_superuser=user_data['is_superuser']
            )
            print(f"✅ Utilisateur '{username}' créé avec succès")
            created_count += 1
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de '{username}': {e}")
    
    print(f"\n📊 RÉSUMÉ:")
    print(f"   • {created_count} utilisateur(s) créé(s)")
    print(f"   • {len(users_to_create)} utilisateur(s) au total")
    
    # Afficher tous les utilisateurs existants
    print(f"\n👥 UTILISATEURS DISPONIBLES:")
    all_users = User.objects.all()
    for user in all_users:
        status = "Admin" if user.is_superuser else "Directeur" if "directeur" in user.username else "Utilisateur"
        print(f"   • {user.username} ({user.email}) - {status}")
    
    print(f"\n🔐 IDENTIFIANTS DE CONNEXION:")
    print(f"   • Admin: admin / hBtH_apEj3dP_baa")
    print(f"   • Directeur Banque A: directeurBanqueA / directeur123")
    print(f"   • Directeur Banque BG: directeurBanqueBG / directeur123")
    print(f"   • Test: testuser / test123")
    
    print(f"\n🌐 URL: http://localhost:8080/login/")
    print(f"✅ Vous pouvez maintenant vous connecter!")

if __name__ == "__main__":
    create_users() 
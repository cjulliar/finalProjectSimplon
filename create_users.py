#!/usr/bin/env python
"""
Script pour créer tous les utilisateurs nécessaires dans Django.
"""

import os
import sys
import django
from pathlib import Path

# Configuration du projet Django
sys.path.append('frontend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')

try:
    django.setup()
    from django.contrib.auth.models import User
    
    def create_user(username, password, email, is_staff=False, is_superuser=False):
        """Créer ou mettre à jour un utilisateur."""
        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_superuser = is_superuser
            user.is_staff = is_staff
            user.email = email
            user.save()
            print(f"✅ Utilisateur '{username}' mis à jour")
            return user
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=is_staff,
                is_superuser=is_superuser
            )
            print(f"✅ Utilisateur '{username}' créé")
            return user
    
    def main():
        print("🔧 Configuration des utilisateurs...")
        
        # Déterminer quelle base de données est utilisée
        from django.conf import settings
        db_engine = settings.DATABASES['default']['ENGINE']
        
        if 'postgresql' in db_engine:
            print("🗄️  Base de données: PostgreSQL")
        else:
            print("🗄️  Base de données: SQLite")
        
        # Créer l'utilisateur admin
        create_user('admin', 'hBtH_apEj3dP_baa', 'admin@example.com', is_staff=True, is_superuser=True)
        
        # Créer l'utilisateur directeurBanqueAG
        create_user('directeurBanqueAG', 'directeur123', 'directeur@banqueag.com', is_staff=True, is_superuser=False)
        
        # Créer quelques utilisateurs de test supplémentaires
        create_user('manager1', 'manager123', 'manager1@example.com', is_staff=True, is_superuser=False)
        create_user('user1', 'user123', 'user1@example.com', is_staff=False, is_superuser=False)
        
        # Lister tous les utilisateurs
        print("\n👥 Utilisateurs existants:")
        for user in User.objects.all():
            print(f"  • {user.username} ({user.email}) - Staff: {user.is_staff} - Admin: {user.is_superuser}")
        
        print("\n✅ Configuration terminée!")
        print("\n🔑 Identifiants de connexion:")
        print("  • Admin: admin / hBtH_apEj3dP_baa")
        print("  • Directeur: directeurBanqueAG / directeur123")
        print("  • Manager: manager1 / manager123")
        print("  • User: user1 / user123")
    
    if __name__ == "__main__":
        main()

except Exception as e:
    print(f"❌ Erreur: {e}")
    print("💡 Assurez-vous que Django est correctement configuré et que la base de données est accessible.")
    sys.exit(1) 
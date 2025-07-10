#!/usr/bin/env python
"""
Script pour créer/vérifier les utilisateurs admin dans Django.
Fonctionne avec PostgreSQL et SQLite.
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
    
    def create_admin_user(username, password, email):
        """Créer ou mettre à jour un utilisateur admin."""
        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.email = email
            user.save()
            print(f"✅ Utilisateur '{username}' mis à jour")
            return user
        except User.DoesNotExist:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            print(f"✅ Utilisateur '{username}' créé")
            return user
    
    def main():
        print("🔧 Configuration des utilisateurs admin...")
        
        # Déterminer quelle base de données est utilisée
        from django.conf import settings
        db_engine = settings.DATABASES['default']['ENGINE']
        
        if 'postgresql' in db_engine:
            print("🗄️  Base de données: PostgreSQL")
            # Utilisateur pour PostgreSQL (mot de passe Docker)
            create_admin_user('admin', 'hBtH_apEj3dP_baa', 'admin@example.com')
        else:
            print("🗄️  Base de données: SQLite")
            # Utilisateur pour SQLite (mot de passe simple)
            create_admin_user('admin', 'admin123', 'admin@example.com')
        
        # Lister tous les utilisateurs
        print("\n👥 Utilisateurs existants:")
        for user in User.objects.all():
            print(f"  • {user.username} ({user.email}) - Admin: {user.is_superuser}")
        
        print("\n✅ Configuration terminée!")
    
    if __name__ == "__main__":
        main()

except Exception as e:
    print(f"❌ Erreur: {e}")
    print("💡 Assurez-vous que Django est correctement configuré et que la base de données est accessible.")
    sys.exit(1) 
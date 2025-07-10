#!/usr/bin/env python
"""
Script pour tester l'authentification Django.
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
    from django.contrib.auth import authenticate
    from django.contrib.auth.models import User
    
    def test_authentication(username, password):
        """Tester l'authentification d'un utilisateur."""
        print(f"\n🔐 Test d'authentification pour '{username}'...")
        
        # Vérifier si l'utilisateur existe
        try:
            user = User.objects.get(username=username)
            print(f"✅ Utilisateur '{username}' trouvé dans la base de données")
            print(f"   • Email: {user.email}")
            print(f"   • Actif: {user.is_active}")
            print(f"   • Staff: {user.is_staff}")
            print(f"   • Superuser: {user.is_superuser}")
        except User.DoesNotExist:
            print(f"❌ Utilisateur '{username}' non trouvé dans la base de données")
            return False
        
        # Tester l'authentification
        authenticated_user = authenticate(username=username, password=password)
        
        if authenticated_user:
            print(f"✅ Authentification réussie pour '{username}'")
            print(f"   • ID: {authenticated_user.id}")
            print(f"   • Email: {authenticated_user.email}")
            return True
        else:
            print(f"❌ Échec de l'authentification pour '{username}'")
            print(f"   • Vérifiez le mot de passe")
            return False
    
    def main():
        print("🧪 Test d'authentification Django")
        print("=" * 50)
        
        # Déterminer quelle base de données est utilisée
        from django.conf import settings
        db_engine = settings.DATABASES['default']['ENGINE']
        
        if 'postgresql' in db_engine:
            print("🗄️  Base de données: PostgreSQL")
        else:
            print("🗄️  Base de données: SQLite")
        
        # Tester les différents utilisateurs
        users_to_test = [
            ('admin', 'hBtH_apEj3dP_baa'),
            ('directeurBanqueAG', 'directeur123'),
            ('manager1', 'manager123'),
            ('user1', 'user123'),
        ]
        
        results = []
        for username, password in users_to_test:
            success = test_authentication(username, password)
            results.append((username, success))
        
        # Résumé
        print("\n" + "=" * 50)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 50)
        
        for username, success in results:
            status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
            print(f"  • {username}: {status}")
        
        # Recommandations
        print("\n💡 RECOMMANDATIONS:")
        if all(success for _, success in results):
            print("  ✅ Tous les utilisateurs peuvent se connecter")
            print("  🌐 Vous pouvez maintenant tester la connexion sur http://localhost:8080/login/")
        else:
            print("  ⚠️  Certains utilisateurs ont des problèmes d'authentification")
            print("  🔧 Vérifiez les mots de passe et les permissions")
    
    if __name__ == "__main__":
        main()

except Exception as e:
    print(f"❌ Erreur: {e}")
    print("💡 Assurez-vous que Django est correctement configuré et que la base de données est accessible.")
    sys.exit(1) 
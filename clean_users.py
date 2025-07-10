#!/usr/bin/env python3
"""
Script pour nettoyer les utilisateurs - ne garder que les directeurs d'agence
"""

import os
import sys
import django

# Configuration Django
sys.path.append('frontend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')

try:
    django.setup()
    from django.contrib.auth.models import User
    
    def clean_users():
        """Supprime tous les utilisateurs sauf les directeurs d'agence"""
        print("🧹 NETTOYAGE DES UTILISATEURS")
        print("=" * 50)
        
        # Compter les utilisateurs avant nettoyage
        all_users = User.objects.all()
        directors = User.objects.filter(username__startswith='directeur')
        others = User.objects.exclude(username__startswith='directeur')
        
        print(f"📊 État avant nettoyage:")
        print(f"   • Total utilisateurs: {all_users.count()}")
        print(f"   • Directeurs d'agence: {directors.count()}")
        print(f"   • Autres utilisateurs: {others.count()}")
        
        if others.count() > 0:
            print(f"\n🗑️  Suppression des utilisateurs non-directeurs:")
            for user in others:
                print(f"   • Suppression de {user.username} ({user.email})")
                user.delete()
            
            print(f"✅ {others.count()} utilisateur(s) supprimé(s)")
        else:
            print(f"\n✅ Aucun utilisateur non-directeur à supprimer")
        
        # Vérifier l'état après nettoyage
        remaining_directors = User.objects.filter(username__startswith='directeur')
        print(f"\n📊 État après nettoyage:")
        print(f"   • Directeurs d'agence: {remaining_directors.count()}")
        print(f"   • Total utilisateurs: {User.objects.count()}")
        
        # Afficher quelques exemples de directeurs
        print(f"\n👥 EXEMPLES DE DIRECTEURS DISPONIBLES:")
        for i, director in enumerate(remaining_directors[:5]):
            print(f"   • {director.username} ({director.email})")
        
        if remaining_directors.count() > 5:
            print(f"   • ... et {remaining_directors.count() - 5} autres")
        
        print(f"\n🔐 IDENTIFIANTS DE CONNEXION:")
        print(f"   • URL: http://localhost:8080/login/")
        print(f"   • Email: cyrjulliard@gmail.com")
        print(f"   • Mot de passe: directeur123")
        
        print(f"\n✅ Nettoyage terminé!")
        print(f"🎯 Seuls les directeurs d'agence peuvent maintenant se connecter")
    
    if __name__ == "__main__":
        clean_users()

except Exception as e:
    print(f"❌ Erreur: {e}")
    print("💡 Assurez-vous que Django est correctement configuré.")
    sys.exit(1) 
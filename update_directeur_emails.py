#!/usr/bin/env python3
"""
Script pour mettre à jour tous les emails des directeurs vers cyrjulliard@gmail.com
"""

import os
import sys
import django

# Ajouter le répertoire frontend au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'frontend'))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')
django.setup()

from django.contrib.auth.models import User

def update_directeur_emails():
    """Met à jour tous les emails des directeurs vers cyrjulliard@gmail.com"""
    
    print("📧 MISE À JOUR DES EMAILS DES DIRECTEURS")
    print("=" * 50)
    
    # Récupérer tous les utilisateurs directeurBanqueX
    directeurs = User.objects.filter(username__startswith='directeurBanque')
    
    print(f"📊 {directeurs.count()} directeurs trouvés")
    
    updated_count = 0
    
    for directeur in directeurs:
        try:
            old_email = directeur.email
            directeur.email = 'cyrjulliard@gmail.com'
            directeur.save()
            
            print(f"✅ {directeur.username} : {old_email} → cyrjulliard@gmail.com")
            updated_count += 1
            
        except Exception as e:
            print(f"❌ Erreur pour {directeur.username}: {e}")
    
    print(f"\n📊 Résumé :")
    print(f"   ✅ Emails mis à jour : {updated_count}")
    print(f"   📧 Nouvel email : cyrjulliard@gmail.com")

if __name__ == '__main__':
    update_directeur_emails() 
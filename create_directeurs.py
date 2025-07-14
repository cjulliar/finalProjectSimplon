#!/usr/bin/env python3
"""
Script pour créer les utilisateurs directeurBanqueX avec le mot de passe directeur123
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

def create_directeur_users():
    """Crée les utilisateurs directeurBanqueX avec le mot de passe directeur123"""
    
    # Liste des banques disponibles dans la base
    banques = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    
    # Ajouter aussi les banques avec deux lettres
    banques.extend(['AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ'])
    banques.extend(['BA', 'BB', 'BC', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BK', 'BL', 'BM', 'BN', 'BO', 'BP', 'BQ', 'BR', 'BS', 'BT', 'BU', 'BV'])
    
    created_count = 0
    updated_count = 0
    
    for banque in banques:
        username = f'directeurBanque{banque}'
        email = f'directeur@banque{banque.lower()}.com'
        
        try:
            # Vérifier si l'utilisateur existe déjà
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'Directeur',
                    'last_name': f'Banque {banque}',
                    'is_active': True,
                    'is_staff': True,
                    'is_superuser': False
                }
            )
            
            if created:
                print(f"✅ Créé: {username} ({email})")
                created_count += 1
            else:
                print(f"ℹ️  Existant: {username} ({email})")
            
            # Définir le mot de passe directeur123 pour tous les utilisateurs
            user.set_password('directeur123')
            user.save()
            
            if not created:
                updated_count += 1
                
        except Exception as e:
            print(f"❌ Erreur pour {username}: {e}")
    
    print(f"\n📊 Résumé:")
    print(f"   - Utilisateurs créés: {created_count}")
    print(f"   - Utilisateurs mis à jour: {updated_count}")
    print(f"   - Total: {created_count + updated_count}")
    print(f"\n🔑 Tous les utilisateurs ont le mot de passe: directeur123")

if __name__ == '__main__':
    create_directeur_users() 
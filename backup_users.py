#!/usr/bin/env python3
"""
Script pour sauvegarder et restaurer les utilisateurs Django
"""

import os
import sys
import django
import json
from datetime import datetime

# Ajouter le répertoire frontend au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'frontend'))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')
django.setup()

from django.contrib.auth.models import User

def backup_users():
    """Sauvegarde tous les utilisateurs dans un fichier JSON"""
    users_data = []
    
    for user in User.objects.all():
        user_data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'password_hash': user.password  # Hash du mot de passe
        }
        users_data.append(user_data)
    
    # Sauvegarder dans un fichier JSON
    backup_file = f"users_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Sauvegarde créée : {backup_file}")
    print(f"📊 {len(users_data)} utilisateurs sauvegardés")
    
    return backup_file

def restore_users(backup_file):
    """Restaure les utilisateurs depuis un fichier JSON"""
    if not os.path.exists(backup_file):
        print(f"❌ Fichier de sauvegarde non trouvé : {backup_file}")
        return False
    
    with open(backup_file, 'r', encoding='utf-8') as f:
        users_data = json.load(f)
    
    restored_count = 0
    updated_count = 0
    
    for user_data in users_data:
        try:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_active': user_data['is_active'],
                    'is_staff': user_data['is_staff'],
                    'is_superuser': user_data['is_superuser'],
                    'password': user_data['password_hash']
                }
            )
            
            if created:
                print(f"✅ Restauré : {user.username}")
                restored_count += 1
            else:
                # Mettre à jour les données existantes
                user.email = user_data['email']
                user.first_name = user_data['first_name']
                user.last_name = user_data['last_name']
                user.is_active = user_data['is_active']
                user.is_staff = user_data['is_staff']
                user.is_superuser = user_data['is_superuser']
                user.save()
                print(f"🔄 Mis à jour : {user.username}")
                updated_count += 1
                
        except Exception as e:
            print(f"❌ Erreur pour {user_data['username']}: {e}")
    
    print(f"\n📊 Restauration terminée:")
    print(f"   - Utilisateurs restaurés: {restored_count}")
    print(f"   - Utilisateurs mis à jour: {updated_count}")
    
    return True

def list_users():
    """Liste tous les utilisateurs actuels"""
    print("👥 Utilisateurs actuels dans la base:")
    print("-" * 50)
    
    for user in User.objects.all().order_by('username'):
        status = "✅" if user.is_active else "❌"
        staff = "👨‍💼" if user.is_staff else "👤"
        superuser = "🔑" if user.is_superuser else ""
        
        print(f"{status} {staff} {superuser} {user.username} ({user.email})")
        if user.first_name or user.last_name:
            print(f"    Nom: {user.first_name} {user.last_name}")
    
    print(f"\n📊 Total: {User.objects.count()} utilisateurs")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Sauvegarde et restauration des utilisateurs Django')
    parser.add_argument('action', choices=['backup', 'restore', 'list'], help='Action à effectuer')
    parser.add_argument('--file', help='Fichier de sauvegarde pour la restauration')
    
    args = parser.parse_args()
    
    if args.action == 'backup':
        backup_users()
    elif args.action == 'restore':
        if not args.file:
            print("❌ Veuillez spécifier un fichier de sauvegarde avec --file")
            exit(1)
        restore_users(args.file)
    elif args.action == 'list':
        list_users() 
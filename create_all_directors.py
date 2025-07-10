#!/usr/bin/env python3
"""
Script pour créer tous les directeurs d'agences dans Django
"""

import os
import sys
import django
import sqlite3
from pathlib import Path

# Configuration Django
sys.path.append('frontend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')

try:
    django.setup()
    from django.contrib.auth.models import User
    
    def create_director_users():
        """Créer tous les directeurs d'agences dans Django"""
        print("🏦 CRÉATION DES DIRECTEURS D'AGENCES DANS DJANGO")
        print("=" * 60)
        
        # Récupérer la liste des agences depuis la base SQLite
        conn = sqlite3.connect('bankreports.db')
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT agence FROM bank_data_enriched ORDER BY agence')
        agences = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"📊 {len(agences)} agences trouvées")
        
        created_count = 0
        updated_count = 0
        
        for agence in agences:
            # Créer le nom d'utilisateur basé sur l'agence
            username = f"directeur{agence.replace(' ', '')}"
            email = "cyrjulliard@gmail.com"
            password = "directeur123"  # Mot de passe simple
            
            try:
                # Vérifier si l'utilisateur existe déjà
                user = User.objects.get(username=username)
                # Mettre à jour l'email et le mot de passe
                user.email = email
                user.set_password(password)
                user.save()
                print(f"✅ {username} - Mis à jour")
                updated_count += 1
            except User.DoesNotExist:
                # Créer un nouvel utilisateur
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=f"Directeur",
                    last_name=agence
                )
                print(f"✅ {username} - Créé")
                created_count += 1
        
        print(f"\n📋 RÉSUMÉ:")
        print(f"   • Utilisateurs créés: {created_count}")
        print(f"   • Utilisateurs mis à jour: {updated_count}")
        print(f"   • Total: {created_count + updated_count}")
        
        # Afficher quelques exemples d'identifiants
        print(f"\n🔐 EXEMPLES D'IDENTIFIANTS:")
        print(f"   • Email: cyrjulliard@gmail.com")
        print(f"   • Mot de passe: directeur123")
        print(f"   • Exemples de noms d'utilisateur:")
        
        for i, agence in enumerate(agences[:5]):
            username = f"directeur{agence.replace(' ', '')}"
            print(f"     - {username} (pour {agence})")
        
        if len(agences) > 5:
            print(f"     - ... et {len(agences) - 5} autres")
        
        print(f"\n✅ Création terminée!")
        
    if __name__ == "__main__":
        create_director_users()

except Exception as e:
    print(f"❌ Erreur: {e}")
    print("💡 Assurez-vous que Django est correctement configuré.")
    sys.exit(1) 
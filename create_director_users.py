#!/usr/bin/env python3
"""
Script pour créer les utilisateurs directeurs d'agences.
Chaque agence aura un directeur avec:
- Email: cyrjulliard@gmail.com (pour les tests)
- Username: directeur[NomAgence]
- Password: admin
"""

import sys
import sqlite3
from pathlib import Path

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent))

from src.db.database import SessionLocal, engine, Base
from src.db.models import User
from src.api.auth import get_password_hash


def get_all_agencies():
    """Récupérer toutes les agences de la base de données."""
    conn = sqlite3.connect('bankreports.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT agence FROM bank_data ORDER BY agence')
    agences = [row[0] for row in cursor.fetchall()]
    conn.close()
    return agences


def normalize_agency_name(agence):
    """Normaliser le nom d'agence pour créer un nom d'utilisateur valide."""
    # Remplacer les espaces par des underscores et enlever les caractères spéciaux
    normalized = agence.replace(' ', '_').replace('-', '_')
    # Garder seulement les caractères alphanumériques et underscores
    normalized = ''.join(c for c in normalized if c.isalnum() or c == '_')
    return f"directeur{normalized}"


def create_director_users():
    """Créer les utilisateurs directeurs pour toutes les agences."""
    print("🏦 Création des utilisateurs directeurs d'agences...")
    
    # Initialiser la base de données
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Récupérer toutes les agences
        agences = get_all_agencies()
        print(f"📊 Trouvé {len(agences)} agences")
        
        # Email et mot de passe standard pour tous
        standard_email_base = "cyrjulliard@gmail.com"
        standard_password = "admin"
        hashed_password = get_password_hash(standard_password)
        
        created_users = 0
        existing_users = 0
        
        for agence in agences:
            username = normalize_agency_name(agence)
            
            # Vérifier si l'utilisateur existe déjà
            existing_user = db.query(User).filter(User.username == username).first()
            
            if existing_user:
                print(f"✅ Utilisateur '{username}' existe déjà pour {agence}")
                existing_users += 1
                continue
            
            # Créer un email unique pour chaque utilisateur (en gardant le même domaine)
            unique_email = f"cyrjulliard+{username}@gmail.com"
            
            # Créer le nouvel utilisateur
            new_user = User(
                username=username,
                email=unique_email,
                hashed_password=hashed_password,
                is_active=True
            )
            
            db.add(new_user)
            print(f"➕ Créé: '{username}' pour l'agence '{agence}'")
            created_users += 1
        
        # Sauvegarder les changements
        db.commit()
        
        print(f"\n🎉 RÉSUMÉ:")
        print(f"   📈 Utilisateurs créés: {created_users}")
        print(f"   ✅ Utilisateurs existants: {existing_users}")
        print(f"   📧 Email base: {standard_email_base} (avec suffixes uniques)")
        print(f"   🔐 Mot de passe standard: {standard_password}")
        print(f"   💡 Les emails seront cyrjulliard+[username]@gmail.com")
        
        # Afficher quelques exemples
        print(f"\n🔍 EXEMPLES D'UTILISATEURS CRÉÉS:")
        sample_users = db.query(User).filter(User.username.like('directeur%')).limit(5).all()
        for user in sample_users:
            print(f"   - {user.username} | {user.email}")
        
        print(f"\n💡 CONNEXION:")
        print(f"   Utilisez n'importe quel nom d'utilisateur 'directeur...' avec le mot de passe 'admin'")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def list_all_director_users():
    """Lister tous les utilisateurs directeurs créés."""
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.username.like('directeur%')).all()
        print(f"\n📋 LISTE DES DIRECTEURS ({len(users)} utilisateurs):")
        for i, user in enumerate(users, 1):
            agence_name = user.username.replace('directeur', '').replace('_', ' ')
            print(f"   {i:2d}. {user.username:<25} -> Agence: {agence_name}")
        
        return users
    finally:
        db.close()


if __name__ == "__main__":
    print("🏦 SCRIPT DE CRÉATION DES UTILISATEURS DIRECTEURS")
    print("=" * 60)
    
    try:
        create_director_users()
        list_all_director_users()
        
        print(f"\n✅ Script terminé avec succès!")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution: {e}")
        sys.exit(1) 
#!/usr/bin/env python3
"""
Script pour configurer un utilisateur administrateur.
"""
import argparse
import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.database import SessionLocal, engine
from src.api.models import User
from src.api.auth import get_password_hash


def create_admin_user(username: str, password: str, email: str = None, output_file: str = None):
    """Crée un utilisateur administrateur."""
    try:
        # Créer les tables si elles n'existent pas
        from src.api.models import Base
        Base.metadata.create_all(bind=engine)
        
        db = SessionLocal()
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"L'utilisateur {username} existe déjà.")
            return
        
        # Créer le nouvel utilisateur administrateur
        hashed_password = get_password_hash(password)
        admin_user = User(
            username=username,
            email=email or f"{username}@example.com",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print(f"Utilisateur administrateur '{username}' créé avec succès.")
        
        # Sauvegarder les informations d'identification si demandé
        if output_file:
            with open(output_file, 'w') as f:
                f.write(f"Username: {username}\n")
                f.write(f"Password: {password}\n")
                f.write(f"Email: {email or f'{username}@example.com'}\n")
            print(f"Informations d'identification sauvegardées dans {output_file}")
        
    except Exception as e:
        print(f"Erreur lors de la création de l'utilisateur administrateur: {e}")
        return 1
    finally:
        db.close()
    
    return 0


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(description="Créer un utilisateur administrateur")
    parser.add_argument("--username", "-u", required=True, help="Nom d'utilisateur")
    parser.add_argument("--password", "-p", help="Mot de passe (généré automatiquement si non fourni)")
    parser.add_argument("--email", "-e", help="Adresse email")
    parser.add_argument("--output", "-o", help="Fichier de sortie pour les informations d'identification")
    
    args = parser.parse_args()
    
    # Générer un mot de passe si non fourni
    password = args.password
    if not password:
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(12))
        print(f"Mot de passe généré automatiquement: {password}")
    
    return create_admin_user(args.username, password, args.email, args.output)


if __name__ == "__main__":
    sys.exit(main()) 
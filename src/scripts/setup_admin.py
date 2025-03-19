#!/usr/bin/env python3
"""
Script pour configurer automatiquement un utilisateur administrateur.
Ce script est destiné à être utilisé lors du déploiement.
"""
import sys
import os
import argparse
import secrets
from pathlib import Path

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api.auth import get_password_hash
from src.db.database import SessionLocal, engine, Base
from src.db.models import User


def initialize_database():
    """Initialiser la base de données en créant toutes les tables."""
    print("Initialisation de la base de données...")
    Base.metadata.create_all(bind=engine)
    print("Base de données initialisée avec succès.")


def generate_password(length=12):
    """Générer un mot de passe aléatoire sécurisé."""
    return secrets.token_urlsafe(length)


def setup_admin_user(username="admin", email="admin@example.com", password=None):
    """
    Configurer un utilisateur administrateur.
    Si l'utilisateur existe déjà, son mot de passe sera réinitialisé.
    """
    if password is None:
        password = generate_password()
        print(f"Mot de passe généré automatiquement: {password}")
    
    db = SessionLocal()
    
    # Vérifier si l'utilisateur existe déjà
    existing_user = db.query(User).filter(User.username == username).first()
    
    # Hasher le mot de passe
    hashed_password = get_password_hash(password)
    
    if existing_user:
        # Mettre à jour l'utilisateur existant
        existing_user.hashed_password = hashed_password
        if email:
            existing_user.email = email
        existing_user.is_active = True
        db.commit()
        db.refresh(existing_user)
        print(f"Mot de passe de l'utilisateur '{username}' réinitialisé.")
    else:
        # Créer un nouvel utilisateur
        admin_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Utilisateur administrateur '{username}' créé avec succès.")
    
    db.close()
    
    # Retourner le mot de passe si généré automatiquement
    if password:
        return password
    else:
        return None


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description="Configurer un utilisateur administrateur.")
    parser.add_argument(
        "--username", "-u",
        type=str,
        default="admin",
        help="Nom d'utilisateur de l'administrateur (par défaut: admin)"
    )
    parser.add_argument(
        "--email", "-e",
        type=str,
        default="admin@example.com",
        help="Email de l'administrateur (par défaut: admin@example.com)"
    )
    parser.add_argument(
        "--password", "-p",
        type=str,
        help="Mot de passe de l'administrateur (si non spécifié, un mot de passe sera généré)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Fichier de sortie pour enregistrer les informations d'identification générées"
    )
    return parser.parse_args()


def save_credentials(username, email, password, output_file):
    """Enregistrer les informations d'identification dans un fichier."""
    with open(output_file, "w") as f:
        f.write(f"Username: {username}\n")
        f.write(f"Email: {email}\n")
        f.write(f"Password: {password}\n")
    print(f"Informations d'identification enregistrées dans {output_file}")


def main():
    """Point d'entrée principal."""
    args = parse_arguments()
    
    # Initialiser la base de données
    initialize_database()
    
    # Configurer l'administrateur
    password = setup_admin_user(args.username, args.email, args.password)
    
    # Si un fichier de sortie est spécifié et un mot de passe a été généré, enregistrer les informations
    if args.output and password:
        save_credentials(args.username, args.email, password, args.output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
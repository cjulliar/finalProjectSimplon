#!/usr/bin/env python3
"""
Script pour créer un utilisateur administrateur.
"""
import sys
import os
import argparse
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


def create_admin_user(username, password, email=None):
    """Créer un utilisateur administrateur."""
    db = SessionLocal()
    
    # Vérifier si l'utilisateur existe déjà
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        print(f"L'utilisateur '{username}' existe déjà.")
        db.close()
        return False
    
    # Créer le nouvel utilisateur
    hashed_password = get_password_hash(password)
    admin_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_active=True
    )
    
    # Ajouter à la base de données
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print(f"Utilisateur administrateur '{username}' créé avec succès.")
    db.close()
    return True


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description="Créer un utilisateur administrateur pour l'API.")
    parser.add_argument(
        "--username", "-u",
        type=str,
        required=True,
        help="Nom d'utilisateur pour l'administrateur"
    )
    parser.add_argument(
        "--password", "-p",
        type=str,
        required=True,
        help="Mot de passe pour l'administrateur"
    )
    parser.add_argument(
        "--email", "-e",
        type=str,
        help="Email pour l'administrateur (optionnel)"
    )
    return parser.parse_args()


def main():
    """Point d'entrée principal."""
    args = parse_arguments()
    
    # Vérifier les données
    if len(args.password) < 8:
        print("Erreur: Le mot de passe doit contenir au moins 8 caractères.")
        return 1
    
    # Initialiser la base de données
    initialize_database()
    
    # Créer l'utilisateur
    success = create_admin_user(args.username, args.password, args.email)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 
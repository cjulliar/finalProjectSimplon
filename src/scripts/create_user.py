#!/usr/bin/env python3
"""
Script pour créer un nouvel utilisateur.
"""
import sys
import os
from pathlib import Path
import argparse
from passlib.context import CryptContext

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.database import get_db
from src.db.models import User

# Créer un contexte de hachage pour les mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description="Créer un nouvel utilisateur.")
    parser.add_argument("--username", "-u", type=str, required=True, help="Nom d'utilisateur")
    parser.add_argument("--password", "-p", type=str, required=True, help="Mot de passe")
    parser.add_argument("--email", "-e", type=str, required=True, help="Adresse email")
    return parser.parse_args()


def create_user(db, username, password, email):
    """Créer un nouvel utilisateur."""
    # Vérifier si l'utilisateur existe déjà
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        print(f"L'utilisateur '{username}' existe déjà.")
        return None
    
    # Hacher le mot de passe
    hashed_password = pwd_context.hash(password)
    
    # Créer l'utilisateur
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_active=True
    )
    
    # Ajouter l'utilisateur à la base de données
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"Utilisateur '{username}' créé avec succès (ID: {user.id}).")
    print(f"Email: {email}")
    
    return user


def main():
    """Point d'entrée principal."""
    args = parse_arguments()
    
    # Obtenir une session de base de données
    db = next(get_db())
    
    # Créer l'utilisateur
    user = create_user(db, args.username, args.password, args.email)
    
    if not user:
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
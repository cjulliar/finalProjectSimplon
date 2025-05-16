#!/usr/bin/env python3
"""
Script pour initialiser la base de données avec Alembic.
"""
import sys
import os
import argparse
import subprocess
from pathlib import Path

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.database import engine, Base
from src.db.models import User, BankData, Analysis, Visualization, ScheduledReport
from src.api.auth import get_password_hash


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description="Initialiser la base de données avec Alembic.")
    parser.add_argument(
        "--create-admin",
        action="store_true",
        help="Créer un utilisateur administrateur"
    )
    parser.add_argument(
        "--username",
        type=str,
        default="admin",
        help="Nom d'utilisateur pour l'administrateur (par défaut: admin)"
    )
    parser.add_argument(
        "--password",
        type=str,
        default="admin123",
        help="Mot de passe pour l'administrateur (par défaut: admin123)"
    )
    parser.add_argument(
        "--email",
        type=str,
        default="admin@example.com",
        help="Email pour l'administrateur (par défaut: admin@example.com)"
    )
    return parser.parse_args()


def run_alembic_migrations():
    """Exécuter les migrations Alembic."""
    print("Exécution des migrations Alembic...")
    
    # Chemin vers le répertoire racine du projet
    project_root = Path(__file__).parent.parent.parent
    
    # Exécuter les migrations Alembic
    try:
        subprocess.run(["alembic", "upgrade", "heads"], cwd=str(project_root), check=True)
        print("Migrations Alembic exécutées avec succès.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution des migrations Alembic: {e}")
        return False


def create_admin_user(username, password, email=None):
    """Créer un utilisateur administrateur."""
    from sqlalchemy.orm import sessionmaker
    
    # Créer une session
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Vérifier si l'utilisateur existe déjà
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"L'utilisateur '{username}' existe déjà.")
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
        
        print(f"Utilisateur administrateur '{username}' créé avec succès.")
        return True
    except Exception as e:
        db.rollback()
        print(f"Erreur lors de la création de l'utilisateur administrateur: {e}")
        return False
    finally:
        db.close()


def main():
    """Point d'entrée principal."""
    args = parse_arguments()
    
    # Exécuter les migrations Alembic
    if not run_alembic_migrations():
        return 1
    
    # Si l'option --create-admin est activée, créer un utilisateur administrateur
    if args.create_admin:
        if not create_admin_user(args.username, args.password, args.email):
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
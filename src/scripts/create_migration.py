#!/usr/bin/env python3
"""
Script pour créer une nouvelle migration Alembic.
"""
import sys
import os
import argparse
import subprocess
from pathlib import Path

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description="Créer une nouvelle migration Alembic.")
    parser.add_argument(
        "message",
        type=str,
        help="Message de la migration (par exemple: 'Ajout de la table users')"
    )
    parser.add_argument(
        "--autogenerate",
        action="store_true",
        help="Générer automatiquement la migration à partir des modèles"
    )
    return parser.parse_args()


def create_migration(message, autogenerate=False):
    """Créer une nouvelle migration Alembic."""
    print(f"Création d'une nouvelle migration : {message}")
    
    # Chemin vers le répertoire racine du projet
    project_root = Path(__file__).parent.parent.parent
    
    # Construire la commande Alembic
    cmd = ["alembic", "revision"]
    
    if autogenerate:
        cmd.append("--autogenerate")
    
    cmd.extend(["-m", message])
    
    # Exécuter la commande Alembic
    try:
        subprocess.run(cmd, cwd=str(project_root), check=True)
        print("Migration créée avec succès.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la création de la migration : {e}")
        return False


def main():
    """Point d'entrée principal."""
    args = parse_arguments()
    
    # Créer la migration
    if not create_migration(args.message, args.autogenerate):
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
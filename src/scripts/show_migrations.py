#!/usr/bin/env python3
"""
Script pour afficher l'historique des migrations Alembic.
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
    parser = argparse.ArgumentParser(description="Afficher l'historique des migrations Alembic.")
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Afficher des informations détaillées"
    )
    return parser.parse_args()


def show_migrations(verbose=False):
    """Afficher l'historique des migrations Alembic."""
    # Chemin vers le répertoire racine du projet
    project_root = Path(__file__).parent.parent.parent
    
    # Construire la commande Alembic
    cmd = ["alembic", "history"]
    
    if verbose:
        cmd.append("-v")
    
    # Exécuter la commande Alembic
    try:
        subprocess.run(cmd, cwd=str(project_root), check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'affichage de l'historique des migrations : {e}")
        return False


def main():
    """Point d'entrée principal."""
    args = parse_arguments()
    
    # Afficher l'historique des migrations
    if not show_migrations(args.verbose):
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
#!/usr/bin/env python3
"""
Script pour appliquer les migrations Alembic.
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
    parser = argparse.ArgumentParser(description="Appliquer les migrations Alembic.")
    parser.add_argument(
        "--revision",
        type=str,
        default="head",
        help="Révision à appliquer (par défaut: head)"
    )
    parser.add_argument(
        "--downgrade",
        action="store_true",
        help="Rétrograder à une révision précédente"
    )
    return parser.parse_args()


def apply_migrations(revision, downgrade=False):
    """Appliquer les migrations Alembic."""
    # Chemin vers le répertoire racine du projet
    project_root = Path(__file__).parent.parent.parent
    
    # Construire la commande Alembic
    cmd = ["alembic"]
    
    if downgrade:
        cmd.append("downgrade")
    else:
        cmd.append("upgrade")
    
    cmd.append(revision)
    
    # Exécuter la commande Alembic
    try:
        subprocess.run(cmd, cwd=str(project_root), check=True)
        action = "rétrogradation" if downgrade else "mise à jour"
        print(f"Migration {action} effectuée avec succès.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'application des migrations : {e}")
        return False


def main():
    """Point d'entrée principal."""
    args = parse_arguments()
    
    # Appliquer les migrations
    if not apply_migrations(args.revision, args.downgrade):
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
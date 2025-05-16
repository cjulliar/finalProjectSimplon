#!/usr/bin/env python3
"""
Script pour mettre à jour la base de données avec les nouveaux modèles.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.database import engine, Base
from src.db.models import BankData, User, Analysis, Visualization, ScheduledReport


def update_database():
    """Mettre à jour la base de données en créant les tables manquantes."""
    print("Mise à jour de la base de données...")
    
    # Créer les tables qui n'existent pas encore
    Base.metadata.create_all(bind=engine)
    
    print("Base de données mise à jour avec succès.")
    print("Les tables suivantes sont maintenant disponibles :")
    for table in Base.metadata.tables:
        print(f"- {table}")


def main():
    """Point d'entrée principal."""
    update_database()
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
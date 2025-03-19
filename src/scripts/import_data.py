#!/usr/bin/env python3
"""
Script pour importer les données Excel dans la base de données SQLite.
"""
import argparse
import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.etl.excel_import import import_excel_to_db


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description="Importe des données Excel dans la base de données SQLite.")
    parser.add_argument(
        "--file", "-f",
        type=str,
        default=os.path.join("docs", "DonneeBanque.xlsx"),
        help="Chemin vers le fichier Excel à importer (par défaut: docs/DonneeBanque.xlsx)"
    )
    return parser.parse_args()


def main():
    """Point d'entrée principal."""
    args = parse_arguments()
    
    # Chemin absolu du fichier
    file_path = os.path.abspath(args.file)
    
    # Vérifier que le fichier existe
    if not os.path.exists(file_path):
        print(f"Erreur: Le fichier {file_path} n'existe pas.")
        return 1
    
    print(f"Importation du fichier: {file_path}")
    rows_inserted = import_excel_to_db(file_path)
    
    if rows_inserted > 0:
        print(f"Importation réussie: {rows_inserted} lignes insérées.")
        return 0
    else:
        print("Échec de l'importation: aucune ligne insérée.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 
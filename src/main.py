"""
Module principal de l'application.
"""
import argparse
import os
import sys
from pathlib import Path

from src.etl.excel_import import import_excel_to_db
from src.db.database import engine, Base


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description="Application de rapports bancaires.")
    parser.add_argument(
        "--import-excel", "-i",
        action="store_true",
        help="Importer les données du fichier Excel"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        default=os.path.join("docs", "DonneeBanque.xlsx"),
        help="Chemin vers le fichier Excel à importer (par défaut: docs/DonneeBanque.xlsx)"
    )
    return parser.parse_args()


def init_db():
    """Initialise la base de données."""
    Base.metadata.create_all(bind=engine)
    print("Base de données initialisée avec succès.")


def main():
    """Point d'entrée principal."""
    print("=== Application de Rapports Bancaires ===")
    
    # Analyser les arguments
    args = parse_arguments()
    
    # Initialiser la base de données
    init_db()
    
    # Si l'option d'importation est activée
    if args.import_excel:
        # Vérifier que le fichier existe
        file_path = os.path.abspath(args.file)
        if not os.path.exists(file_path):
            print(f"Erreur: Le fichier {file_path} n'existe pas.")
            return 1
        
        print(f"Importation du fichier Excel: {file_path}")
        rows_inserted = import_excel_to_db(file_path)
        
        if rows_inserted > 0:
            print(f"Importation réussie: {rows_inserted} lignes insérées.")
        else:
            print("Échec de l'importation: aucune ligne insérée.")
            return 1
    else:
        print("Pour importer des données, utilisez l'option --import-excel")
    
    print("\nTraitement terminé.")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
#!/usr/bin/env python3
"""
Script pour importer les données du fichier DonneeBanque.xlsx vers la base de données PostgreSQL.
Ce script gère à la fois l'importation des données de la semaine courante et de l'historique.
"""
import os
import sys
import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime
from sqlalchemy import text

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.database import engine, SessionLocal, Base
from src.db.models import BankData, BankDataRaw

# Banques à filtrer pour le développement
FILTERED_BANKS = ["Banque A", "Banque B", "Banque C", "Banque D"]

def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Importe les données du fichier Excel vers la base de données PostgreSQL."
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        default=os.path.join("data", "DonneeBanque.xlsx"),
        help="Chemin vers le fichier Excel à importer (par défaut: data/DonneeBanque.xlsx)"
    )
    parser.add_argument(
        "--sheet", "-s",
        type=str,
        choices=["current", "history", "all"],
        default="all",
        help="Onglet à importer: 'current' pour la semaine courante, 'history' pour l'historique, 'all' pour les deux"
    )
    parser.add_argument(
        "--filter-banks", "-b",
        action="store_true",
        help=f"Filtrer uniquement les banques spécifiées pour le développement: {', '.join(FILTERED_BANKS)}"
    )
    parser.add_argument(
        "--truncate", "-t",
        action="store_true",
        help="Vider les tables avant l'importation"
    )
    return parser.parse_args()

def initialize_database():
    """Initialiser la base de données en créant les tables nécessaires."""
    print("Initialisation de la base de données...")
    Base.metadata.create_all(bind=engine)
    print("Base de données initialisée avec succès.")

def read_excel_file(file_path, sheet_name):
    """
    Lit le fichier Excel et retourne un DataFrame.
    
    Args:
        file_path (str): Chemin vers le fichier Excel
        sheet_name (str): Nom de l'onglet à lire
        
    Returns:
        DataFrame: Données du fichier Excel
    """
    try:
        # Déterminer le nom réel de l'onglet
        if sheet_name == "current":
            sheet = "Donnee Sem Cour"
        elif sheet_name == "history":
            sheet = "Donnee DataSet"
        else:
            raise ValueError(f"Nom d'onglet non valide: {sheet_name}")
        
        # Lire le fichier Excel
        df = pd.read_excel(file_path, sheet_name=sheet)
        print(f"Fichier Excel lu avec succès: {file_path}, onglet: {sheet}")
        print(f"Nombre de lignes: {len(df)}")
        print(f"Colonnes: {', '.join(df.columns)}")
        return df
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier Excel: {e}")
        return None

def filter_banks(df, filter_enabled=False):
    """
    Filtre le DataFrame pour ne garder que les banques spécifiées si le filtre est activé.
    
    Args:
        df (DataFrame): DataFrame à filtrer
        filter_enabled (bool): Si True, applique le filtre
        
    Returns:
        DataFrame: DataFrame filtré
    """
    if filter_enabled:
        filtered_df = df[df['MULTI_SITE'].isin(FILTERED_BANKS)]
        print(f"Données filtrées: {len(filtered_df)} lignes sur {len(df)} (uniquement {', '.join(FILTERED_BANKS)})")
        return filtered_df
    return df

def truncate_tables():
    """Vide les tables avant l'importation."""
    print("Vidage des tables...")
    with engine.connect() as connection:
        connection.execute(text("TRUNCATE TABLE bank_data_raw CASCADE"))
        connection.execute(text("TRUNCATE TABLE bank_data CASCADE"))
        connection.commit()
    print("Tables vidées avec succès.")

def import_to_raw_table(df):
    """
    Importe les données brutes dans la table bank_data_raw.
    
    Args:
        df (DataFrame): DataFrame à importer
        
    Returns:
        int: Nombre de lignes insérées
    """
    try:
        # Utiliser un context manager pour s'assurer que la session est fermée
        with SessionLocal() as db:
            count = 0
            # Traitement par lots pour limiter l'utilisation de la mémoire
            batch_size = 500
            total_rows = len(df)
            
            for i in range(0, total_rows, batch_size):
                batch_df = df.iloc[i:min(i+batch_size, total_rows)]
                
                # Convertir le DataFrame en liste de dictionnaires
                records = batch_df.to_dict(orient='records')
                
                # Insérer les enregistrements dans la base de données
                for record in records:
                    # Créer un nouvel objet BankDataRaw
                    bank_data_raw = BankDataRaw(
                        week_id=str(record['ID_SEM_COMM']),
                        group_name=record['GROUPE'],
                        bank_name=record['MULTI_SITE'],
                        raw_data=record,
                        created_at=datetime.now()
                    )
                    db.add(bank_data_raw)
                    count += 1
                
                # Commit par lot
                db.commit()
                print(f"Importation en cours: {min(i+batch_size, total_rows)}/{total_rows} lignes")
            
            print(f"Données brutes importées avec succès: {count} lignes")
            return count
    except Exception as e:
        print(f"Erreur lors de l'importation des données brutes: {e}")
        return 0

def transform_to_bank_data(df):
    """
    Transforme les données brutes en données structurées pour la table bank_data.
    
    Args:
        df (DataFrame): DataFrame avec les données brutes
        
    Returns:
        int: Nombre de lignes insérées
    """
    try:
        # Utiliser un context manager pour s'assurer que la session est fermée
        with SessionLocal() as db:
            count = 0
            # Traitement par lots pour limiter l'utilisation de la mémoire
            batch_size = 500
            total_rows = len(df)
            
            for i in range(0, total_rows, batch_size):
                batch_df = df.iloc[i:min(i+batch_size, total_rows)]
                
                # Convertir le DataFrame en liste de dictionnaires
                records = batch_df.to_dict(orient='records')
                
                # Insérer les enregistrements dans la base de données
                for record in records:
                    # Extraire la date à partir de l'ID de semaine (format YYYYWW)
                    week_id = str(record['ID_SEM_COMM'])
                    year = int(week_id[:4])
                    week = int(week_id[4:])
                    
                    # Convertir la semaine en date approximative (premier jour de la semaine)
                    from datetime import datetime, timedelta
                    date_obj = datetime.strptime(f'{year}-W{week}-1', '%Y-W%W-%w').date()
                    
                    # Calculer le montant total (SOMME_PART + SOMME_PRO)
                    montant_total = 0
                    if 'SOMME_PART' in record and pd.notna(record['SOMME_PART']):
                        montant_total += record['SOMME_PART']
                    if 'SOMME_PRO' in record and pd.notna(record['SOMME_PRO']):
                        montant_total += record['SOMME_PRO']
                    
                    # Calculer le nombre total de transactions (OCC_PART + OCC_PRO)
                    transactions_total = 0
                    if 'OCC_PART' in record and pd.notna(record['OCC_PART']):
                        transactions_total += record['OCC_PART']
                    if 'OCC_PRO' in record and pd.notna(record['OCC_PRO']):
                        transactions_total += record['OCC_PRO']
                    
                    # Créer un nouvel objet BankData
                    bank_data = BankData(
                        agence=record['MULTI_SITE'],
                        date=date_obj,
                        montant=montant_total,
                        nombre_transactions=transactions_total,
                        created_at=datetime.now()
                    )
                    db.add(bank_data)
                    count += 1
                
                # Commit par lot
                db.commit()
                print(f"Transformation en cours: {min(i+batch_size, total_rows)}/{total_rows} lignes")
            
            print(f"Données transformées et importées avec succès: {count} lignes")
            return count
    except Exception as e:
        print(f"Erreur lors de la transformation des données: {e}")
        return 0

def main():
    """Point d'entrée principal."""
    args = parse_arguments()
    
    # Vérifier que le fichier existe
    file_path = os.path.abspath(args.file)
    if not os.path.exists(file_path):
        print(f"Erreur: Le fichier {file_path} n'existe pas.")
        return 1
    
    # Initialiser la base de données
    initialize_database()
    
    # Vider les tables si demandé
    if args.truncate:
        truncate_tables()
    
    # Déterminer les onglets à importer
    sheets_to_import = []
    if args.sheet == "current" or args.sheet == "all":
        sheets_to_import.append("current")
    if args.sheet == "history" or args.sheet == "all":
        sheets_to_import.append("history")
    
    total_rows_imported = 0
    
    # Importer chaque onglet
    for sheet in sheets_to_import:
        print(f"\nImportation de l'onglet {sheet}...")
        df = read_excel_file(file_path, sheet)
        
        if df is not None:
            # Filtrer les banques si demandé
            df = filter_banks(df, args.filter_banks)
            
            # Importer les données brutes
            raw_rows = import_to_raw_table(df)
            
            # Transformer et importer les données structurées
            structured_rows = transform_to_bank_data(df)
            
            total_rows_imported += structured_rows
    
    print(f"\nImportation terminée: {total_rows_imported} lignes au total")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
"""
Module d'importation des données Excel vers la base de données SQLite.
"""
import os
import pandas as pd
from pathlib import Path
from datetime import datetime, date
from sqlalchemy.orm import Session

from src.db.database import SessionLocal, engine
from src.db.models import Base, BankData


def initialize_database():
    """Initialise la base de données."""
    Base.metadata.create_all(bind=engine)
    print("Base de données initialisée")


def read_excel_file(file_path):
    """
    Lit le fichier Excel et retourne un DataFrame.
    
    Args:
        file_path (str): Chemin vers le fichier Excel
        
    Returns:
        DataFrame: Données du fichier Excel
    """
    try:
        df = pd.read_excel(file_path)
        print(f"Fichier Excel lu avec succès: {file_path}")
        print(f"Nombre de lignes: {len(df)}")
        print(f"Colonnes: {', '.join(df.columns)}")
        return df
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier Excel: {e}")
        return None


def clean_data(df):
    """
    Nettoie et prépare les données.
    
    Args:
        df (DataFrame): DataFrame à nettoyer
        
    Returns:
        DataFrame: DataFrame nettoyé
    """
    if df is None:
        return None
        
    # Structure spécifique pour le fichier DonneeBanque.xlsx
    if 'ID_SEM_COMM' in df.columns and 'GROUPE' in df.columns:
        print("Structure détectée: DonneeBanque.xlsx")
        
        # Création du DataFrame avec les colonnes requises
        result_df = pd.DataFrame()
        
        # Utiliser GROUPE comme agence
        if 'GROUPE' in df.columns:
            result_df['agence'] = df['GROUPE']
        
        # Création d'une date basée sur ID_SEM_COMM
        if 'ID_SEM_COMM' in df.columns:
            # Générer un DataFrame avec des dates
            # Utiliser le 1er janvier 2023 comme date de départ et ajouter un jour à chaque ligne
            # Cette logique peut être adaptée selon le format réel de ID_SEM_COMM
            start_date = pd.Timestamp('2023-01-01')
            dates = [start_date + pd.Timedelta(days=i) for i in range(len(df))]
            result_df['date'] = [d.date() for d in dates]
            
        # Montant total = somme de SOMME_PART et SOMME_PRO
        montant_total = pd.Series(0, index=df.index)
        if 'SOMME_PART' in df.columns:
            montant_total += df['SOMME_PART'].fillna(0)
        if 'SOMME_PRO' in df.columns:
            montant_total += df['SOMME_PRO'].fillna(0)
        if 'SOMME_RANG' in df.columns:
            montant_total += df['SOMME_RANG'].fillna(0)
        
        result_df['montant'] = montant_total
        
        # Nombre de transactions = OCC_PART + OCC_PRO
        transactions_total = pd.Series(0, index=df.index)
        if 'OCC_PART' in df.columns:
            transactions_total += df['OCC_PART'].fillna(0)
        if 'OCC_PRO' in df.columns:
            transactions_total += df['OCC_PRO'].fillna(0)
        
        result_df['nombre_transactions'] = transactions_total.astype(int)
        
        print("Données adaptées pour le format spécifique")
        print(f"Nombre de lignes après adaptation: {len(result_df)}")
        return result_df
    
    # Vérification de la présence des colonnes requises pour le cas général
    required_columns = ['agence', 'date', 'montant', 'nombre_transactions']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"Colonnes manquantes: {', '.join(missing_columns)}")
        # Tentative de mappage de colonnes si les noms ne correspondent pas exactement
        column_mapping = {}
        for col in df.columns:
            if 'agence' in col.lower():
                column_mapping[col] = 'agence'
            elif 'date' in col.lower():
                column_mapping[col] = 'date'
            elif 'montant' in col.lower() or 'somme' in col.lower():
                column_mapping[col] = 'montant'
            elif 'transaction' in col.lower() or 'nombre' in col.lower():
                column_mapping[col] = 'nombre_transactions'
        
        if column_mapping:
            df = df.rename(columns=column_mapping)
            print(f"Colonnes renommées: {column_mapping}")
            
            # Vérifier à nouveau les colonnes manquantes
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"Impossible de trouver les colonnes requises: {', '.join(missing_columns)}")
                return None
        else:
            return None
    
    # Conversion des types de données
    try:
        # Conversion de la colonne date
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.date
        
        # Conversion des valeurs numériques
        if 'montant' in df.columns:
            df['montant'] = pd.to_numeric(df['montant'], errors='coerce')
        
        if 'nombre_transactions' in df.columns:
            df['nombre_transactions'] = pd.to_numeric(df['nombre_transactions'], errors='coerce').astype(int)
        
        # Suppression des lignes avec des valeurs manquantes
        df = df.dropna(subset=required_columns)
        
        print("Données nettoyées avec succès")
        print(f"Nombre de lignes après nettoyage: {len(df)}")
        return df
    except Exception as e:
        print(f"Erreur lors du nettoyage des données: {e}")
        return None


def insert_data_to_db(df):
    """
    Insère les données du DataFrame dans la base de données.
    
    Args:
        df (DataFrame): DataFrame à insérer
        
    Returns:
        int: Nombre de lignes insérées
    """
    if df is None:
        return 0
    
    try:
        # Utiliser un context manager pour s'assurer que la session est fermée
        with SessionLocal() as db:
            count = 0
            # Traitement par lots pour limiter l'utilisation de la mémoire
            batch_size = 1000
            total_rows = len(df)
            
            for i in range(0, total_rows, batch_size):
                batch_df = df.iloc[i:min(i+batch_size, total_rows)]
                
                # Convertir le DataFrame en liste de dictionnaires
                records = batch_df.to_dict(orient='records')
                
                # Insérer les enregistrements dans la base de données
                for record in records:
                    # Créer un nouvel objet BankData
                    bank_data = BankData(
                        agence=record['agence'],
                        date=record['date'],
                        montant=record['montant'],
                        nombre_transactions=record['nombre_transactions']
                    )
                    db.add(bank_data)
                    count += 1
                
                # Commit par lot
                db.commit()
                print(f"Insertion en cours: {min(i+batch_size, total_rows)}/{total_rows}")
            
            print(f"Données insérées avec succès: {count} lignes")
            return count
    except Exception as e:
        print(f"Erreur lors de l'insertion des données: {e}")
        return 0


def import_excel_to_db(file_path):
    """
    Importe les données du fichier Excel dans la base de données.
    
    Args:
        file_path (str): Chemin vers le fichier Excel
        
    Returns:
        int: Nombre de lignes insérées
    """
    # S'assurer que la base de données est initialisée
    initialize_database()
    
    # Lire le fichier Excel
    df = read_excel_file(file_path)
    
    # Nettoyer les données
    df = clean_data(df)
    
    # Insérer les données dans la base de données
    return insert_data_to_db(df)


def main():
    """Point d'entrée principal."""
    # Chemin du fichier Excel (relatif ou absolu)
    excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'docs', 'DonneeBanque.xlsx')
    
    # Importer les données
    rows_inserted = import_excel_to_db(excel_path)
    
    print(f"Importation terminée: {rows_inserted} lignes insérées")


if __name__ == "__main__":
    main() 
"""
Tests pour le module d'importation Excel.
"""
import os
import sys
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date
import tempfile
from unittest.mock import patch

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.etl.excel_import import read_excel_file, clean_data, insert_data_to_db, import_excel_to_db
from src.db.database import engine, Base, SessionLocal
from src.db.models import BankData


@pytest.fixture(scope="function")
def setup_test_db():
    """Configure une base de données de test temporaire."""
    # Créer les tables dans la base de données
    Base.metadata.create_all(bind=engine)
    
    # Fournir une session de base de données
    db = SessionLocal()
    
    try:
        yield db
    finally:
        # Nettoyer après le test
        db.close()
        # Supprimer toutes les tables
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_dataframe():
    """Crée un DataFrame de test."""
    data = {
        'agence': ['Agence1', 'Agence2', 'Agence3'],
        'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'montant': [1000.50, 2500.75, 750.25],
        'nombre_transactions': [5, 10, 3]
    }
    return pd.DataFrame(data)


@pytest.fixture
def temp_excel_file(tmp_path, sample_dataframe):
    """Crée un fichier Excel temporaire pour les tests."""
    file_path = tmp_path / "test_data.xlsx"
    sample_dataframe.to_excel(file_path, index=False)
    return file_path


def test_read_excel_file(temp_excel_file):
    """Teste la lecture d'un fichier Excel."""
    # Lire le fichier Excel
    df = read_excel_file(temp_excel_file)
    
    # Vérifications
    assert df is not None
    assert len(df) == 3
    assert set(df.columns) == set(['agence', 'date', 'montant', 'nombre_transactions'])


def test_read_excel_file_nonexistent():
    """Teste la lecture d'un fichier Excel inexistant."""
    # Tenter de lire un fichier inexistant
    df = read_excel_file("fichier_inexistant.xlsx")
    
    # Vérification
    assert df is None


def test_clean_data(sample_dataframe):
    """Teste le nettoyage des données."""
    # Nettoyer les données
    df_cleaned = clean_data(sample_dataframe)
    
    # Vérifications
    assert df_cleaned is not None
    assert len(df_cleaned) == 3
    assert isinstance(df_cleaned['date'].iloc[0], date)
    assert isinstance(df_cleaned['montant'].iloc[0], float)
    
    # Vérifier que nombre_transactions est soit un int, soit un numpy.int64
    value = df_cleaned['nombre_transactions'].iloc[0]
    assert isinstance(value, (int, np.int64, np.int32, np.int16, np.int8)), f"Type attendu: int, type actuel: {type(value)}"


def test_clean_data_missing_columns():
    """Teste le nettoyage des données avec des colonnes manquantes."""
    # Créer un DataFrame avec des colonnes manquantes
    df = pd.DataFrame({
        'agence': ['Agence1'],
        'date': ['2023-01-01']
    })
    
    # Nettoyer les données
    df_cleaned = clean_data(df)
    
    # Vérification
    assert df_cleaned is None


def test_insert_data_to_db(setup_test_db, sample_dataframe):
    """Teste l'insertion des données dans la base de données."""
    # Nettoyer les données avant l'insertion
    df_cleaned = clean_data(sample_dataframe)
    
    # Insérer les données
    count = insert_data_to_db(df_cleaned)
    
    # Vérifications
    assert count == 3
    
    # Vérifier que les données sont bien dans la base
    with SessionLocal() as db:
        bank_data = db.query(BankData).all()
        assert len(bank_data) == 3
        assert bank_data[0].agence == 'Agence1'
        assert bank_data[0].montant == 1000.50
        assert bank_data[0].nombre_transactions == 5


@pytest.fixture(scope="function")
def create_test_excel():
    """Créer un fichier Excel temporaire avec des données de test."""
    # Créer un fichier temporaire
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tf:
        # Créer un DataFrame test
        data = {
            'agence': ['Agence A', 'Agence B', 'Agence C'],
            'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'montant': [1000, 2000, 3000],
            'nombre_transactions': [10, 20, 30]
        }
        df = pd.DataFrame(data)
        
        # Enregistrer le DataFrame dans le fichier Excel
        df.to_excel(tf.name, index=False)
        
        excel_path = tf.name
    
    yield excel_path
    
    # Supprimer le fichier temporaire
    os.unlink(excel_path)


def test_import_excel_to_db(create_test_excel):
    """Tester l'importation d'un fichier Excel dans la base de données."""
    excel_path = create_test_excel
    
    # Vérifier que le fichier Excel existe
    assert os.path.exists(excel_path), f"Le fichier Excel n'existe pas: {excel_path}"
    
    # Utiliser un mock pour la session de base de données
    with patch('src.etl.excel_import.SessionLocal') as mock_session:
        # Configurer le mock
        mock_db = mock_session.return_value.__enter__.return_value
        
        # Importer les données
        count = import_excel_to_db(excel_path)
        
        # Vérifier que l'importation a réussi
        assert count > 0, "L'importation a échoué"
        
        # Vérifier que la fonction d'insertion a été appelée
        assert mock_db.add.call_count > 0, "Aucune donnée n'a été ajoutée à la base de données"
        assert mock_db.commit.call_count > 0, "Les données n'ont pas été validées dans la base de données"


def test_import_excel_to_db_with_errors():
    """Tester l'importation avec des erreurs."""
    # Tester avec un fichier inexistant
    non_existent_file = "fichier_inexistant.xlsx"
    count = import_excel_to_db(non_existent_file)
    assert count == 0, "L'importation devrait échouer avec un fichier inexistant"
    
    # Tester avec un fichier invalide
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tf:
        tf.write(b"Ceci n'est pas un fichier Excel")
        invalid_file = tf.name
    
    try:
        count = import_excel_to_db(invalid_file)
        assert count == 0, "L'importation devrait échouer avec un fichier non Excel"
    finally:
        os.unlink(invalid_file)


def test_import_excel_to_db_with_invalid_data():
    """Tester l'importation avec des données invalides."""
    # Créer un fichier Excel avec des données invalides
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tf:
        # DataFrame avec des colonnes manquantes
        data = {
            'agence': ['Agence A', 'Agence B', 'Agence C'],
            # Colonne 'date' manquante
            'montant': [1000, 2000, 3000],
            # Colonne 'nombre_transactions' manquante
        }
        df = pd.DataFrame(data)
        df.to_excel(tf.name, index=False)
        
        invalid_data_file = tf.name
    
    try:
        count = import_excel_to_db(invalid_data_file)
        assert count == 0, "L'importation devrait échouer avec des données invalides"
    finally:
        os.unlink(invalid_data_file)


def test_import_excel_to_db_with_duplicates(create_test_excel):
    """Tester l'importation avec des données en doublon."""
    excel_path = create_test_excel
    
    # Utiliser un patch pour la session de base de données
    with patch('src.etl.excel_import.SessionLocal') as mock_session:
        # Configurer le mock
        mock_db = mock_session.return_value.__enter__.return_value
        
        # Première importation
        count1 = import_excel_to_db(excel_path)
        assert count1 > 0, "La première importation a échoué"
        
        # Deuxième importation (même fichier)
        count2 = import_excel_to_db(excel_path)
        assert count2 > 0, "La deuxième importation a échoué"
        
        # Vérifier que les deux importations ont fonctionné
        total_count = count1 + count2
        assert total_count > count1, "La deuxième importation n'a pas ajouté de données"


def test_import_excel_to_db_real_file():
    """
    Teste l'importation du fichier Excel réel.
    
    Note: Ce test est conditionné par l'existence du fichier DonneeBanque.xlsx
    """
    # Chemin du fichier Excel réel
    file_path = os.path.join('docs', 'DonneeBanque.xlsx')
    
    # Ne lancer le test que si le fichier existe
    if os.path.exists(file_path):
        # Lire le fichier pour obtenir le nombre de lignes attendues
        try:
            df = pd.read_excel(file_path)
            expected_rows = len(df)
            
            # Si le fichier est vide, skip le test
            if expected_rows == 0:
                pytest.skip("Le fichier Excel est vide.")
                
            # Vérifier que le DataFrame a les colonnes requises ou peut être adapté
            required_columns = ['agence', 'date', 'montant', 'nombre_transactions']
            has_required_cols = all(col in df.columns for col in required_columns)
            can_be_mapped = any('agence' in col.lower() for col in df.columns) and \
                            any('date' in col.lower() for col in df.columns) and \
                            any('montant' in col.lower() or 'somme' in col.lower() for col in df.columns) and \
                            any('transaction' in col.lower() or 'nombre' in col.lower() for col in df.columns)
            
            if not (has_required_cols or can_be_mapped):
                pytest.skip("Le fichier Excel n'a pas le format attendu.")
            
        except Exception as e:
            pytest.skip(f"Erreur lors de la lecture du fichier Excel: {e}")
            
        # Ne pas modifier la base de données réelle dans ce test
        pytest.skip("Test avec fichier réel désactivé pour éviter de modifier la base de données.")
    else:
        pytest.skip("Le fichier docs/DonneeBanque.xlsx n'existe pas.") 
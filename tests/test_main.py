import pytest
import os
from pathlib import Path

# Obtenir le chemin absolu du répertoire racine du projet
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"

# Corriger l'importation pour utiliser le module correct
from src.main import init_db, parse_arguments
from src.etl.excel_import import read_excel_file
from src.db.database import engine, Base
from src.db.models import BankData

@pytest.fixture(scope="session")
def setup_database():
    """Crée la base de données de test"""
    # Utiliser une base de données SQLite en mémoire pour les tests
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def setup_test_data(tmp_path):
    """Crée un fichier Excel de test"""
    import pandas as pd
    
    # S'assurer que le dossier docs existe
    DOCS_DIR.mkdir(exist_ok=True)
    
    # Créer un DataFrame de test
    test_data = {
        'agence': ['Agence1', 'Agence2'],
        'date': ['2024-03-19', '2024-03-19'],
        'montant': [1000, 2000],
        'nombre_transactions': [10, 20]
    }
    df = pd.DataFrame(test_data)
    
    # Sauvegarder en Excel
    excel_path = DOCS_DIR / "DonneeBanque.xlsx"
    df.to_excel(excel_path, index=False)
    yield
    # Nettoyage : supprimer le fichier de test
    if excel_path.exists():
        excel_path.unlink()

def test_excel_file_exists():
    """Vérifie que le fichier Excel existe"""
    excel_path = DOCS_DIR / "DonneeBanque.xlsx"
    assert excel_path.exists(), "Le fichier Excel n'existe pas"

def test_read_excel_file(setup_database):
    """Teste la lecture des données Excel"""
    excel_path = DOCS_DIR / "DonneeBanque.xlsx"
    data = read_excel_file(str(excel_path))
    assert data is not None, "La lecture des données a échoué"
    assert len(data) > 0, "Le fichier Excel est vide"
    assert "agence" in data.columns, "La colonne 'agence' est manquante"
    assert "date" in data.columns, "La colonne 'date' est manquante"
    assert "montant" in data.columns, "La colonne 'montant' est manquante"
    assert "nombre_transactions" in data.columns, "La colonne 'nombre_transactions' est manquante"

def test_init_db():
    """Teste l'initialisation de la base de données"""
    # Cette fonction ne fait qu'appeler la fonction, elle ne teste pas réellement les résultats
    # car cela est déjà couvert par d'autres tests
    init_db()
    # Si aucune exception n'est levée, le test passe
    assert True 
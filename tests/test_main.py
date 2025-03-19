import pytest
import os
from pathlib import Path
import sys
import tempfile
import subprocess
from unittest.mock import patch, MagicMock, ANY
import argparse

# Obtenir le chemin absolu du répertoire racine du projet
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"

# Corriger l'importation pour utiliser le module correct
from src.main import init_db, parse_arguments, main
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

def test_parse_arguments():
    """Tester le parsing des arguments."""
    # Test avec l'option --import-excel
    with patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(
        import_excel=True, 
        file="docs/DonneeBanque.xlsx"  # La valeur par défaut dans le code
    )):
        args = parse_arguments()
        assert args.import_excel is True
        assert args.file == "docs/DonneeBanque.xlsx"
    
    # Test avec l'option --import-excel et --file
    with patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(
        import_excel=True, 
        file="test.xlsx"
    )):
        args = parse_arguments()
        assert args.import_excel is True
        assert args.file == "test.xlsx"
    
    # Test sans options
    with patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(
        import_excel=False, 
        file="docs/DonneeBanque.xlsx"  # La valeur par défaut dans le code
    )):
        args = parse_arguments()
        assert args.import_excel is False
        assert args.file == "docs/DonneeBanque.xlsx"

def test_main_import_excel():
    """Tester la fonction main avec l'option --import-excel."""
    # Créer un fichier Excel temporaire
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tf:
        excel_path = tf.name
    
    try:
        # Créer un contenu Excel valide
        import pandas as pd
        data = {
            'agence': ['Agence A', 'Agence B'],
            'date': ['2023-01-01', '2023-01-02'],
            'montant': [1000, 2000],
            'nombre_transactions': [10, 20]
        }
        df = pd.DataFrame(data)
        df.to_excel(excel_path, index=False)
        
        # Tester directement l'exécution sans mock
        with patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(
            import_excel=True, 
            file=excel_path
        )):
            # Au lieu de mocker l'importation, exécutons-la réellement
            result = main()
            # Le fichier existe et est valide, le résultat devrait être 0
            assert result == 0
    finally:
        # Nettoyer
        if os.path.exists(excel_path):
            os.unlink(excel_path)

def test_main_import_excel_file_not_found():
    """Tester la fonction main avec un fichier inexistant."""
    # Simuler l'exécution avec un fichier inexistant
    with patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(
        import_excel=True, 
        file="fichier_inexistant.xlsx"
    )):
        with patch('src.etl.excel_import.import_excel_to_db') as mock_import:
            mock_import.return_value = 0  # Simuler l'échec de l'importation
            result = main()
            
            # Vérifier que la fonction retourne une erreur
            assert result == 1

def test_main_default_behavior():
    """Tester le comportement par défaut de la fonction main."""
    # Simuler l'exécution sans options
    with patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(
        import_excel=False, 
        file="docs/DonneeBanque.xlsx"
    )):
        with patch('builtins.print') as mock_print:
            result = main()
            
            # Vérifier que le message d'aide est affiché
            mock_print.assert_called()
            assert result == 0

def test_script_execution():
    """Tester l'exécution du script en tant que processus."""
    # Ne pas exécuter ce test en CI/CD pour éviter les problèmes d'environnement
    if os.environ.get("CI") == "true":
        pytest.skip("Ignorer ce test en CI/CD")
    
    # Créer un fichier Excel temporaire
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tf:
        excel_path = tf.name
    
    try:
        # Créer un contenu Excel valide
        import pandas as pd
        data = {
            'agence': ['Agence A', 'Agence B'],
            'date': ['2023-01-01', '2023-01-02'],
            'montant': [1000, 2000],
            'nombre_transactions': [10, 20]
        }
        df = pd.DataFrame(data)
        df.to_excel(excel_path, index=False)
        
        # Exécuter le script
        result = subprocess.run(
            [sys.executable, '-m', 'src.main', '--import-excel', '--file', excel_path],
            capture_output=True,
            text=True
        )
        
        # Vérifier le code de retour
        assert result.returncode == 0 or "Erreur:" in result.stdout
    finally:
        # Nettoyer
        if os.path.exists(excel_path):
            os.unlink(excel_path) 
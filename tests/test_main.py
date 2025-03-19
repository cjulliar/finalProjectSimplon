import pytest
from pathlib import Path
from src.main import read_excel_data
from src.db.database import engine, Base
from src.db.models import BankData

@pytest.fixture(scope="session")
def setup_database():
    """Crée la base de données de test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_excel_file_exists():
    """Vérifie que le fichier Excel existe"""
    excel_path = Path("docs/DonneeBanque.xlsx")
    assert excel_path.exists(), "Le fichier Excel n'existe pas"

def test_read_excel_data():
    """Teste la lecture des données Excel"""
    data = read_excel_data()
    assert data is not None, "La lecture des données a échoué"
    assert len(data) > 0, "Le fichier Excel est vide"
    assert "agence" in data.columns, "La colonne 'agence' est manquante"
    assert "date" in data.columns, "La colonne 'date' est manquante" 
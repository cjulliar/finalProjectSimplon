"""
Tests pour vérifier l'environnement d'exécution.
"""
import os
import sys
import pytest
from pathlib import Path

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.database import engine, Base, SessionLocal
from src.utils.environment import check_environment, check_files_existence


def test_python_version():
    """Tester la version de Python."""
    import platform
    version = tuple(map(int, platform.python_version_tuple()))
    assert version >= (3, 10), "Python 3.10 ou supérieur est requis"


def test_required_packages():
    """Tester que les packages requis sont installés."""
    required_packages = [
        "sqlalchemy",
        "fastapi",
        "pydantic",
        "pytest",
        "pandas",
    ]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            pytest.fail(f"Le package {package} n'est pas installé")


def test_database_connection():
    """Tester la connexion à la base de données."""
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    
    # Vérifier que la connexion fonctionne
    db = SessionLocal()
    assert db is not None, "La connexion à la base de données a échoué"
    db.close()
    
    # Nettoyer
    Base.metadata.drop_all(bind=engine)


def test_environment_check():
    """Tester la fonction de vérification de l'environnement."""
    env_report = check_environment()
    assert env_report is not None
    assert "python_version" in env_report
    assert "platform" in env_report
    assert "sqlite_version" in env_report
    assert "working_directory" in env_report


def test_files_existence():
    """Tester la fonction de vérification de l'existence des fichiers."""
    files_report = check_files_existence()
    assert files_report is not None
    
    # Vérifier que les fichiers essentiels existent
    essential_files = [
        "requirements.txt",
        "src/main.py",
        "src/db/database.py",
        "src/db/models.py",
    ]
    
    for file_path in essential_files:
        assert files_report[file_path], f"Le fichier {file_path} n'existe pas"


def test_docs_directory():
    """Tester que le répertoire docs existe."""
    docs_dir = Path(__file__).parent.parent / "docs"
    assert docs_dir.exists(), "Le répertoire docs n'existe pas"
    assert docs_dir.is_dir(), "docs n'est pas un répertoire" 
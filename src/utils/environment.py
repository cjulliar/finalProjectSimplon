"""
Utilitaires pour vérifier l'environnement d'exécution.
"""
import os
import sys
import platform
import sqlite3
import importlib.util
from pathlib import Path


def check_environment():
    """
    Vérifier l'environnement d'exécution et retourner un rapport.
    
    Returns:
        dict: Un dictionnaire contenant des informations sur l'environnement.
    """
    env_info = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "sqlite_version": sqlite3.sqlite_version,
        "working_directory": os.getcwd(),
        "modules": {},
        "environment_variables": {}
    }
    
    # Vérifier les modules clés
    for module_name in ["sqlalchemy", "fastapi", "pydantic", "pytest", "pandas"]:
        spec = importlib.util.find_spec(module_name)
        if spec is not None:
            module = importlib.import_module(module_name)
            version = getattr(module, "__version__", "Version inconnue")
            env_info["modules"][module_name] = version
        else:
            env_info["modules"][module_name] = None
    
    # Vérifier les variables d'environnement pertinentes
    for env_var in ["PYTHONPATH", "DATABASE_URL", "LOG_LEVEL", "ENV"]:
        env_info["environment_variables"][env_var] = os.environ.get(env_var)
    
    return env_info


def check_files_existence():
    """
    Vérifier l'existence des fichiers essentiels pour l'application.
    
    Returns:
        dict: Un dictionnaire indiquant si chaque fichier existe.
    """
    base_dir = Path(__file__).parent.parent.parent
    
    essential_files = [
        "requirements.txt",
        "src/main.py",
        "src/db/database.py",
        "src/db/models.py",
        "src/api/routes.py",
        "src/api/auth.py",
        "src/etl/excel_import.py",
        "docs/DonneeBanque.xlsx",
        "tests/test_database.py",
        "tests/test_api.py",
    ]
    
    files_report = {}
    
    for file_path in essential_files:
        full_path = base_dir / file_path
        files_report[file_path] = full_path.exists()
    
    return files_report


def prepare_environment():
    """
    Préparer l'environnement pour l'exécution de l'application.
    
    Returns:
        bool: True si l'environnement est correctement préparé.
    """
    # Ajouter le répertoire racine au chemin Python
    base_dir = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(base_dir))
    
    # Créer des répertoires s'ils n'existent pas
    for directory in ["logs", "data"]:
        dir_path = base_dir / directory
        if not dir_path.exists():
            dir_path.mkdir()
    
    return True


def print_environment_report():
    """Affiche un rapport sur l'environnement d'exécution."""
    env_report = check_environment()
    files_report = check_files_existence()
    
    print("=== Rapport d'environnement ===")
    print(f"Python: {env_report['python_version']}")
    print(f"Plateforme: {env_report['platform']}")
    print(f"SQLite: {env_report['sqlite_version']}")
    print(f"Répertoire de travail: {env_report['working_directory']}")
    
    print("\n=== Vérification des fichiers ===")
    for file_path, exists in files_report.items():
        status = "✓" if exists else "✗"
        print(f"{status} {file_path}")
    
    return env_report, files_report


if __name__ == "__main__":
    print_environment_report() 
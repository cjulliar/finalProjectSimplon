"""
Utilitaire pour tester l'environnement d'exécution.
"""
import os
import sys
import platform
import sqlite3
from pathlib import Path


def check_environment():
    """Vérifie l'environnement d'exécution et retourne un rapport."""
    report = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "environment_variables": {k: v for k, v in os.environ.items() if not k.startswith("_")},
        "working_directory": os.getcwd(),
        "sqlite_version": sqlite3.sqlite_version,
        "path": sys.path,
    }
    return report


def check_files_existence():
    """Vérifie l'existence des fichiers importants."""
    root_dir = Path(__file__).parent.parent.parent
    required_files = [
        "requirements.txt",
        "setup.py",
        "docker-compose.yml",
        "src/main.py",
        "src/db/database.py",
        "src/db/models.py",
    ]
    
    report = {}
    for file_path in required_files:
        full_path = root_dir / file_path
        report[file_path] = full_path.exists()
    
    return report


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
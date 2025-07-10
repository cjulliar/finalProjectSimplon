#!/usr/bin/env python3
"""
Script de test complet pour validation CI/CD
Teste tous les composants critiques du système bancaire intelligent
"""

import os
import sys
import sqlite3
import requests
import subprocess
from datetime import datetime
from pathlib import Path

def print_header(title):
    """Affiche un en-tête formaté"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_section(title):
    """Affiche une section formatée"""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")

def test_file_structure():
    """Test de la structure des fichiers"""
    print_section("📁 Structure des Fichiers")
    
    required_files = [
        'README.md',
        'requirements.txt',
        'docker-compose.yml',
        'src/main.py',
        'frontend/manage.py',
        'tests/__init__.py'
    ]
    
    required_dirs = [
        'src',
        'frontend',
        'tests',
        'docs',
        'docker'
    ]
    
    score = 0
    total = len(required_files) + len(required_dirs)
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
            score += 1
        else:
            print(f"❌ {file_path} - MANQUANT")
    
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"✅ {dir_path}/")
            score += 1
        else:
            print(f"❌ {dir_path}/ - MANQUANT")
    
    return score, total

def test_database():
    """Test de la base de données"""
    print_section("🗄️ Base de Données")
    
    score = 0
    total = 3
    
    # Test existence base SQLite
    if os.path.exists('bankreports.db'):
        print("✅ Base SQLite principale existe")
        score += 1
        
        # Test connexion et tables
        try:
            conn = sqlite3.connect('bankreports.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['bank_data_enriched', 'users', 'scheduled_reports']
            found_tables = [t for t in required_tables if t in tables]
            
            if len(found_tables) >= 2:
                print(f"✅ Tables trouvées: {found_tables}")
                score += 1
            else:
                print(f"❌ Tables manquantes. Trouvées: {tables}")
                
            # Test données
            cursor.execute("SELECT COUNT(*) FROM bank_data_enriched")
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"✅ Données présentes: {count} enregistrements")
                score += 1
            else:
                print("❌ Aucune donnée dans bank_data_enriched")
                
            conn.close()
        except Exception as e:
            print(f"❌ Erreur base de données: {e}")
    else:
        print("❌ Base SQLite principale manquante")
    
    return score, total

def test_python_environment():
    """Test de l'environnement Python"""
    print_section("🐍 Environnement Python")
    
    score = 0
    total = 4
    
    # Version Python
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 10:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        score += 1
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor} - Version 3.10+ requise")
    
    # Dépendances critiques
    critical_packages = ['fastapi', 'django', 'sqlalchemy', 'pandas']
    for package in critical_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
            score += 1
        except ImportError:
            print(f"❌ {package} - MANQUANT")
    
    return score, total

def test_frontend():
    """Test du frontend Django"""
    print_section("🌐 Frontend Django")
    
    score = 0
    total = 3
    
    # Test template home.html
    template_path = 'frontend/templates/dashboard/home.html'
    if os.path.exists(template_path):
        print("✅ Template home.html existe")
        score += 1
    else:
        print("❌ Template home.html manquant")
    
    # Test manage.py
    manage_path = 'frontend/manage.py'
    if os.path.exists(manage_path):
        print("✅ manage.py existe")
        score += 1
    else:
        print("❌ manage.py manquant")
    
    # Test settings.py
    settings_path = 'frontend/frontend/settings.py'
    if os.path.exists(settings_path):
        print("✅ settings.py existe")
        score += 1
    else:
        print("❌ settings.py manquant")
    
    return score, total

def test_api():
    """Test de l'API FastAPI"""
    print_section("🔌 API FastAPI")
    
    score = 0
    total = 3
    
    # Test main.py
    api_main_path = 'src/api/main.py'
    if os.path.exists(api_main_path):
        print("✅ main.py API existe")
        score += 1
    else:
        print("❌ main.py API manquant")
    
    # Test routes
    routes_path = 'src/api/routes.py'
    if os.path.exists(routes_path):
        print("✅ routes.py existe")
        score += 1
    else:
        print("❌ routes.py manquant")
    
    # Test models
    models_path = 'src/api/models.py'
    if os.path.exists(models_path):
        print("✅ models.py existe")
        score += 1
    else:
        print("❌ models.py manquant")
    
    return score, total

def test_celery():
    """Test du système Celery"""
    print_section("⚡ Système Celery")
    
    score = 0
    total = 3
    
    # Test celery_app.py
    celery_app_path = 'src/celery_app.py'
    if os.path.exists(celery_app_path):
        print("✅ celery_app.py existe")
        score += 1
    else:
        print("❌ celery_app.py manquant")
    
    # Test tasks
    tasks_dir = 'src/tasks'
    if os.path.isdir(tasks_dir):
        print("✅ Dossier tasks existe")
        score += 1
    else:
        print("❌ Dossier tasks manquant")
    
    # Test script de test Celery
    test_celery_path = 'test_celery_system.py'
    if os.path.exists(test_celery_path):
        print("✅ Script test Celery existe")
        score += 1
    else:
        print("❌ Script test Celery manquant")
    
    return score, total

def test_docker():
    """Test de la configuration Docker"""
    print_section("🐳 Configuration Docker")
    
    score = 0
    total = 3
    
    # Test docker-compose.yml
    if os.path.exists('docker-compose.yml'):
        print("✅ docker-compose.yml existe")
        score += 1
    else:
        print("❌ docker-compose.yml manquant")
    
    # Test Dockerfile
    dockerfile_path = 'docker/app/Dockerfile'
    if os.path.exists(dockerfile_path):
        print("✅ Dockerfile app existe")
        score += 1
    else:
        print("❌ Dockerfile app manquant")
    
    # Test dossier docker
    if os.path.isdir('docker'):
        print("✅ Dossier docker existe")
        score += 1
    else:
        print("❌ Dossier docker manquant")
    
    return score, total

def test_documentation():
    """Test de la documentation"""
    print_section("📚 Documentation")
    
    score = 0
    total = 4
    
    # Test README.md
    if os.path.exists('README.md'):
        print("✅ README.md existe")
        score += 1
    else:
        print("❌ README.md manquant")
    
    # Test dossier docs
    if os.path.isdir('docs'):
        print("✅ Dossier docs existe")
        score += 1
    else:
        print("❌ Dossier docs manquant")
    
    # Test requirements.txt
    if os.path.exists('requirements.txt'):
        print("✅ requirements.txt existe")
        score += 1
    else:
        print("❌ requirements.txt manquant")
    
    # Test .gitignore
    if os.path.exists('.gitignore'):
        print("✅ .gitignore existe")
        score += 1
    else:
        print("❌ .gitignore manquant")
    
    return score, total

def run_pytest():
    """Exécute les tests pytest"""
    print_section("🧪 Tests Pytest")
    
    try:
        result = subprocess.run(
            ['python', '-m', 'pytest', 'tests/', '-v', '--tb=short', '--quiet'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Tests pytest passés")
            return 1, 1
        else:
            print(f"❌ Tests pytest échoués: {result.stderr}")
            return 0, 1
    except subprocess.TimeoutExpired:
        print("❌ Tests pytest timeout")
        return 0, 1
    except Exception as e:
        print(f"❌ Erreur tests pytest: {e}")
        return 0, 1

def main():
    """Fonction principale"""
    print_header("🏦 TEST CI/CD - SYSTÈME BANCAIRE INTELLIGENT")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_score = 0
    total_tests = 0
    
    # Tests structure
    score, tests = test_file_structure()
    total_score += score
    total_tests += tests
    
    # Tests base de données
    score, tests = test_database()
    total_score += score
    total_tests += tests
    
    # Tests environnement Python
    score, tests = test_python_environment()
    total_score += score
    total_tests += tests
    
    # Tests frontend
    score, tests = test_frontend()
    total_score += score
    total_tests += tests
    
    # Tests API
    score, tests = test_api()
    total_score += score
    total_tests += tests
    
    # Tests Celery
    score, tests = test_celery()
    total_score += score
    total_tests += tests
    
    # Tests Docker
    score, tests = test_docker()
    total_score += score
    total_tests += tests
    
    # Tests documentation
    score, tests = test_documentation()
    total_score += score
    total_tests += tests
    
    # Tests pytest
    score, tests = run_pytest()
    total_score += score
    total_tests += tests
    
    # Résultat final
    print_header("🎯 RÉSULTAT FINAL")
    percentage = (total_score / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"Score: {total_score}/{total_tests} ({percentage:.1f}%)")
    
    if percentage >= 90:
        print("🏆 EXCELLENT - Prêt pour la production")
        exit_code = 0
    elif percentage >= 80:
        print("✅ BON - Quelques améliorations mineures")
        exit_code = 0
    elif percentage >= 70:
        print("⚠️ MOYEN - Améliorations nécessaires")
        exit_code = 1
    else:
        print("❌ INSUFFISANT - Problèmes critiques")
        exit_code = 1
    
    print(f"\nTest terminé à {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return exit_code

if __name__ == "__main__":
    exit(main()) 
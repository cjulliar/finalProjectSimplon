#!/usr/bin/env python3
"""
Script de test final du système Bank Reports
Teste toutes les fonctionnalités implémentées
"""

import requests
import json
import time
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}  {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")

def print_test(name, status, details=""):
    status_icon = f"{Colors.GREEN}✅" if status else f"{Colors.RED}❌"
    print(f"{status_icon} {Colors.WHITE}{name}{Colors.END}")
    if details:
        print(f"   {Colors.CYAN}{details}{Colors.END}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.END}")

def test_api_health():
    """Test de santé de l'API FastAPI"""
    print_header("Test API FastAPI (Port 8001)")
    
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        success = response.status_code == 200
        print_test("API Health Check", success, f"Status: {response.status_code}")
        
        if success:
            data = response.json()
            print_test("Database Connection", data.get('database') == 'connected', 
                      f"DB Type: {data.get('database_type', 'Unknown')}")
            print_test("AI Service", data.get('ai_service') == 'connected',
                      f"Mode: {data.get('ai_mode', 'Unknown')}")
        
        return success
    except Exception as e:
        print_test("API Health Check", False, f"Erreur: {e}")
        return False

def test_celery_api():
    """Test des endpoints Celery"""
    print_header("Test Système Celery")
    
    tests_passed = 0
    total_tests = 0
    
    # Test status
    try:
        response = requests.get("http://localhost:8001/api/celery/status", timeout=5)
        success = response.status_code == 200
        total_tests += 1
        if success:
            tests_passed += 1
            data = response.json()
            print_test("Status Endpoint", True, f"Status: {data.get('status')}")
        else:
            print_test("Status Endpoint", False, f"HTTP {response.status_code}")
    except Exception as e:
        total_tests += 1
        print_test("Status Endpoint", False, f"Erreur: {e}")
    
    # Test workers
    try:
        response = requests.get("http://localhost:8001/api/celery/workers", timeout=5)
        success = response.status_code == 200
        total_tests += 1
        if success:
            tests_passed += 1
            data = response.json()
            print_test("Workers Endpoint", True, f"Workers: {data.get('total_workers', 0)}")
        else:
            print_test("Workers Endpoint", False, f"HTTP {response.status_code}")
    except Exception as e:
        total_tests += 1
        print_test("Workers Endpoint", False, f"Erreur: {e}")
    
    # Test tasks
    try:
        response = requests.get("http://localhost:8001/api/celery/tasks", timeout=5)
        success = response.status_code == 200
        total_tests += 1
        if success:
            tests_passed += 1
            data = response.json()
            active_count = len(data.get('active_tasks', {}))
            print_test("Tasks Endpoint", True, f"Tâches actives: {active_count}")
        else:
            print_test("Tasks Endpoint", False, f"HTTP {response.status_code}")
    except Exception as e:
        total_tests += 1
        print_test("Tasks Endpoint", False, f"Erreur: {e}")
    
    # Test connectivity
    try:
        response = requests.post("http://localhost:8001/api/celery/test", timeout=10)
        success = response.status_code == 200
        total_tests += 1
        if success:
            tests_passed += 1
            data = response.json()
            connectivity = data.get('connectivity')
            print_test("Connectivity Test", connectivity == 'success', 
                      f"Résultat: {connectivity}")
        else:
            print_test("Connectivity Test", False, f"HTTP {response.status_code}")
    except Exception as e:
        total_tests += 1
        print_test("Connectivity Test", False, f"Erreur: {e}")
    
    print_info(f"Endpoints Celery: {tests_passed}/{total_tests} fonctionnels")
    return tests_passed, total_tests

def test_django_frontend():
    """Test du frontend Django"""
    print_header("Test Frontend Django (Port 8080)")
    
    try:
        response = requests.get("http://localhost:8080/", timeout=5)
        success = response.status_code == 200
        print_test("Django Home Page", success, f"Status: {response.status_code}")
        
        # Test dashboard Celery
        try:
            response = requests.get("http://localhost:8080/celery/", timeout=5)
            celery_success = response.status_code == 200
            print_test("Celery Dashboard", celery_success, f"Status: {response.status_code}")
        except Exception as e:
            print_test("Celery Dashboard", False, f"Erreur: {e}")
            celery_success = False
        
        return success and celery_success
    except Exception as e:
        print_test("Django Home Page", False, f"Erreur: {e}")
        return False

def test_database_files():
    """Vérification des fichiers de base de données"""
    print_header("Test Bases de Données")
    
    # SQLite API
    api_db = Path("src/bankreports.db")
    api_exists = api_db.exists()
    print_test("Base SQLite API", api_exists, 
              f"Taille: {api_db.stat().st_size // 1024} KB" if api_exists else "Fichier manquant")
    
    # SQLite Django
    django_db = Path("frontend/db.sqlite3")
    django_exists = django_db.exists()
    print_test("Base SQLite Django", django_exists,
              f"Taille: {django_db.stat().st_size // 1024} KB" if django_exists else "Fichier manquant")
    
    return api_exists and django_exists

def test_generated_reports():
    """Vérification des rapports générés"""
    print_header("Test Rapports Générés")
    
    reports_dir = Path("reports")
    if not reports_dir.exists():
        print_test("Dossier Reports", False, "Dossier manquant")
        return False
    
    html_files = list(reports_dir.glob("*.html"))
    pdf_files = list(reports_dir.glob("*.pdf"))
    
    print_test("Dossier Reports", True, f"Trouvé: {len(html_files)} HTML, {len(pdf_files)} PDF")
    
    if html_files:
        latest_html = max(html_files, key=lambda f: f.stat().st_mtime)
        size_kb = latest_html.stat().st_size // 1024
        print_test("Dernier Rapport HTML", True, f"{latest_html.name} ({size_kb} KB)")
    
    return len(html_files) > 0

def test_openapi_docs():
    """Test de la documentation OpenAPI"""
    print_header("Test Documentation API")
    
    try:
        response = requests.get("http://localhost:8001/docs", timeout=5)
        docs_success = response.status_code == 200
        print_test("Swagger UI", docs_success, f"Status: {response.status_code}")
        
        response = requests.get("http://localhost:8001/openapi.json", timeout=5)
        openapi_success = response.status_code == 200
        print_test("OpenAPI Schema", openapi_success, f"Status: {response.status_code}")
        
        if openapi_success:
            data = response.json()
            paths = len(data.get('paths', {}))
            print_info(f"Endpoints documentés: {paths}")
        
        return docs_success and openapi_success
    except Exception as e:
        print_test("Documentation API", False, f"Erreur: {e}")
        return False

def generate_system_report():
    """Génère un rapport du système"""
    print_header("Rapport Final du Système")
    
    # Collecte des informations
    api_ok = test_api_health()
    celery_passed, celery_total = test_celery_api()
    django_ok = test_django_frontend()
    db_ok = test_database_files()
    reports_ok = test_generated_reports()
    docs_ok = test_openapi_docs()
    
    # Calcul du score
    total_score = 0
    max_score = 0
    
    # API (20 points)
    max_score += 20
    if api_ok:
        total_score += 20
    
    # Celery (30 points)
    max_score += 30
    total_score += int((celery_passed / max(celery_total, 1)) * 30)
    
    # Django (20 points)
    max_score += 20
    if django_ok:
        total_score += 20
    
    # Databases (15 points)
    max_score += 15
    if db_ok:
        total_score += 15
    
    # Reports (10 points)
    max_score += 10
    if reports_ok:
        total_score += 10
    
    # Documentation (5 points)
    max_score += 5
    if docs_ok:
        total_score += 5
    
    percentage = (total_score / max_score) * 100
    
    print_header("🎯 SCORE FINAL")
    print(f"{Colors.BOLD}{Colors.PURPLE}Score: {total_score}/{max_score} ({percentage:.1f}%){Colors.END}")
    
    if percentage >= 90:
        print(f"{Colors.GREEN}{Colors.BOLD}🏆 EXCELLENT - Système production-ready!{Colors.END}")
    elif percentage >= 75:
        print(f"{Colors.YELLOW}{Colors.BOLD}🥈 TRÈS BIEN - Système fonctionnel avec améliorations possibles{Colors.END}")
    elif percentage >= 60:
        print(f"{Colors.YELLOW}{Colors.BOLD}🥉 BIEN - Système de base opérationnel{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ INSUFFISANT - Problèmes critiques détectés{Colors.END}")
    
    # Recommandations
    print_header("📋 Recommandations")
    
    if not api_ok:
        print(f"{Colors.RED}• Corriger l'API FastAPI (port 8001){Colors.END}")
    if celery_passed < celery_total:
        print(f"{Colors.YELLOW}• Améliorer la connectivité Celery/Redis{Colors.END}")
    if not django_ok:
        print(f"{Colors.RED}• Corriger le frontend Django (port 8080){Colors.END}")
    if not db_ok:
        print(f"{Colors.YELLOW}• Vérifier les bases de données{Colors.END}")
    if not reports_ok:
        print(f"{Colors.YELLOW}• Générer des rapports de test{Colors.END}")
    
    if percentage >= 90:
        print(f"{Colors.GREEN}• Déployer en production avec Docker{Colors.END}")
        print(f"{Colors.GREEN}• Configurer Redis pour Celery en production{Colors.END}")
        print(f"{Colors.GREEN}• Implémenter l'envoi d'emails réel{Colors.END}")

if __name__ == "__main__":
    print(f"{Colors.BOLD}{Colors.PURPLE}")
    print("=" * 80)
    print("  🏦 BANK REPORTS SYSTEM - TEST FINAL")
    print("  🎯 Validation complète du système")
    print("=" * 80)
    print(f"{Colors.END}")
    
    try:
        generate_system_report()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrompu par l'utilisateur{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Erreur lors du test: {e}{Colors.END}")
        sys.exit(1)
    
    print(f"\n{Colors.CYAN}Test terminé à {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}") 
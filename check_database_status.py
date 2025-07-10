#!/usr/bin/env python3
"""
Script pour vérifier le statut des bases de données du projet.
"""
import requests
import json
import sys

def check_api_database():
    """Vérifie la base de données utilisée par l'API."""
    try:
        response = requests.get("http://localhost:8000/api/database-info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {"error": f"API Status: {response.status_code}"}
    except Exception as e:
        return {"error": f"API inaccessible: {e}"}

def check_frontend_status():
    """Vérifie le statut du frontend."""
    try:
        response = requests.get("http://localhost:8080", timeout=5, allow_redirects=False)
        return {"status": f"HTTP {response.status_code}", "available": True}
    except Exception as e:
        return {"status": f"Erreur: {e}", "available": False}

def main():
    print("🔍 === STATUT DES BASES DE DONNÉES ===")
    print()
    
    # Vérification API
    print("📊 API FastAPI:")
    api_db = check_api_database()
    if "error" in api_db:
        print(f"   ❌ {api_db['error']}")
    else:
        db_type = api_db.get('type', 'Unknown')
        url = api_db.get('url', 'Unknown')
        status = api_db.get('status', 'Unknown')
        
        if db_type == "PostgreSQL":
            print(f"   🐘 Base de données: PostgreSQL")
        elif db_type == "SQLite":
            print(f"   🗄️ Base de données: SQLite")
        else:
            print(f"   ❓ Base de données: {db_type}")
        
        print(f"   📍 URL: {url}")
        print(f"   🔗 Statut: {status}")
    
    print()
    
    # Vérification Frontend
    print("🌐 Frontend Django:")
    frontend_status = check_frontend_status()
    if frontend_status['available']:
        print(f"   ✅ Disponible - {frontend_status['status']}")
        print(f"   📱 URL: http://localhost:8080")
    else:
        print(f"   ❌ {frontend_status['status']}")
    
    print()
    print("💡 Configuration actuelle:")
    print("   - PostgreSQL prioritaire avec fallback SQLite automatique")
    print("   - API et Frontend utilisent la même logique de fallback")
    print("   - Basculement transparent en cas d'indisponibilité PostgreSQL")

if __name__ == "__main__":
    main() 
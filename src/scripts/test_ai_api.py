#!/usr/bin/env python3
"""
Script pour tester l'API d'IA avec des données de test.
"""
import sys
import os
import argparse
import json
import requests
from datetime import date, datetime, timedelta
from pathlib import Path

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.database import SessionLocal, engine, Base
from src.db.models import BankData, User
from src.scripts.generate_test_data import generate_test_data, insert_test_data, initialize_database


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description="Tester l'API d'IA avec des données générées.")
    parser.add_argument(
        "--entries", "-e",
        type=int,
        default=100,
        help="Nombre d'entrées à générer (par défaut: 100)"
    )
    parser.add_argument(
        "--host", "-H",
        type=str,
        default="http://localhost:8000",
        help="URL de l'API (par défaut: http://localhost:8000)"
    )
    parser.add_argument(
        "--username", "-u",
        type=str,
        default="admin",
        help="Nom d'utilisateur pour l'authentification (par défaut: admin)"
    )
    parser.add_argument(
        "--password", "-p",
        type=str,
        default="password123",
        help="Mot de passe pour l'authentification (par défaut: password123)"
    )
    parser.add_argument(
        "--generate-data", "-g",
        action="store_true",
        help="Générer des données de test avant d'exécuter le test de l'API"
    )
    return parser.parse_args()


def get_auth_token(host, username, password):
    """Obtenir un token d'authentification."""
    print(f"Authentification en tant que {username}...")
    
    try:
        response = requests.post(
            f"{host}/api/token",
            data={
                "username": username,
                "password": password
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("Authentification réussie.")
            return token
        else:
            print(f"Erreur d'authentification: {response.status_code} - {response.text}")
            return None
    
    except Exception as e:
        print(f"Erreur lors de l'authentification: {str(e)}")
        return None


def test_ai_api(host, token, agence=None):
    """Tester l'API d'IA."""
    print("\nTest de l'API d'IA...")
    
    # Préparer les paramètres de la requête
    request_data = {
        "start_date": (date.today() - timedelta(days=30)).isoformat(),
        "end_date": date.today().isoformat(),
        "include_visualizations": True
    }
    
    if agence:
        request_data["agence"] = agence
    
    try:
        # Appeler l'API
        response = requests.post(
            f"{host}/api/ai/analyze",
            json=request_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n=== Analyse IA réussie ===")
            print(f"ID de l'analyse: {result['id']}")
            print(f"Nombre de points de données: {result['metadata']['data_points']}")
            print(f"Agences analysées: {', '.join(result['metadata']['agencies'])}")
            print(f"Temps d'exécution: {result['metadata']['execution_time']:.2f} secondes")
            print(f"Modèle utilisé: {result['metadata']['model_used']}")
            
            print("\n=== Extrait du rapport ===")
            # Afficher les 500 premiers caractères du rapport
            print(result["report"][:500] + "...\n")
            
            if result["visualizations"]:
                print(f"Visualisations générées: {len(result['visualizations'])}")
                for i, viz in enumerate(result["visualizations"]):
                    print(f"  {i+1}. {viz['title']} - {viz['type']} - {viz['url']}")
            
            return result
            
        else:
            print(f"Erreur lors de l'appel à l'API: {response.status_code} - {response.text}")
            return None
    
    except Exception as e:
        print(f"Erreur lors du test de l'API d'IA: {str(e)}")
        return None


def main():
    """Point d'entrée principal."""
    args = parse_arguments()
    
    # Générer des données de test si demandé
    if args.generate_data:
        print("\n=== Génération des données de test ===")
        initialize_database()
        data = generate_test_data(args.entries)
        insert_test_data(data)
    
    # Obtenir un token d'authentification
    token = get_auth_token(args.host, args.username, args.password)
    if not token:
        print("Impossible de continuer sans authentification.")
        return 1
    
    # Tester l'API d'IA
    result = test_ai_api(args.host, token)
    if not result:
        print("Le test de l'API d'IA a échoué.")
        return 1
    
    print("\nTest terminé avec succès.")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
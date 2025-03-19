#!/usr/bin/env python3
"""
Script pour lancer l'API FastAPI.
"""
import sys
import os
import argparse
import subprocess
from pathlib import Path

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description="Lancer l'API FastAPI.")
    parser.add_argument(
        "--host", "-H",
        type=str,
        default="127.0.0.1",
        help="Hôte sur lequel lancer l'API (par défaut: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8000,
        help="Port sur lequel lancer l'API (par défaut: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Activer le rechargement automatique à chaque modification de code"
    )
    return parser.parse_args()


def main():
    """Point d'entrée principal."""
    args = parse_arguments()
    
    # Construire la commande uvicorn
    cmd = [
        "uvicorn",
        "src.api.main:app",
        "--host", args.host,
        "--port", str(args.port)
    ]
    
    if args.reload:
        cmd.append("--reload")
    
    # Afficher des informations
    print(f"Démarrage de l'API sur http://{args.host}:{args.port}")
    print("Documentation de l'API disponible sur :")
    print(f"- Swagger UI : http://{args.host}:{args.port}/docs")
    print(f"- ReDoc : http://{args.host}:{args.port}/redoc")
    print("Utilisez Ctrl+C pour arrêter l'API\n")
    
    # Exécuter uvicorn
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nArrêt de l'API")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
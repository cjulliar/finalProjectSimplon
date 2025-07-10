#!/usr/bin/env python3
"""
Script pour démarrer l'API FastAPI.
"""
import os
import sys
import uvicorn
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api.main import app


def main():
    """Point d'entrée principal."""
    # Configuration par défaut
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "false").lower() == "true"
    
    print(f"Démarrage de l'API sur {host}:{port}")
    print(f"Mode reload: {reload}")
    
    # Démarrer le serveur
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Script pour exécuter tous les tests.
"""
import os
import sys
import subprocess
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_tests():
    """Exécuter tous les tests."""
    print("=== Exécution des tests ===")
    
    # Test d'import des modules principaux
    try:
        import src.api.main
        print("✓ Import de src.api.main réussi")
    except Exception as e:
        print(f"✗ Erreur lors de l'import de src.api.main: {e}")
        return 1
    
    try:
        import src.db.database
        print("✓ Import de src.db.database réussi")
    except Exception as e:
        print(f"✗ Erreur lors de l'import de src.db.database: {e}")
        return 1
    
    try:
        import src.ia.ai_service
        print("✓ Import de src.ia.ai_service réussi")
    except Exception as e:
        print(f"✗ Erreur lors de l'import de src.ia.ai_service: {e}")
        return 1
    
    # Test de création des tables
    try:
        from src.db.database import engine
        from src.db.models import Base
        Base.metadata.create_all(bind=engine)
        print("✓ Création des tables réussie")
    except Exception as e:
        print(f"✗ Erreur lors de la création des tables: {e}")
        return 1
    
    # Test de l'API
    try:
        from src.api.main import app
        print("✓ Application FastAPI créée avec succès")
    except Exception as e:
        print(f"✗ Erreur lors de la création de l'application FastAPI: {e}")
        return 1
    
    print("=== Tous les tests sont passés ===")
    return 0


def main():
    """Point d'entrée principal."""
    return run_tests()


if __name__ == "__main__":
    sys.exit(main()) 
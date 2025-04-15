#!/usr/bin/env python3
"""
Script pour exécuter tous les tests du projet.
Ce script est utilisé dans le CI/CD pour vérifier que tous les tests passent.
"""
import sys
import os
import subprocess
import time
from pathlib import Path

# Ajouter le répertoire parent au chemin de recherche Python
root_dir = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(root_dir))

# Liste des modules de test à exécuter
TEST_MODULES = [
    "tests/test_database.py",
    "tests/test_excel_import.py",
    "tests/test_main.py",
    "tests/test_ia_service.py",  # Ajout du test pour le service d'IA
    # "tests/test_api.py"  # Commenté car nécessite des dépendances supplémentaires
]

# Configuration de l'environnement de test
os.environ["TESTING"] = "True"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["API_SECRET_KEY"] = "test-secret-key"


def initialize_test_environment():
    """Initialiser l'environnement de test."""
    print("== Initialisation de l'environnement de test ==")
    
    # Créer les répertoires nécessaires s'ils n'existent pas
    for directory in ["docs", "data"]:
        dir_path = root_dir / directory
        if not dir_path.exists():
            print(f"Création du répertoire {directory}...")
            dir_path.mkdir(exist_ok=True)


def generate_test_data():
    """Générer des données de test pour les tests."""
    print("== Génération des données de test ==")
    
    # Générer un fichier Excel de test si nécessaire
    docs_dir = root_dir / "docs"
    excel_path = docs_dir / "DonneeBanque.xlsx"
    
    if not excel_path.exists():
        try:
            import pandas as pd
            print(f"Création du fichier Excel de test: {excel_path}")
            
            # Créer un DataFrame avec des données de test simples
            data = {
                'agence': ['Agence A', 'Agence B', 'Agence C'],
                'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
                'montant': [1000, 2000, 3000],
                'nombre_transactions': [10, 20, 30]
            }
            df = pd.DataFrame(data)
            
            # Sauvegarder en Excel
            df.to_excel(excel_path, index=False)
            print(f"Fichier Excel créé avec succès.")
        except Exception as e:
            print(f"Erreur lors de la création du fichier Excel: {e}")
            print("Les tests nécessitant ce fichier pourraient échouer.")


def run_tests():
    """Exécuter tous les tests."""
    print("== Exécution des tests ==")
    
    start_time = time.time()
    all_passed = True
    
    # Exécuter pytest pour tous les modules de test
    for module in TEST_MODULES:
        module_path = root_dir / module
        if not module_path.exists():
            print(f"ERREUR: Le module de test {module} n'existe pas.")
            all_passed = False
            continue
        
        print(f"\nTest de {module}...")
        cmd = ["python3", "-m", "pytest", str(module_path), "-v"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
            
            if result.returncode != 0:
                print(f"ÉCHEC: Le test {module} a échoué avec le code {result.returncode}")
                print(result.stderr)
                all_passed = False
            else:
                print(f"SUCCÈS: Le test {module} a réussi.")
        except Exception as e:
            print(f"ERREUR: Impossible d'exécuter le test {module}: {e}")
            all_passed = False
    
    # Afficher un récapitulatif
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n== Récapitulatif des tests ==")
    print(f"Durée totale: {duration:.2f} secondes")
    print(f"Résultat global: {'SUCCÈS' if all_passed else 'ÉCHEC'}")
    
    return 0 if all_passed else 1


def main():
    """Point d'entrée principal."""
    print("\n=== Batterie de tests pour CI/CD ===\n")
    
    # Initialiser l'environnement de test
    initialize_test_environment()
    
    # Générer des données de test
    generate_test_data()
    
    # Exécuter les tests
    result = run_tests()
    
    print("\n=== Fin de la batterie de tests ===\n")
    return result


if __name__ == "__main__":
    sys.exit(main()) 
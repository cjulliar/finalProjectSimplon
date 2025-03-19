#!/usr/bin/env python3
"""
Script pour exécuter tous les tests liés à l'importation des données et à la base de données.
Ceci permettra de valider les éléments du critère C4 de la grille d'évaluation.
"""
import sys
import os
import subprocess
from pathlib import Path


def run_tests():
    """Exécute les tests pertinents pour C4."""
    # Obtenir le chemin absolu du projet
    root_dir = Path(__file__).parent.parent.absolute()
    
    # Modifier le chemin de recherche Python
    sys.path.insert(0, str(root_dir))
    
    # Liste des modules de test à exécuter
    test_modules = [
        "tests/test_database.py",
        "tests/test_excel_import.py"
    ]
    
    # Exécuter les tests
    print("=== Exécution des tests pour C4 ===")
    
    # Vérifier que les fichiers existent
    for module in test_modules:
        module_path = root_dir / module
        if not module_path.exists():
            print(f"Erreur: Le module de test {module} n'existe pas.")
            return 1
    
    # Exécuter pytest
    cmd = ["python3", "-m", "pytest"] + test_modules + ["-v"]
    result = subprocess.run(cmd, cwd=str(root_dir))
    
    # Afficher un récapitulatif
    if result.returncode == 0:
        print("\n=== Tous les tests ont réussi ! ===")
        print("Éléments testés avec succès :")
        print("✅ Connexion à la base de données")
        print("✅ Modèle de données")
        print("✅ Lecture du fichier Excel")
        print("✅ Nettoyage et transformation des données")
        print("✅ Insertion des données dans la base")
        print("✅ Performances d'insertion par lots")
        print("✅ Requêtes et filtrage des données")
        print("\nCes éléments valident les points suivants du critère C4 :")
        print("- Le modèle physique des données est fonctionnel")
        print("- Le script d'import fourni est fonctionnel")
    else:
        print("\n=== Certains tests ont échoué ===")
        print("Veuillez vérifier les erreurs ci-dessus.")
    
    return result.returncode


def main():
    """Point d'entrée principal."""
    sys.exit(run_tests())


if __name__ == "__main__":
    main() 
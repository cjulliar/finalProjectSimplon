#!/usr/bin/env python3
"""
Script pour générer des données de test et les insérer dans la base de données.
"""
import sys
import os
import argparse
import random
from datetime import date, timedelta
from pathlib import Path

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.database import SessionLocal, engine, Base
from src.db.models import BankData


def initialize_database():
    """Initialiser la base de données en créant toutes les tables."""
    print("Initialisation de la base de données...")
    Base.metadata.create_all(bind=engine)
    print("Base de données initialisée avec succès.")


def generate_test_data(num_entries=100):
    """Générer des données de test pour la base de données."""
    print(f"Génération de {num_entries} entrées de test...")
    
    # Liste des agences
    agences = ["Agence A", "Agence B", "Agence C", "Agence D", "Agence E"]
    
    # Date de début (il y a 30 jours)
    start_date = date.today() - timedelta(days=30)
    
    # Liste pour stocker les données générées
    data = []
    
    # Pour chaque agence, générer des données pour les 30 derniers jours
    for agence in agences:
        for i in range(30):
            current_date = start_date + timedelta(days=i)
            
            # Générer des montants et nombres de transactions aléatoires
            montant = random.uniform(1000, 10000)
            nombre_transactions = random.randint(5, 100)
            
            # Créer l'objet BankData
            data.append(BankData(
                agence=agence,
                date=current_date,
                montant=montant,
                nombre_transactions=nombre_transactions
            ))
    
    return data


def insert_test_data(data):
    """Insérer les données de test dans la base de données."""
    print("Insertion des données dans la base de données...")
    
    db = SessionLocal()
    
    try:
        # Ajouter toutes les données
        db.add_all(data)
        db.commit()
        print(f"{len(data)} entrées insérées avec succès.")
        return True
    except Exception as e:
        db.rollback()
        print(f"Erreur lors de l'insertion des données : {e}")
        return False
    finally:
        db.close()


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description="Générer des données de test pour la base de données.")
    parser.add_argument(
        "--entries", "-e",
        type=int,
        default=100,
        help="Nombre d'entrées à générer (par défaut: 100)"
    )
    return parser.parse_args()


def main():
    """Point d'entrée principal."""
    args = parse_arguments()
    
    # Initialiser la base de données
    initialize_database()
    
    # Générer les données de test
    data = generate_test_data(args.entries)
    
    # Insérer les données dans la base de données
    success = insert_test_data(data)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 
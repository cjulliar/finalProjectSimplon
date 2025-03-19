#!/usr/bin/env python3
"""
Script pour visualiser le contenu de la base de données SQLite.
"""
import argparse
import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
from src.db.database import SessionLocal
from src.db.models import BankData


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description="Affiche le contenu de la base de données SQLite.")
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=10,
        help="Nombre maximum de lignes à afficher (par défaut: 10)"
    )
    parser.add_argument(
        "--agence", "-a",
        type=str,
        help="Filtrer par agence"
    )
    parser.add_argument(
        "--stats", "-s",
        action="store_true",
        help="Afficher les statistiques"
    )
    return parser.parse_args()


def display_data(limit=10, agence=None):
    """
    Affiche les données de la base de données.
    
    Args:
        limit (int): Nombre maximum de lignes à afficher
        agence (str, optional): Filtre par agence
    """
    with SessionLocal() as db:
        # Construction de la requête
        query = db.query(BankData)
        
        # Appliquer le filtre d'agence si spécifié
        if agence:
            query = query.filter(BankData.agence == agence)
        
        # Limiter le nombre de résultats
        query = query.limit(limit)
        
        # Exécuter la requête
        results = query.all()
        
        if not results:
            print("Aucune donnée trouvée dans la base de données.")
            return
        
        # Conversion en DataFrame pour un affichage plus propre
        data = [{
            'ID': item.id,
            'Agence': item.agence,
            'Date': item.date,
            'Montant': item.montant,
            'Nombre de transactions': item.nombre_transactions,
            'Date de création': item.created_at
        } for item in results]
        
        df = pd.DataFrame(data)
        print(df)


def display_stats():
    """Affiche des statistiques sur les données."""
    with SessionLocal() as db:
        # Nombre total d'enregistrements
        total_count = db.query(BankData).count()
        
        if total_count == 0:
            print("Aucune donnée trouvée dans la base de données.")
            return
        
        print(f"Nombre total d'enregistrements: {total_count}")
        
        # Nombre d'agences uniques
        agence_count = db.query(BankData.agence).distinct().count()
        print(f"Nombre d'agences: {agence_count}")
        
        # Liste des agences
        agences = [a[0] for a in db.query(BankData.agence).distinct().all()]
        print(f"Agences: {', '.join(agences)}")
        
        # Statistiques par agence
        print("\nStatistiques par agence:")
        for agence in agences:
            # Montant total par agence
            total_amount = db.query(BankData).filter(BankData.agence == agence).all()
            if total_amount:
                montant_total = sum(item.montant for item in total_amount)
                transactions_total = sum(item.nombre_transactions for item in total_amount)
                print(f"  {agence}: {len(total_amount)} enregistrements, "
                      f"{montant_total:.2f} € total, "
                      f"{transactions_total} transactions")


def main():
    """Point d'entrée principal."""
    args = parse_arguments()
    
    if args.stats:
        display_stats()
    else:
        display_data(limit=args.limit, agence=args.agence)
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
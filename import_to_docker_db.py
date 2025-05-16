#!/usr/bin/env python3
"""
Script pour importer les données de test dans la base de données PostgreSQL utilisée par Docker.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Fonction pour créer des données de test
def create_test_data():
    """
    Crée un DataFrame avec des données de test pour 5 semaines et 3 agences.
    
    Returns:
        DataFrame: Données de test
    """
    # Créer des données de test pour 5 semaines et 3 agences
    data = []
    for week in range(5):
        for agency in ['Agence1', 'Agence2', 'Agence3']:
            # Simuler une tendance avec des variations aléatoires
            base_amount = 1000 * (1 + 0.1 * week) + np.random.randint(-200, 200)
            base_transactions = 50 * (1 + 0.05 * week) + np.random.randint(-10, 10)
            
            data.append({
                'ID_SEM_COMM': f'S{week+1}',
                'GROUPE': agency,
                'SOMME_PART': base_amount * 0.6,
                'SOMME_PRO': base_amount * 0.4,
                'OCC_PART': int(base_transactions * 0.7),
                'OCC_PRO': int(base_transactions * 0.3)
            })

    # Créer un DataFrame
    return pd.DataFrame(data)

# Script principal
if __name__ == "__main__":
    print("Création des données de test...")
    df = create_test_data()
    
    print("Aperçu des données:")
    print(df.head())
    
    # Enregistrer en CSV pour l'import dans Docker
    csv_path = "docker_import_data.csv"
    df.to_csv(csv_path, index=False)
    print(f"Données sauvegardées dans {csv_path}")
    
    print("\nPour importer ces données dans la base de données PostgreSQL, exécutez:")
    print(f"docker exec -i finalprojectsimplon-db-1 psql -U postgres -d bankreports -c \"CREATE TEMPORARY TABLE temp_import (ID_SEM_COMM TEXT, GROUPE TEXT, SOMME_PART FLOAT, SOMME_PRO FLOAT, OCC_PART INT, OCC_PRO INT);\"")
    print(f"cat {csv_path} | docker exec -i finalprojectsimplon-db-1 psql -U postgres -d bankreports -c \"\\COPY temp_import FROM STDIN WITH CSV HEADER;\"")
    print(f"docker exec -i finalprojectsimplon-db-1 psql -U postgres -d bankreports -c \"INSERT INTO bank_data (agence, date, montant, nombre_transactions, created_at) SELECT GROUPE, CURRENT_DATE - (CAST(SUBSTRING(ID_SEM_COMM, 2, 1) AS INTEGER) * INTERVAL '7 days'), SOMME_PART + SOMME_PRO, OCC_PART + OCC_PRO, NOW() FROM temp_import;\"")
    
    print("\nOu exécutez le script avec l'option --import pour importer automatiquement:")
    print(f"python {sys.argv[0]} --import")
    
    # Si l'option --import est spécifiée, importer automatiquement
    if len(sys.argv) > 1 and sys.argv[1] == "--import":
        print("\nImportation automatique des données...")
        
        # Commande pour créer une table temporaire
        create_temp_table_cmd = f"docker exec -i finalprojectsimplon-db-1 psql -U postgres -d bankreports -c \"CREATE TEMPORARY TABLE temp_import (ID_SEM_COMM TEXT, GROUPE TEXT, SOMME_PART FLOAT, SOMME_PRO FLOAT, OCC_PART INT, OCC_PRO INT);\""
        print(f"Exécution: {create_temp_table_cmd}")
        os.system(create_temp_table_cmd)
        
        # Commande pour copier les données
        copy_cmd = f"cat {csv_path} | docker exec -i finalprojectsimplon-db-1 psql -U postgres -d bankreports -c \"\\COPY temp_import FROM STDIN WITH CSV HEADER;\""
        print(f"Exécution: {copy_cmd}")
        os.system(copy_cmd)
        
        # Commande pour insérer les données dans bank_data
        insert_cmd = f"docker exec -i finalprojectsimplon-db-1 psql -U postgres -d bankreports -c \"INSERT INTO bank_data (agence, date, montant, nombre_transactions, created_at) SELECT GROUPE, CURRENT_DATE - (CAST(SUBSTRING(ID_SEM_COMM, 2, 1) AS INTEGER) * INTERVAL '7 days'), SOMME_PART + SOMME_PRO, OCC_PART + OCC_PRO, NOW() FROM temp_import;\""
        print(f"Exécution: {insert_cmd}")
        os.system(insert_cmd)
        
        # Vérifier le nombre de lignes insérées
        count_cmd = f"docker exec -i finalprojectsimplon-db-1 psql -U postgres -d bankreports -c \"SELECT COUNT(*) FROM bank_data;\""
        print(f"Vérification du nombre de lignes: {count_cmd}")
        os.system(count_cmd)
        
        print("Importation terminée.") 
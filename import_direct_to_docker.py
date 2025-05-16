#!/usr/bin/env python3
"""
Script pour insérer directement des données de test dans la base de données PostgreSQL.
"""
import os
import random
from datetime import datetime, timedelta

# Configuration
NUM_WEEKS = 5
AGENCIES = ['Agence1', 'Agence2', 'Agence3']
START_DATE = datetime.now().date() - timedelta(days=NUM_WEEKS * 7)

# Générer des commandes SQL pour insérer des données
print("Génération des commandes SQL...")

# Commande pour vider la table
truncate_cmd = "docker exec -i finalprojectsimplon-db-1 psql -U postgres -d bankreports -c \"TRUNCATE TABLE bank_data;\""
print(f"Exécution: {truncate_cmd}")
os.system(truncate_cmd)

# Générer des données pour chaque semaine et agence
for week in range(NUM_WEEKS):
    for agency in AGENCIES:
        # Simuler une tendance avec des variations aléatoires
        base_amount = 1000 * (1 + 0.1 * week) + random.randint(-200, 200)
        base_transactions = 50 * (1 + 0.05 * week) + random.randint(-10, 10)
        
        # Calculer la date pour cette semaine
        date = START_DATE + timedelta(days=week * 7)
        
        # Créer la commande SQL
        sql = f"INSERT INTO bank_data (agence, date, montant, nombre_transactions, created_at) VALUES ('{agency}', '{date}', {base_amount}, {base_transactions}, NOW());"
        cmd = f"docker exec -i finalprojectsimplon-db-1 psql -U postgres -d bankreports -c \"{sql}\""
        
        print(f"Insertion de données pour {agency}, semaine {week+1} ({date})...")
        os.system(cmd)

# Vérifier le nombre de lignes insérées
count_cmd = "docker exec -i finalprojectsimplon-db-1 psql -U postgres -d bankreports -c \"SELECT COUNT(*) FROM bank_data;\""
print(f"\nVérification du nombre de lignes: ")
os.system(count_cmd)

# Afficher les données insérées
data_cmd = "docker exec -i finalprojectsimplon-db-1 psql -U postgres -d bankreports -c \"SELECT * FROM bank_data ORDER BY date DESC LIMIT 10;\""
print(f"\nAperçu des données insérées: ")
os.system(data_cmd)

print("\nImportation terminée.") 
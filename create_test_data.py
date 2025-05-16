import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Créer le répertoire docs s'il n'existe pas
os.makedirs('docs', exist_ok=True)

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
df = pd.DataFrame(data)

# Afficher un aperçu des données
print("Aperçu des données:")
print(df.head())

# Enregistrer en Excel
file_path = os.path.join('docs', 'DonneeBanque.xlsx')
df.to_excel(file_path, index=False)
print(f'Fichier Excel créé avec succès: {file_path}') 
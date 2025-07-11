#!/bin/bash

# Chemin du projet
PROJECT_DIR="/Users/cyriljulliard/simplon/finalProjectSimplon"
cd "$PROJECT_DIR"

# Activer l'environnement virtuel
source venv/bin/activate

# Lancer la génération des prompts
echo "Lancement de la génération des prompts d'analyse IA..."
python generate_analysis_prompts.py

# Vérification du résultat
if [ $? -eq 0 ]; then
    echo "✅ Génération des prompts terminée avec succès."
    echo "Les fichiers sont dans prompts_analysis/generated_prompts/"
else
    echo "❌ Erreur lors de la génération des prompts."
    echo "Vérifiez que la base de données contient bien la table 'bank_data' ou 'bank_data_enriched' et les données nécessaires."
fi 
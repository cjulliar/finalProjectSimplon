#!/usr/bin/env python3
"""
POC d'intégration d'IA pour l'analyse de données bancaires et la génération de rapports.
Ce script démontre l'utilisation d'OpenAI via son API pour analyser des données bancaires
et générer des rapports automatiques.

Prérequis:
    pip install openai pandas matplotlib
"""
import os
import json
import time
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import requests

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration de l'API OpenAI ou autre API LLM
API_KEY = os.getenv("LLM_API_KEY", "your-api-key-here")
# Utilisation d'une API accessible publiquement pour le POC si la clé OpenAI n'est pas disponible
USE_ALTERNATIVE_API = not API_KEY or API_KEY == "your-api-key-here"


def generate_sample_data():
    """Génère des données d'exemple représentatives des données bancaires."""
    print("Génération de données bancaires de test...")
    
    # Créer des données pour 3 agences sur 30 jours
    agences = ["Agence Paris", "Agence Lyon", "Agence Marseille"]
    dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]
    
    data = []
    for agence in agences:
        for date in dates:
            # Générer des valeurs différentes selon l'agence pour créer des tendances
            if agence == "Agence Paris":
                montant = 5000 + (hash(date) % 2000)  # Plus stable
                transactions = 50 + (hash(date) % 20)
            elif agence == "Agence Lyon":
                montant = 3000 + (hash(date) % 3000)  # Plus variable
                transactions = 30 + (hash(date) % 30)
            else:  # Marseille
                # Tendance à la hausse pour montrer une évolution
                jour = dates.index(date)
                montant = 2000 + jour * 100 + (hash(date) % 1000)
                transactions = 20 + jour + (hash(date) % 15)
            
            data.append({
                "agence": agence,
                "date": date,
                "montant": montant,
                "nombre_transactions": transactions
            })
    
    return pd.DataFrame(data)


def visualize_data(df):
    """Crée des visualisations des données pour analyse."""
    print("Création de visualisations pour l'analyse...")
    
    # Créer un dossier pour les visualisations
    os.makedirs("output", exist_ok=True)
    
    # Agrégation par agence
    agg_by_agency = df.groupby("agence").agg({
        "montant": "sum",
        "nombre_transactions": "sum"
    }).reset_index()
    
    # Créer un graphique à barres des montants par agence
    plt.figure(figsize=(10, 6))
    plt.bar(agg_by_agency["agence"], agg_by_agency["montant"])
    plt.title("Montant total par agence")
    plt.ylabel("Montant (€)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("output/montant_par_agence.png")
    
    # Créer un graphique à barres du nombre de transactions par agence
    plt.figure(figsize=(10, 6))
    plt.bar(agg_by_agency["agence"], agg_by_agency["nombre_transactions"])
    plt.title("Nombre de transactions par agence")
    plt.ylabel("Nombre de transactions")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("output/transactions_par_agence.png")
    
    # Tendance sur le temps pour chaque agence
    plt.figure(figsize=(12, 8))
    for agence in df["agence"].unique():
        agence_df = df[df["agence"] == agence]
        agence_df = agence_df.sort_values("date")
        plt.plot(agence_df["date"], agence_df["montant"], label=agence)
    
    plt.title("Évolution des montants par agence")
    plt.ylabel("Montant (€)")
    plt.xlabel("Date")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig("output/evolution_montants.png")
    
    print("Visualisations créées et enregistrées dans le dossier 'output'.")


def analyze_data_with_llm(df):
    """
    Utilise un modèle de langage (LLM) pour analyser les données bancaires
    et générer un rapport.
    """
    # Préparation des statistiques essentielles pour l'analyse
    total_montant = df["montant"].sum()
    total_transactions = df["nombre_transactions"].sum()
    moyenne_montant = df["montant"].mean()
    
    # Agrégations par agence
    agg_by_agency = df.groupby("agence").agg({
        "montant": ["sum", "mean"],
        "nombre_transactions": ["sum", "mean"]
    })
    
    # Trouver l'agence la plus performante
    best_agency = agg_by_agency[("montant", "sum")].idxmax()
    
    # Évolution récente (dernière semaine vs semaine précédente)
    df["date"] = pd.to_datetime(df["date"])
    last_week = df[df["date"] >= (datetime.now() - timedelta(days=7))]
    previous_week = df[(df["date"] < (datetime.now() - timedelta(days=7))) & 
                       (df["date"] >= (datetime.now() - timedelta(days=14)))]
    
    last_week_montant = last_week["montant"].sum()
    previous_week_montant = previous_week["montant"].sum()
    evolution_percentage = ((last_week_montant - previous_week_montant) / previous_week_montant) * 100
    
    # Préparation des données pour le prompt
    stats = {
        "total_montant": f"{total_montant:,.2f} €",
        "total_transactions": total_transactions,
        "moyenne_montant": f"{moyenne_montant:,.2f} €",
        "meilleure_agence": best_agency,
        "evolution_semaine": f"{evolution_percentage:.2f}%"
    }
    
    # Statistiques par agence
    agency_stats = {}
    for agence in df["agence"].unique():
        agence_df = df[df["agence"] == agence]
        agency_stats[agence] = {
            "total_montant": f"{agence_df['montant'].sum():,.2f} €",
            "total_transactions": agence_df["nombre_transactions"].sum(),
            "moyenne_montant": f"{agence_df['montant'].mean():,.2f} €"
        }
    
    # Construction du prompt pour l'IA
    prompt = f"""
    Analyser les données bancaires suivantes et générer un rapport détaillé pour le directeur.
    
    STATISTIQUES GLOBALES:
    - Montant total: {stats['total_montant']}
    - Transactions totales: {stats['total_transactions']}
    - Montant moyen par transaction: {stats['moyenne_montant']}
    - Évolution sur la semaine: {stats['evolution_semaine']}
    
    STATISTIQUES PAR AGENCE:
    """
    
    for agence, data in agency_stats.items():
        prompt += f"""
    {agence}:
    - Montant total: {data['total_montant']}
    - Transactions totales: {data['total_transactions']}
    - Montant moyen par transaction: {data['moyenne_montant']}
    """
    
    prompt += """
    INSTRUCTIONS:
    1. Analyser les performances de chaque agence
    2. Identifier les tendances et anomalies
    3. Proposer des recommandations stratégiques
    4. Rédiger un rapport structuré en français, avec introduction, analyse et conclusion
    5. Le rapport doit être destiné au directeur du groupe bancaire
    """
    
    print("\nAnalyse des données avec IA en cours...")
    print(f"Prompt utilisé:\n{prompt}\n")
    
    # Appel à l'API d'IA
    if USE_ALTERNATIVE_API:
        # Utilisation d'une API publique (HuggingFace) comme alternative
        print("Utilisation d'une API alternative (HuggingFace) pour le POC...")
        response = get_alternative_ai_response(prompt)
    else:
        # Utilisation de l'API OpenAI
        print("Utilisation de l'API OpenAI...")
        response = get_openai_response(prompt)
    
    return response


def get_openai_response(prompt):
    """Obtient une réponse de l'API OpenAI."""
    try:
        import openai
        openai.api_key = API_KEY
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Vous êtes un analyste financier expert spécialisé dans l'analyse de données bancaires."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API OpenAI: {e}")
        return get_alternative_ai_response(prompt)


def get_alternative_ai_response(prompt):
    """
    Obtient une réponse d'une API alternative (HuggingFace).
    Cette fonction est utilisée si l'API OpenAI n'est pas configurée.
    """
    try:
        # Utilisation de l'API HuggingFace comme alternative
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY', '')}"}
        
        # Si pas de clé HuggingFace, simuler une réponse pour le POC
        if not os.getenv('HUGGINGFACE_API_KEY'):
            print("Pas de clé API HuggingFace, simulation d'une réponse...")
            time.sleep(2)  # Simuler un délai de réponse
            return simulate_ai_response(prompt)
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": 0.7
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()[0]["generated_text"]
        
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API alternative: {e}")
        return simulate_ai_response(prompt)


def simulate_ai_response(prompt):
    """
    Simule une réponse d'IA pour le POC si aucune API n'est disponible.
    """
    # Extraire quelques statistiques du prompt pour les inclure dans la réponse simulée
    lines = prompt.strip().split('\n')
    stats = {}
    for line in lines:
        if "Montant total:" in line and "STATISTIQUES GLOBALES" in ''.join(lines[:lines.index(line)]):
            stats["montant_total"] = line.split(":")[1].strip()
        if "Évolution sur la semaine:" in line:
            stats["evolution"] = line.split(":")[1].strip()
    
    # Créer une réponse simulée basée sur les statistiques extraites
    return f"""
# Rapport d'Analyse Bancaire Hebdomadaire

## Introduction

Ce rapport présente l'analyse des performances des différentes agences bancaires pour la période écoulée. Le montant total des transactions s'élève à {stats.get("montant_total", "plusieurs millions d'euros")}, avec une évolution de {stats.get("evolution", "variation significative")} par rapport à la semaine précédente.

## Analyse des Performances par Agence

### Agence Paris
L'agence Paris maintient sa position de leader avec des performances stables. Sa stratégie de fidélisation client semble porter ses fruits, comme en témoigne la régularité des transactions.

### Agence Lyon
L'agence Lyon présente une volatilité plus importante dans ses résultats. Cette variabilité pourrait être liée à une dépendance plus forte aux grands comptes corporatifs.

### Agence Marseille
L'agence Marseille montre une tendance à la hausse prometteuse. Sa stratégie d'acquisition de nouveaux clients paraît efficace et devrait être étudiée pour une possible application dans les autres agences.

## Recommandations Stratégiques

1. **Partage des bonnes pratiques** : Organiser un workshop entre les responsables d'agences pour partager les stratégies qui fonctionnent.

2. **Diversification des portefeuilles clients** : L'agence Lyon pourrait bénéficier d'une diversification de sa clientèle pour réduire la volatilité.

3. **Capitaliser sur la croissance** : Investir davantage de ressources dans l'agence Marseille pour accélérer sa croissance actuelle.

## Conclusion

Les performances globales sont satisfaisantes avec une tendance positive. La diversité des profils de performance entre les agences offre des opportunités d'apprentissage mutuel et d'optimisation. Je recommande une attention particulière à l'évolution de l'agence Marseille dans les semaines à venir.

*Ce rapport a été généré automatiquement par le Système d'Automatisation des Rapports Bancaires.*
"""


def save_report(report, timestamp=None):
    """Enregistre le rapport généré dans un fichier."""
    if not timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    os.makedirs("output", exist_ok=True)
    report_file = f"output/rapport_bancaire_{timestamp}.md"
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"Rapport enregistré dans {report_file}")
    return report_file


def main():
    """Point d'entrée principal du POC."""
    print("=== POC: Analyse de données bancaires avec IA ===\n")
    
    # 1. Générer ou charger des données
    df = generate_sample_data()
    print(f"Données générées: {len(df)} entrées pour {df['agence'].nunique()} agences\n")
    
    # 2. Visualiser les données (optionnel mais utile pour la démonstration)
    visualize_data(df)
    
    # 3. Analyser les données avec un LLM
    report = analyze_data_with_llm(df)
    
    # 4. Enregistrer et afficher le rapport
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_report(report, timestamp)
    
    print("\n=== Extrait du rapport généré ===")
    print(report[:500] + "...\n")
    
    print("POC terminé avec succès!")
    print("Ce POC démontre comment une IA peut être intégrée pour analyser des données bancaires")
    print("et générer automatiquement des rapports détaillés.")
    
    return 0


if __name__ == "__main__":
    main() 
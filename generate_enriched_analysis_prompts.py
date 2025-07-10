#!/usr/bin/env python3
"""
🧠 GÉNÉRATION DE PRÉ-PROMPTS ENRICHIS AVEC HISTORIQUE
===================================================

Script pour générer des pré-prompts d'analyse IA enrichis incluant :
- Données actuelles de la banque/agence  
- Historique des 4-5 dernières semaines
- Analyses LLM précédentes de la même agence
- Comparaisons et tendances

Auteur: Système d'IA Bancaire  
Date: 2025-01-27
"""

import sys
import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_connection():
    """Récupérer la connexion à la base de données."""
    return sqlite3.connect('bankreports.db')

def get_all_agencies():
    """Récupérer la liste de toutes les agences/banques."""
    conn = get_database_connection()
    agencies = pd.read_sql('SELECT DISTINCT agence FROM bank_data ORDER BY agence', conn)
    conn.close()
    return agencies['agence'].tolist()

def get_bank_statistics(agence, semaine):
    """
    Récupère les statistiques bancaires pour une agence et une semaine donnée
    """
    conn = sqlite3.connect('bankreports.db')
    
    try:
        # Récupérer les données pour la semaine spécifique
        query = """
        SELECT 
            agence,
            date,
            montant,
            nombre_transactions,
            created_at
        FROM bank_data 
        WHERE agence = ? AND strftime('%Y-W%W', date) = ?
        ORDER BY date
        """
        
        cursor = conn.cursor()
        cursor.execute(query, (agence, semaine))
        data = cursor.fetchall()
        
        if not data:
            return None
            
        # Calculer les statistiques
        total_montant = sum(row[2] for row in data)
        total_transactions = sum(row[3] for row in data)
        nombre_jours = len(data)
        montant_moyen_jour = total_montant / nombre_jours if nombre_jours > 0 else 0
        transactions_moyenne_jour = total_transactions / nombre_jours if nombre_jours > 0 else 0
        
        # Trouver les pics et creux
        montants = [row[2] for row in data]
        pic_montant = max(montants) if montants else 0
        creux_montant = min(montants) if montants else 0
        
        transactions = [row[3] for row in data]
        pic_transactions = max(transactions) if transactions else 0
        creux_transactions = min(transactions) if transactions else 0
        
        return {
            'agence': agence,
            'semaine': semaine,
            'periode': f"{data[0][1]} à {data[-1][1]}" if data else "N/A",
            'nombre_jours_activite': nombre_jours,
            'montant_total': total_montant,
            'nombre_transactions_total': total_transactions,
            'montant_moyen_jour': montant_moyen_jour,
            'transactions_moyenne_jour': transactions_moyenne_jour,
            'pic_montant': pic_montant,
            'creux_montant': creux_montant,
            'pic_transactions': pic_transactions,
            'creux_transactions': creux_transactions,
            'donnees_detaillees': [
                {
                    'date': row[1],
                    'montant': row[2],
                    'transactions': row[3]
                } for row in data
            ]
        }
        
    finally:
        conn.close()

def get_historical_weeks_data(agence, target_semaine, nb_semaines_precedentes=4):
    """
    Récupère les données des semaines précédentes pour analyse comparative
    """
    conn = sqlite3.connect('bankreports.db')
    
    try:
        # Récupérer toutes les semaines disponibles pour cette agence
        query = """
        SELECT DISTINCT strftime('%Y-W%W', date) as semaine, date
        FROM bank_data 
        WHERE agence = ?
        ORDER BY date DESC
        """
        
        cursor = conn.cursor()
        cursor.execute(query, (agence,))
        available_weeks = cursor.fetchall()
        
        if not available_weeks:
            return []
        
        # Prendre les semaines précédentes (exclut la semaine cible)
        historical_weeks = []
        for semaine, date in available_weeks:
            if semaine != target_semaine and len(historical_weeks) < nb_semaines_precedentes:
                stats = get_bank_statistics(agence, semaine)
                if stats:
                    historical_weeks.append(stats)
        
        return historical_weeks
        
    finally:
        conn.close()

def get_previous_llm_analyses(agence):
    """
    Récupère les analyses LLM précédentes pour cette agence
    """
    conn = sqlite3.connect('bankreports.db')
    
    try:
        # Chercher les analyses existantes pour cette agence
        # Le nom dans analyses est au format "Banque_X_semaine_2025_24"
        agence_pattern = agence.replace(' ', '_')
        
        query = """
        SELECT report, analysis_metadata, created_at
        FROM analyses 
        WHERE analysis_metadata LIKE ?
        ORDER BY created_at DESC
        LIMIT 3
        """
        
        cursor = conn.cursor()
        cursor.execute(query, (f'%{agence_pattern}%',))
        analyses = cursor.fetchall()
        
        previous_analyses = []
        for report, metadata_str, created_at in analyses:
            try:
                metadata = json.loads(metadata_str)
                if metadata.get('type') == 'llm_generated_report':
                    # Extraire un résumé du rapport (premiers 200 caractères)
                    summary = report[:200] + "..." if len(report) > 200 else report
                    previous_analyses.append({
                        'date_analyse': created_at,
                        'semaine_analysee': metadata.get('semaine', 'unknown'),
                        'resume': summary,
                        'validation_status': metadata.get('validation_status', 'unknown')
                    })
            except:
                continue
                
        return previous_analyses
        
    finally:
        conn.close()

def calculate_trends_and_comparisons(current_stats, historical_data):
    """
    Calcule les tendances et comparaisons avec l'historique
    """
    if not historical_data:
        return {
            'evolution_montant': 0,
            'evolution_transactions': 0,
            'tendance': 'Données insuffisantes',
            'performance_relative': 'N/A'
        }
    
    # Calculer les moyennes historiques
    montants_historiques = [week['montant_total'] for week in historical_data]
    transactions_historiques = [week['nombre_transactions_total'] for week in historical_data]
    
    moyenne_historique_montant = sum(montants_historiques) / len(montants_historiques)
    moyenne_historique_transactions = sum(transactions_historiques) / len(transactions_historiques)
    
    # Évolution par rapport à la moyenne historique
    evolution_montant = ((current_stats['montant_total'] - moyenne_historique_montant) / moyenne_historique_montant * 100) if moyenne_historique_montant > 0 else 0
    evolution_transactions = ((current_stats['nombre_transactions_total'] - moyenne_historique_transactions) / moyenne_historique_transactions * 100) if moyenne_historique_transactions > 0 else 0
    
    # Déterminer la tendance
    if evolution_montant > 10:
        tendance = "Forte croissance"
    elif evolution_montant > 2:
        tendance = "Croissance modérée"
    elif evolution_montant > -2:
        tendance = "Stable"
    elif evolution_montant > -10:
        tendance = "Déclin modéré"
    else:
        tendance = "Forte baisse"
    
    # Performance relative
    if evolution_montant > 5 and evolution_transactions > 5:
        performance_relative = "Excellente"
    elif evolution_montant > 0 and evolution_transactions > 0:
        performance_relative = "Bonne"
    elif evolution_montant > -5 and evolution_transactions > -5:
        performance_relative = "Correcte"
    else:
        performance_relative = "Préoccupante"
    
    return {
        'evolution_montant': evolution_montant,
        'evolution_transactions': evolution_transactions,
        'tendance': tendance,
        'performance_relative': performance_relative,
        'moyenne_historique_montant': moyenne_historique_montant,
        'moyenne_historique_transactions': moyenne_historique_transactions
    }

def create_enriched_analysis_prompt(agence, current_stats, historical_data, previous_analyses, trends):
    """
    Créer le pré-prompt enrichi avec historique et analyses précédentes
    """
    
    if not current_stats:
        return f"""
=== PRÉ-PROMPT D'ANALYSE IA ENRICHI ===
AGENCE: {agence}
STATUT: AUCUNE DONNÉE DISPONIBLE

Aucune donnée n'est disponible pour cette agence dans la période analysée.
Ce prompt ne peut pas être envoyé à un LLM car il n'y a pas de données à analyser.
"""

    # Formatage des montants
    montant_total_formatted = f"{current_stats['montant_total']:,.2f} €"
    montant_moyen_formatted = f"{current_stats['montant_moyen_jour']:,.2f} €"
    
    prompt = f"""=== PRÉ-PROMPT D'ANALYSE IA ENRICHI ===
AGENCE: {agence}
PÉRIODE ANALYSÉE: {current_stats['periode']}
DATE GÉNÉRATION: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

RÔLE: Tu es un analyste financier expert spécialisé dans l'analyse bancaire avec accès à l'historique.

CONTEXTE: Analyser les données bancaires actuelles ET historiques pour générer un rapport directorial complet avec perspectives temporelles.

📊 DONNÉES ACTUELLES - SEMAINE {current_stats['semaine']}:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Montant total: {montant_total_formatted}
• Transactions totales: {current_stats['nombre_transactions_total']}
• Montant moyen/jour: {montant_moyen_formatted}
• Transactions moyennes/jour: {current_stats['transactions_moyenne_jour']:.1f}
• Jours d'activité: {current_stats['nombre_jours_activite']}
• Pic montant: {current_stats['pic_montant']:,.2f} €
• Creux montant: {current_stats['creux_montant']:,.2f} €

📈 ANALYSE COMPARATIVE ET TENDANCES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Évolution montant vs historique: {trends['evolution_montant']:+.1f}%
• Évolution transactions vs historique: {trends['evolution_transactions']:+.1f}%
• Tendance globale: {trends['tendance']}
• Performance relative: {trends['performance_relative']}
• Moyenne historique montant: {trends['moyenne_historique_montant']:,.2f} €
• Moyenne historique transactions: {trends['moyenne_historique_transactions']:.0f}"""

    # Ajouter l'historique détaillé
    if historical_data:
        prompt += f"""

📚 HISTORIQUE DES {len(historical_data)} DERNIÈRES SEMAINES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        for i, week_data in enumerate(historical_data[:4], 1):
            prompt += f"""
Semaine {i} ({week_data['semaine']}): {week_data['montant_total']:,.2f} € | {week_data['nombre_transactions_total']} transactions"""

    # Ajouter les analyses LLM précédentes
    if previous_analyses:
        prompt += f"""

🧠 ANALYSES IA PRÉCÉDENTES ({len(previous_analyses)} disponibles):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        for i, analysis in enumerate(previous_analyses[:2], 1):
            prompt += f"""
Analyse {i} (du {analysis['date_analyse'][:10]}):
"{analysis['resume']}"
Statut: {analysis['validation_status']}"""

    # Instructions détaillées pour l'IA
    prompt += f"""

🎯 INSTRUCTIONS DÉTAILLÉES POUR L'ANALYSE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. ANALYSER LA PERFORMANCE ACTUELLE de {agence} (semaine {current_stats['semaine']})
2. COMPARER avec l'historique des {len(historical_data) if historical_data else 0} semaines précédentes
3. IDENTIFIER les tendances, variations et anomalies significatives
4. ÉVALUER la performance relative ({trends['performance_relative']}) et expliquer les causes
5. INTÉGRER les insights des analyses précédentes si disponibles
6. PROPOSER des recommandations stratégiques basées sur l'ensemble des données
7. RÉDIGER un rapport exécutif structuré en français professionnel

📋 STRUCTURE OBLIGATOIRE DU RAPPORT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• RÉSUMÉ EXÉCUTIF (3 lignes maximum)
• PERFORMANCE SEMAINE ACTUELLE
• ANALYSE COMPARATIVE HISTORIQUE
• TENDANCES ET INSIGHTS CLÉS
• RECOMMANDATIONS STRATÉGIQUES  
• CONCLUSION ET PROCHAINES ÉTAPES

⚠️ CONTRAINTES IMPORTANTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Rapport en français professionnel
• Destiné au directeur général du groupe
• Maximum 600 mots
• Utiliser uniquement les données fournies
• Ton factuel et constructif
• Chiffres précis avec contexte
• Recommandations concrètes et actionnables

=== FIN DU PRÉ-PROMPT ENRICHI ===
"""
    
    return prompt

def generate_week_identifier():
    """Générer un identifiant de semaine basé sur la date actuelle."""
    now = datetime.now()
    week_number = now.isocalendar()[1]
    return f"semaine_{now.year}_{week_number:02d}"

def sanitize_filename(name):
    """Nettoyer un nom pour utilisation dans un nom de fichier."""
    return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()

def main():
    """Fonction principale"""
    print("🧠 GÉNÉRATION DE PRÉ-PROMPTS ENRICHIS")
    print("=" * 60)
    
    # Obtenir la semaine cible
    target_week = "2025-W07"  # Dernière semaine avec données
    print(f"📅 Semaine cible: {target_week}")
    
    # Créer les répertoires de sortie
    base_dir = Path("prompts_analysis")
    enriched_prompts_dir = base_dir / "enriched_prompts"
    enriched_responses_dir = base_dir / "enriched_responses"
    
    enriched_prompts_dir.mkdir(parents=True, exist_ok=True)
    enriched_responses_dir.mkdir(parents=True, exist_ok=True)
    
    # Obtenir toutes les agences
    agencies = get_all_agencies()
    print(f"🏦 Agences trouvées: {len(agencies)}")
    
    processed = 0
    with_data = 0
    with_history = 0
    with_previous_analyses = 0
    
    for agence in agencies:
        print(f"📍 Traitement: {agence}")
        
        # Données actuelles
        current_stats = get_bank_statistics(agence, target_week)
        
        if current_stats:
            with_data += 1
            
            # Données historiques
            historical_data = get_historical_weeks_data(agence, target_week, nb_semaines_precedentes=5)
            if historical_data:
                with_history += 1
            
            # Analyses précédentes
            previous_analyses = get_previous_llm_analyses(agence)
            if previous_analyses:
                with_previous_analyses += 1
            
            # Calculs des tendances
            trends = calculate_trends_and_comparisons(current_stats, historical_data)
            
            # Générer le prompt enrichi
            enriched_prompt = create_enriched_analysis_prompt(
                agence, current_stats, historical_data, previous_analyses, trends
            )
            
            # Sauvegarder le prompt
            safe_name = sanitize_filename(agence)
            prompt_filename = f"enriched_prompt_{safe_name}.txt"
            response_filename = f"enriched_mail_{safe_name}.txt"
            
            with open(enriched_prompts_dir / prompt_filename, 'w', encoding='utf-8') as f:
                f.write(enriched_prompt)
            
            # Créer un template de réponse
            response_template = f"""[RAPPORT À COMPLÉTER AVEC L'IA]

AGENCE: {agence}
SEMAINE: {target_week}
DONNÉES HISTORIQUES: {len(historical_data)} semaines
ANALYSES PRÉCÉDENTES: {len(previous_analyses)}

Ce fichier doit être rempli avec la réponse du LLM après traitement du prompt enrichi.
"""
            
            with open(enriched_responses_dir / response_filename, 'w', encoding='utf-8') as f:
                f.write(response_template)
            
            processed += 1
        
        else:
            print(f"   ⚠️  Aucune donnée pour {agence}")
    
    # Résumé final
    print(f"\n🎯 RÉSUMÉ GÉNÉRATION ENRICHIE:")
    print(f"═══════════════════════════════════════")
    print(f"✅ Agences traitées: {processed}/{len(agencies)}")
    print(f"📊 Avec données actuelles: {with_data}")
    print(f"📈 Avec historique: {with_history}")
    print(f"🧠 Avec analyses précédentes: {with_previous_analyses}")
    print(f"📁 Prompts générés: {enriched_prompts_dir}")
    print(f"📝 Templates réponses: {enriched_responses_dir}")
    
    print(f"\n💡 AMÉLIORATIONS APPORTÉES:")
    print(f"   • Intégration de l'historique des 5 dernières semaines")
    print(f"   • Comparaisons et calculs de tendances automatiques")
    print(f"   • Inclusion des analyses LLM précédentes")
    print(f"   • Prompts structurés avec métriques enrichies")
    print(f"   • Instructions détaillées pour l'IA")

if __name__ == "__main__":
    main()
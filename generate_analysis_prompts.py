#!/usr/bin/env python3
"""
Script pour générer les pré-prompts d'analyse IA avec les vraies données de chaque banque.
Ce script extrait les données de chaque banque/agence depuis la BDD et génère les prompts 
prêts à être envoyés à un LLM.
"""

import sys
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_connection():
    """Obtenir une connexion à la base de données."""
    return sqlite3.connect("bankreports.db")

def get_all_agencies():
    """Récupérer la liste de toutes les agences/banques."""
    conn = get_database_connection()
    try:
        try:
    agencies = pd.read_sql('SELECT DISTINCT agence FROM bank_data ORDER BY agence', conn)
        except Exception:
            agencies = pd.read_sql('SELECT DISTINCT agence FROM bank_data_enriched ORDER BY agence', conn)
    finally:
    conn.close()
    return agencies['agence'].tolist()

def get_latest_week_data(agence, weeks_back=1):
    """Récupérer les données de la dernière semaine pour une agence donnée."""
    conn = get_database_connection()
    try:
        # Utiliser directement bank_data_enriched qui contient les vraies données
        max_date_query = f"SELECT MAX(date_semaine) as max_date FROM bank_data_enriched WHERE agence = ?"
        max_date = pd.read_sql(max_date_query, conn, params=(agence,)).iloc[0]['max_date']
        if pd.isna(max_date):
            return pd.DataFrame()
        week_data_query = f"SELECT * FROM bank_data_enriched WHERE agence = ? AND date_semaine = ?"
        df = pd.read_sql(week_data_query, conn, params=(agence, max_date))
    finally:
        conn.close()
    return df

def calculate_agency_statistics(df):
    """
    Calculer les statistiques pour une agence à partir de toutes les colonnes disponibles.
    """
    columns = [
        'semaine_id', 'annee', 'numero_semaine', 'date_semaine', 'groupe', 'agence',
        'occ_part', 'conso_dec', 'bilan_net', 'vers_ep_fi', 'vb_iard_part', 'vb_prev_part',
        'vb_ass_peri_pea_hiss', 'tx_occ_part_soc', 'moy_part', 'somme_part', 'rang_part',
        'occ_pro', 'occ_pro_cible', 'eqpt_dec', 'vb_iard_pro', 'vb_prev_pro', 'vb_contr_comm',
        'coll_pro_net', 'tx_occ_pro_soc', 'moy_pro', 'somme_pro', 'rang_pro', 'moy_global',
        'somme_rang', 'rang_global'
    ]
    stats = {col: (df[col].sum() if col in df and pd.api.types.is_numeric_dtype(df[col]) else df[col].iloc[0] if col in df and not df.empty else 0) for col in columns}
    stats["has_data"] = not df.empty
    stats["period_start"] = df["date_semaine"].min() if "date_semaine" in df else None
    stats["period_end"] = df["date_semaine"].max() if "date_semaine" in df else None
    return stats

def create_analysis_prompt(agence, stats):
    """
    Créer un prompt complet pour ChatGPT qui génère un email de compte rendu d'analyse.
    """
    if not stats["has_data"]:
        return f"""
=== PROMPT COMPLET POUR CHATGPT ===
AGENCE: {agence}
STATUT: AUCUNE DONNÉE DISPONIBLE

INSTRUCTIONS:
Vous êtes un analyste financier expérimenté. Générer un email de compte rendu pour l'agence {agence}.

DONNÉES:
Aucune donnée disponible pour cette agence dans la période analysée.

RÉPONSE ATTENDUE:
Un email professionnel expliquant qu'aucune donnée n'est disponible pour cette période.
"""
    
    # Formater les données pour une meilleure lisibilité
    formatted_data = f"""
DONNÉES DE L'AGENCE {agence} - SEMAINE {stats['numero_semaine']} {stats['annee']}:
• Période: {stats['period_start']} au {stats['period_end']}
• Groupe: {stats['groupe']}

INDICATEURS CLÉS:
• Consommation déclarée (CONSO_DEC): {stats['conso_dec']:,.2f} €
• Bilan net (BILAN_NET): {stats['bilan_net']:,.2f} €
• Versements épargne financière (VERS_EP_FI): {stats['vers_ep_fi']:,.2f} €
• Équipement déclaré (EQPT_DEC): {stats['eqpt_dec']:,.2f} €
• Collecte professionnelle nette (COLL_PRO_NET): {stats['coll_pro_net']:,.2f} €

ACTIVITÉ PARTICULIERS:
• Occurrences particuliers (OCC_PART): {stats['occ_part']}
• Ventes bancaires IARD particuliers (VB_IARD_PART): {stats['vb_iard_part']}
• Ventes bancaires prévoyance particuliers (VB_PREV_PART): {stats['vb_prev_part']}
• Ventes bancaires assurance/PEA/HISS (VB_ASS_PERI_PEA_HISS): {stats['vb_ass_peri_pea_hiss']}
• Taux d'occurrence particuliers (TX_OCC_PART_SOC): {stats['tx_occ_part_soc']:.2f}%
• Moyenne particuliers (MOY_PART): {stats['moy_part']:.2f}
• Somme particuliers (SOMME_PART): {stats['somme_part']}
• Rang particuliers (RANG_PART): {stats['rang_part']}

ACTIVITÉ PROFESSIONNELLE:
• Occurrences professionnels (OCC_PRO): {stats['occ_pro']}
• Occurrences professionnels cible (OCC_PRO_CIBLE): {stats['occ_pro_cible']}
• Ventes bancaires IARD professionnels (VB_IARD_PRO): {stats['vb_iard_pro']}
• Ventes bancaires prévoyance professionnels (VB_PREV_PRO): {stats['vb_prev_pro']}
• Ventes bancaires contrats commerciaux (VB_CONTR_COMM): {stats['vb_contr_comm']}
• Taux d'occurrence professionnels (TX_OCC_PRO_SOC): {stats['tx_occ_pro_soc']:.2f}%
• Moyenne professionnels (MOY_PRO): {stats['moy_pro']:.2f}
• Somme professionnels (SOMME_PRO): {stats['somme_pro']}
• Rang professionnels (RANG_PRO): {stats['rang_pro']}

INDICATEURS GLOBAUX:
• Moyenne globale (MOY_GLOBAL): {stats['moy_global']:.2f}
• Somme rang (SOMME_RANG): {stats['somme_rang']}
• Rang global (RANG_GLOBAL): {stats['rang_global']}
"""

    prompt = f"""
=== PROMPT COMPLET POUR CHATGPT ===

INSTRUCTIONS:
Vous êtes un analyste financier expérimenté spécialisé dans l'analyse bancaire. Vous devez générer un email de compte rendu hebdomadaire professionnel pour les directeurs d'agence.

CONTEXTE:
{formatted_data}

TÂCHE:
Rédiger un email de compte rendu hebdomadaire qui sera envoyé aux directeurs de l'agence {agence}.

STRUCTURE ATTENDUE:
1. **Objet du mail** : Compte rendu hebdomadaire - {agence} - Semaine {stats['numero_semaine']} {stats['annee']}

2. **Corps du mail** :
   - Salutation professionnelle
   - Synthèse des résultats clés (3-4 points principaux)
   - Analyse détaillée par segment (particuliers vs professionnels)
   - Points forts de la semaine
   - Axes d'amélioration identifiés
   - Alertes ou points d'attention
   - Recommandations concrètes pour la semaine suivante
   - Signature professionnelle

STYLE:
- Ton professionnel mais accessible
- Données chiffrées précises
- Analyse factuelle et constructive
- Recommandations actionnables
- Longueur : 200-300 mots

FORMAT DE SORTIE:
Générer uniquement le contenu de l'email (objet + corps), sans commentaires supplémentaires.

RÉPONSE ATTENDUE:
[Générer ici l'email complet]
"""
    
    return prompt

def generate_week_identifier():
    """Générer un identifiant de semaine basé sur la date actuelle."""
    now = datetime.now()
    # Format: semaine_YYYY_WW (année + numéro de semaine)
    week_number = now.isocalendar()[1]
    return f"semaine_{now.year}_{week_number:02d}"

def sanitize_filename(name):
    """Nettoyer un nom pour utilisation dans un nom de fichier."""
    # Remplacer les caractères non autorisés
    name = name.replace(" ", "_")
    name = name.replace("/", "_")
    name = name.replace("\\", "_")
    name = name.replace(":", "_")
    return name

def main():
    """Fonction principale."""
    logger.info("=== GÉNÉRATION DES PRÉ-PROMPTS D'ANALYSE IA ===")
    
    # Récupérer toutes les agences
    logger.info("Récupération de la liste des agences...")
    agencies = get_all_agencies()
    logger.info(f"Trouvé {len(agencies)} agences/banques dans la base de données")
    
    # Identifier la semaine actuelle
    week_id = generate_week_identifier()
    logger.info(f"Génération pour la période: {week_id}")
    
    # Créer les dossiers s'ils n'existent pas
    enriched_preprompts_dir = Path("prompts_analysis/enriched_preprompts")
    responses_dir = Path("prompts_analysis/llm_responses")
    enriched_preprompts_dir.mkdir(parents=True, exist_ok=True)
    responses_dir.mkdir(parents=True, exist_ok=True)
    
    generated_count = 0
    empty_count = 0
    
    # Générer les prompts pour chaque agence
    for i, agence in enumerate(agencies, 1):
        logger.info(f"[{i}/{len(agencies)}] Traitement de l'agence: {agence}")
        
        try:
            # Récupérer les données de la dernière semaine
            df = get_latest_week_data(agence, weeks_back=1)
            
            # Calculer les statistiques
            stats = calculate_agency_statistics(df)
            
            # Créer le prompt
            prompt = create_analysis_prompt(agence, stats)
            
            # Nom de fichier sécurisé
            safe_agence_name = sanitize_filename(agence)
            
            # Sauvegarder le prompt
            prompt_filename = f"preprompt_{safe_agence_name}_{week_id}.txt"
            prompt_filepath = enriched_preprompts_dir / prompt_filename
            
            with open(prompt_filepath, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            # Créer le fichier de réponse vide correspondant
            response_filename = f"mail_{safe_agence_name}_{week_id}.txt"
            response_filepath = responses_dir / response_filename
            
            if not response_filepath.exists():  # Ne pas écraser s'il existe déjà
                response_content = f"""=== RÉPONSE LLM POUR {agence} ===
SEMAINE: {week_id}
FICHIER PROMPT SOURCE: {prompt_filename}

[Coller ici la réponse du LLM pour l'agence {agence}]

=== INSTRUCTIONS ===
1. Copiez le contenu du fichier {prompt_filename}
2. Envoyez-le à votre LLM préféré 
3. Collez la réponse complète du LLM ci-dessous
4. Sauvegardez ce fichier

=== RÉPONSE LLM ===
[Réponse à coller ici]
"""
                with open(response_filepath, 'w', encoding='utf-8') as f:
                    f.write(response_content)
            
            if stats["has_data"]:
                generated_count += 1
                logger.info(f"  ✅ Prompt généré avec données pour {agence}")
            else:
                empty_count += 1
                logger.info(f"  ⚠️  Aucune donnée disponible")
                
        except Exception as e:
            logger.error(f"  ❌ Erreur lors du traitement de {agence}: {str(e)}")
            empty_count += 1
    
    # Résumé final
    logger.info("\n=== RÉSUMÉ DE LA GÉNÉRATION ===")
    logger.info(f"Total agences traitées: {len(agencies)}")
    logger.info(f"Prompts générés avec données: {generated_count}")
    logger.info(f"Prompts sans données: {empty_count}")
    logger.info(f"Semaine analysée: {week_id}")
    logger.info(f"\nFichiers générés dans:")
    logger.info(f"  - Prompts: {enriched_preprompts_dir}")
    logger.info(f"  - Réponses (à remplir): {responses_dir}")
    
    # Instructions pour l'utilisateur
    print(f"\n🎯 PROCHAINES ÉTAPES:")
    print(f"1. Examinez les fichiers dans {enriched_preprompts_dir}/")
    print(f"2. Copiez les prompts vers votre LLM préféré")
    print(f"3. Collez les réponses dans {responses_dir}/")
    print(f"4. Analysez l'efficacité des prompts et des données")

if __name__ == "__main__":
    main() 
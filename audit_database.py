#!/usr/bin/env python3
"""
Script pour faire un audit complet de la base de données.
"""

import sqlite3
import pandas as pd
from datetime import datetime

def audit_database():
    """Auditer complètement la base de données."""
    conn = sqlite3.connect('bankreports.db')
    
    print('=== AUDIT COMPLET DE LA BASE DE DONNÉES ===\n')
    
    # 1. Lister toutes les tables
    tables = pd.read_sql('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name', conn)
    print(f'📊 TABLES EXISTANTES ({len(tables)}):')
    for table in tables['name']:
        print(f'  - {table}')
    
    print('\n' + '='*60 + '\n')
    
    # 2. Structure détaillée de chaque table
    for table_name in tables['name']:
        if table_name == 'alembic_version':
            continue
            
        print(f'📋 STRUCTURE DE LA TABLE "{table_name}":')
        
        try:
            # Schema
            schema = pd.read_sql(f'PRAGMA table_info({table_name})', conn)
            print('  Colonnes:')
            for _, row in schema.iterrows():
                nullable = 'NULL' if row['notnull'] == 0 else 'NOT NULL'
                default = f' DEFAULT {row["dflt_value"]}' if row['dflt_value'] is not None else ''
                pk = ' (PRIMARY KEY)' if row['pk'] == 1 else ''
                print(f'    - {row["name"]}: {row["type"]} {nullable}{default}{pk}')
            
            # Nombre de lignes
            count = pd.read_sql(f'SELECT COUNT(*) as count FROM {table_name}', conn)
            print(f'  Nombre de lignes: {count.iloc[0]["count"]}')
            
            # Échantillon de données si la table n'est pas vide
            if count.iloc[0]['count'] > 0:
                sample = pd.read_sql(f'SELECT * FROM {table_name} LIMIT 3', conn)
                print('  Échantillon:')
                for _, row in sample.iterrows():
                    print(f'    {dict(row)}')
                    
        except Exception as e:
            print(f'  Erreur: {e}')
        
        print('\n' + '-'*50 + '\n')
    
    # 3. Analyse spécifique pour bank_data
    print('🔍 ANALYSE SPÉCIFIQUE DE LA TABLE BANK_DATA:')
    try:
        # Période couverte
        date_range = pd.read_sql('SELECT MIN(date) as min_date, MAX(date) as max_date FROM bank_data', conn)
        print(f'  Période: {date_range.iloc[0]["min_date"]} à {date_range.iloc[0]["max_date"]}')
        
        # Nombre d'agences
        agencies = pd.read_sql('SELECT COUNT(DISTINCT agence) as count FROM bank_data', conn)
        print(f'  Nombre d\'agences: {agencies.iloc[0]["count"]}')
        
        # Top 5 des agences par volume
        top_agencies = pd.read_sql('''
            SELECT agence, 
                   SUM(montant) as total_montant,
                   SUM(nombre_transactions) as total_transactions,
                   COUNT(*) as nb_enregistrements
            FROM bank_data 
            GROUP BY agence 
            ORDER BY total_montant DESC 
            LIMIT 5
        ''', conn)
        print('  Top 5 agences par montant:')
        for _, row in top_agencies.iterrows():
            print(f'    {row["agence"]}: {row["total_montant"]:,.2f}€ ({row["total_transactions"]} trans., {row["nb_enregistrements"]} enreg.)')
        
    except Exception as e:
        print(f'  Erreur dans l\'analyse: {e}')
    
    print('\n' + '='*60 + '\n')
    
    # 4. Recommandations pour stocker les rapports LLM
    print('💡 RECOMMANDATIONS POUR STOCKER LES RAPPORTS LLM:')
    print('''
1. CRÉER UNE NOUVELLE TABLE "llm_reports":
   - id: INTEGER PRIMARY KEY
   - bank_name: VARCHAR (nom de la banque)
   - report_week: VARCHAR (semaine analysée, ex: "semaine_2025_24")
   - prompt_content: TEXT (contenu du pré-prompt)
   - llm_response: TEXT (réponse du LLM)
   - created_at: DATETIME
   - metadata: JSON (informations additionnelles)

2. CRÉER UNE TABLE "prompt_analysis":
   - id: INTEGER PRIMARY KEY
   - llm_report_id: INTEGER FOREIGN KEY
   - prompt_quality_score: INTEGER (1-10)
   - response_quality_score: INTEGER (1-10)
   - analysis_notes: TEXT
   - created_at: DATETIME

3. UTILISER LA TABLE EXISTANTE "analyses" si elle correspond:
   - Vérifier si elle peut stocker nos données LLM
   - Adapter si nécessaire

4. CRÉER DES INDEX pour les performances:
   - INDEX sur bank_name + report_week
   - INDEX sur created_at
''')
    
    conn.close()

if __name__ == "__main__":
    audit_database() 
#!/usr/bin/env python3
"""
Script de consolidation des bases de données
Crée une base unique avec toutes les données importantes du projet
"""

import sqlite3
import os
import shutil
from datetime import datetime

def consolidate_databases():
    """Consolide toutes les bases de données en une seule"""
    
    print("🔧 CONSOLIDATION DES BASES DE DONNÉES")
    print("=" * 50)
    
    # Sauvegarder la base actuelle
    backup_name = f"bankreports_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    if os.path.exists("bankreports.db"):
        shutil.copy("bankreports.db", backup_name)
        print(f"✅ Sauvegarde créée : {backup_name}")
    
    # Créer une nouvelle base consolidée
    consolidated_db = "bankreports_consolidated.db"
    
    # Supprimer si elle existe déjà
    if os.path.exists(consolidated_db):
        os.remove(consolidated_db)
    
    print(f"📦 Création de la base consolidée : {consolidated_db}")
    
    # 1. Copier la structure et les données enrichies de bankreports.db
    print("\n1️⃣ Copie des données enrichies...")
    shutil.copy("bankreports.db", consolidated_db)
    
    # 2. Ajouter les tables manquantes depuis bankreports_backup.db
    print("2️⃣ Ajout des tables manquantes...")
    
    # Connexion aux bases
    consolidated_conn = sqlite3.connect(consolidated_db)
    backup_conn = sqlite3.connect("bankreports_backup.db")
    
    # Obtenir la structure des tables depuis backup
    backup_cursor = backup_conn.cursor()
    consolidated_cursor = consolidated_conn.cursor()
    
    # Tables à migrer
    tables_to_migrate = [
        'users',
        'analyses', 
        'scheduled_reports',
        'visualizations',
        'alembic_version'
    ]
    
    for table in tables_to_migrate:
        try:
            # Vérifier si la table existe dans backup
            backup_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if backup_cursor.fetchone():
                print(f"   📋 Migration de la table : {table}")
                
                # Obtenir la structure de la table
                backup_cursor.execute(f"PRAGMA table_info({table})")
                columns = backup_cursor.fetchall()
                
                # Créer la table dans la base consolidée
                column_defs = []
                for col in columns:
                    col_name, col_type, not_null, default_val, pk = col[1], col[2], col[3], col[4], col[5]
                    col_def = f"{col_name} {col_type}"
                    if not_null:
                        col_def += " NOT NULL"
                    if default_val is not None:
                        col_def += f" DEFAULT {default_val}"
                    if pk:
                        col_def += " PRIMARY KEY"
                    column_defs.append(col_def)
                
                create_sql = f"CREATE TABLE {table} ({', '.join(column_defs)})"
                consolidated_cursor.execute(create_sql)
                
                # Copier les données
                backup_cursor.execute(f"SELECT * FROM {table}")
                rows = backup_cursor.fetchall()
                
                if rows:
                    # Obtenir les noms de colonnes
                    backup_cursor.execute(f"PRAGMA table_info({table})")
                    column_names = [col[1] for col in backup_cursor.fetchall()]
                    
                    # Préparer la requête d'insertion
                    placeholders = ', '.join(['?' for _ in column_names])
                    insert_sql = f"INSERT INTO {table} ({', '.join(column_names)}) VALUES ({placeholders})"
                    
                    # Insérer les données
                    consolidated_cursor.executemany(insert_sql, rows)
                    print(f"      ✅ {len(rows)} enregistrements migrés")
                else:
                    print(f"      ℹ️  Table vide")
                    
        except Exception as e:
            print(f"      ⚠️  Erreur lors de la migration de {table}: {e}")
    
    # 3. Migrer les emails depuis backup
    print("\n3️⃣ Migration des emails...")
    try:
        backup_cursor.execute("SELECT * FROM email_reports")
        emails = backup_cursor.fetchall()
        
        if emails:
            # Vider la table email_reports existante
            consolidated_cursor.execute("DELETE FROM email_reports")
            
            # Obtenir la structure
            backup_cursor.execute("PRAGMA table_info(email_reports)")
            column_names = [col[1] for col in backup_cursor.fetchall()]
            
            # Insérer les emails
            placeholders = ', '.join(['?' for _ in column_names])
            insert_sql = f"INSERT INTO email_reports ({', '.join(column_names)}) VALUES ({placeholders})"
            consolidated_cursor.executemany(insert_sql, emails)
            print(f"   ✅ {len(emails)} emails migrés")
        else:
            print("   ℹ️  Aucun email à migrer")
    except Exception as e:
        print(f"   ⚠️  Erreur lors de la migration des emails: {e}")
    
    # Valider les changements
    consolidated_conn.commit()
    
    # Vérifier le résultat
    print("\n4️⃣ Vérification de la base consolidée...")
    consolidated_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in consolidated_cursor.fetchall()]
    print(f"   📋 Tables présentes : {', '.join(tables)}")
    
    # Compter les données
    print("\n5️⃣ Statistiques de la base consolidée :")
    for table in ['users', 'email_reports', 'bank_data_enriched', 'analyses', 'scheduled_reports', 'execution_logs']:
        try:
            consolidated_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = consolidated_cursor.fetchone()[0]
            print(f"   📊 {table}: {count} enregistrements")
        except:
            print(f"   📊 {table}: table non trouvée")
    
    # Fermer les connexions
    backup_conn.close()
    consolidated_conn.close()
    
    # Remplacer la base actuelle
    print(f"\n6️⃣ Remplacement de la base actuelle...")
    shutil.move(consolidated_db, "bankreports.db")
    
    print("\n🎉 CONSOLIDATION TERMINÉE AVEC SUCCÈS !")
    print("=" * 50)
    print("✅ Base unique créée : bankreports.db")
    print("✅ Toutes les données importantes migrées")
    print("✅ Prêt pour le déploiement")
    print(f"✅ Sauvegarde conservée : {backup_name}")
    
    return True

if __name__ == "__main__":
    try:
        consolidate_databases()
    except Exception as e:
        print(f"❌ Erreur lors de la consolidation : {e}")
        exit(1) 
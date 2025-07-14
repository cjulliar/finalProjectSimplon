#!/usr/bin/env python3
"""
Script de sauvegarde automatique de la base de production
"""

import os
import shutil
import sqlite3
from datetime import datetime

def backup_production_database():
    """Sauvegarde la base de production"""
    
    print("💾 SAUVEGARDE DE LA BASE DE PRODUCTION")
    print("=" * 50)
    
    # Chemin de la base de production
    production_db = "bankreports.db"
    
    if not os.path.exists(production_db):
        print(f"❌ Base de production non trouvée : {production_db}")
        return False
    
    # Créer le nom de la sauvegarde avec timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"bankreports_production_backup_{timestamp}.db"
    
    try:
        # Copier la base de production
        shutil.copy2(production_db, backup_name)
        
        # Vérifier l'intégrité de la sauvegarde
        conn = sqlite3.connect(backup_name)
        cursor = conn.cursor()
        
        # Vérifier les tables principales
        cursor.execute("SELECT COUNT(*) FROM auth_user")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM email_reports")
        email_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bank_data_enriched")
        bank_data_count = cursor.fetchone()[0]
        
        conn.close()
        
        # Taille de la sauvegarde
        backup_size = os.path.getsize(backup_name) / (1024 * 1024)  # MB
        
        print(f"✅ Sauvegarde créée : {backup_name}")
        print(f"📊 Taille : {backup_size:.1f} MB")
        print(f"👥 Utilisateurs : {user_count}")
        print(f"📧 Emails : {email_count}")
        print(f"🏦 Données bancaires : {bank_data_count}")
        
        # Nettoyer les anciennes sauvegardes (garder seulement les 5 plus récentes)
        cleanup_old_backups()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde : {e}")
        return False

def cleanup_old_backups():
    """Nettoie les anciennes sauvegardes (garde seulement les 5 plus récentes)"""
    
    backup_files = []
    for file in os.listdir('.'):
        if file.startswith('bankreports_production_backup_') and file.endswith('.db'):
            backup_files.append(file)
    
    if len(backup_files) > 5:
        # Trier par date de modification (plus ancien en premier)
        backup_files.sort(key=lambda x: os.path.getmtime(x))
        
        # Supprimer les plus anciens
        files_to_delete = backup_files[:-5]
        
        for file in files_to_delete:
            try:
                os.remove(file)
                print(f"🗑️  Ancienne sauvegarde supprimée : {file}")
            except Exception as e:
                print(f"⚠️  Erreur lors de la suppression de {file} : {e}")

def list_backups():
    """Liste toutes les sauvegardes disponibles"""
    
    print("\n📋 SAUVEGARDES DISPONIBLES")
    print("=" * 30)
    
    backup_files = []
    for file in os.listdir('.'):
        if file.startswith('bankreports_production_backup_') and file.endswith('.db'):
            backup_files.append(file)
    
    if not backup_files:
        print("Aucune sauvegarde trouvée")
        return
    
    # Trier par date de modification (plus récent en premier)
    backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    for i, file in enumerate(backup_files, 1):
        mtime = datetime.fromtimestamp(os.path.getmtime(file))
        size = os.path.getsize(file) / (1024 * 1024)  # MB
        
        print(f"{i:2d}. {file}")
        print(f"    📅 {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"    📊 {size:.1f} MB")

def restore_backup(backup_file):
    """Restaure une sauvegarde"""
    
    if not os.path.exists(backup_file):
        print(f"❌ Sauvegarde non trouvée : {backup_file}")
        return False
    
    print(f"🔄 RESTAURATION DE LA SAUVEGARDE : {backup_file}")
    print("=" * 50)
    
    # Sauvegarder la base actuelle avant restauration
    current_backup = f"bankreports_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2("bankreports.db", current_backup)
    print(f"✅ Sauvegarde de la base actuelle : {current_backup}")
    
    try:
        # Restaurer la sauvegarde
        shutil.copy2(backup_file, "bankreports.db")
        print(f"✅ Base restaurée depuis : {backup_file}")
        
        # Vérifier l'intégrité
        conn = sqlite3.connect("bankreports.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM auth_user")
        user_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"✅ Vérification : {user_count} utilisateurs dans la base restaurée")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la restauration : {e}")
        return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Sauvegarde et restauration de la base de production')
    parser.add_argument('action', choices=['backup', 'list', 'restore'], help='Action à effectuer')
    parser.add_argument('--file', help='Fichier de sauvegarde pour la restauration')
    
    args = parser.parse_args()
    
    if args.action == 'backup':
        backup_production_database()
    elif args.action == 'list':
        list_backups()
    elif args.action == 'restore':
        if not args.file:
            print("❌ Veuillez spécifier un fichier de sauvegarde avec --file")
            exit(1)
        restore_backup(args.file) 
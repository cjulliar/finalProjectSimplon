#!/usr/bin/env python3
"""
Script pour vérifier le contenu des bases de données et faire le ménage.
"""
import sqlite3
import os
from pathlib import Path

def check_database_content():
    """Vérifier le contenu des deux bases de données."""
    print("🔍 VÉRIFICATION DES BASES DE DONNÉES")
    print("=" * 50)
    
    # Vérifier l'ancienne base
    old_db = "bankreports.db"
    new_db = "bankreports_enriched.db"
    
    if Path(old_db).exists():
        print(f"\n📊 ANCIENNE BASE: {old_db}")
        print("-" * 30)
        
        conn_old = sqlite3.connect(old_db)
        cursor_old = conn_old.cursor()
        
        # Lister les tables
        cursor_old.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor_old.fetchall()
        print(f"   Tables: {[t[0] for t in tables]}")
        
        # Compter les enregistrements dans chaque table
        for table in tables:
            table_name = table[0]
            try:
                cursor_old.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor_old.fetchone()[0]
                print(f"   {table_name}: {count:,} enregistrements")
            except Exception as e:
                print(f"   {table_name}: Erreur - {e}")
        
        conn_old.close()
    
    if Path(new_db).exists():
        print(f"\n📊 NOUVELLE BASE: {new_db}")
        print("-" * 30)
        
        conn_new = sqlite3.connect(new_db)
        cursor_new = conn_new.cursor()
        
        # Lister les tables
        cursor_new.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor_new.fetchall()
        print(f"   Tables: {[t[0] for t in tables]}")
        
        # Compter les enregistrements
        for table in tables:
            table_name = table[0]
            try:
                cursor_new.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor_new.fetchone()[0]
                print(f"   {table_name}: {count:,} enregistrements")
                
                # Afficher les colonnes de la table principale
                if table_name == "bank_data_enriched":
                    cursor_new.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor_new.fetchall()
                    print(f"   └─ {len(columns)} colonnes")
                    
            except Exception as e:
                print(f"   {table_name}: Erreur - {e}")
        
        conn_new.close()
    
    # Recommandation
    print(f"\n💡 RECOMMANDATION:")
    if Path(old_db).exists() and Path(new_db).exists():
        old_size = Path(old_db).stat().st_size / (1024*1024)  # MB
        new_size = Path(new_db).stat().st_size / (1024*1024)  # MB
        print(f"   Ancienne base: {old_size:.1f} MB")
        print(f"   Nouvelle base: {new_size:.1f} MB")
        print(f"   → Vous pouvez supprimer l'ancienne base si la nouvelle est complète")
    
    return True

def backup_and_switch():
    """Sauvegarder l'ancienne base et basculer vers la nouvelle."""
    print(f"\n🔄 BASCULE VERS LA NOUVELLE BASE")
    print("-" * 40)
    
    old_db = "bankreports.db"
    new_db = "bankreports_enriched.db"
    backup_db = "bankreports_backup.db"
    
    if Path(old_db).exists():
        # Renommer l'ancienne en backup
        os.rename(old_db, backup_db)
        print(f"   ✅ Ancienne base renommée: {backup_db}")
        
        # Renommer la nouvelle en principale
        os.rename(new_db, old_db)
        print(f"   ✅ Nouvelle base activée: {old_db}")
        
        print(f"\n   🎯 Résultat:")
        print(f"      • Base active: {old_db} (avec données enrichies)")
        print(f"      • Sauvegarde: {backup_db} (anciennes données)")
        
        return True
    else:
        print(f"   ⚠️  Ancienne base non trouvée")
        return False

def main():
    """Fonction principale."""
    check_database_content()
    
    print(f"\n" + "="*50)
    response = input("Voulez-vous basculer vers la nouvelle base ? (o/n): ")
    
    if response.lower() in ['o', 'oui', 'y', 'yes']:
        backup_and_switch()
        print(f"\n🎉 Migration terminée ! La nouvelle base enrichie est maintenant active.")
    else:
        print(f"\n📝 Aucun changement effectué. Les deux bases coexistent.")

if __name__ == "__main__":
    main() 
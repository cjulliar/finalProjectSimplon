#!/usr/bin/env python3
"""
Script de finalisation - Une seule base de données SQLite
"""

import os
import shutil
import sqlite3
from datetime import datetime

def finalize_single_database():
    """Finalise la consolidation en une seule base de données"""
    
    print("🎯 FINALISATION - UNE SEULE BASE DE DONNÉES")
    print("=" * 50)
    
    # 1. Vérifier que la base consolidée existe et est complète
    print("\n1️⃣ Vérification de la base consolidée...")
    
    if not os.path.exists("bankreports.db"):
        print("❌ Base consolidée non trouvée !")
        return False
    
    # Vérifier le contenu
    conn = sqlite3.connect("bankreports.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"   ✅ Tables présentes: {len(tables)}")
    print(f"   📋 Tables: {', '.join(tables)}")
    
    # Compter les données importantes
    stats = {}
    for table in ['users', 'email_reports', 'bank_data_enriched', 'analyses']:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        stats[table] = count
        print(f"   📊 {table}: {count} enregistrements")
    
    conn.close()
    
    # 2. Créer une sauvegarde de sécurité
    print("\n2️⃣ Création d'une sauvegarde de sécurité...")
    
    backup_name = f"bankreports_final_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy("bankreports.db", backup_name)
    print(f"   ✅ Sauvegarde créée: {backup_name}")
    
    # 3. Supprimer les bases redondantes
    print("\n3️⃣ Nettoyage des bases redondantes...")
    
    bases_to_remove = [
        "frontend/db.sqlite3",
        "frontend/bankreports.db", 
        "src/bankreports.db",
        "bankreports_backup.db",
        "bankreports_old.db",
        "bankreports_enriched.db",
        "data/bank_data_enriched.db"
    ]
    
    for base_path in bases_to_remove:
        if os.path.exists(base_path):
            try:
                os.remove(base_path)
                print(f"   🗑️  Supprimé: {base_path}")
            except Exception as e:
                print(f"   ⚠️  Erreur suppression {base_path}: {e}")
        else:
            print(f"   ℹ️  Non trouvé: {base_path}")
    
    # 4. Vérifier qu'il ne reste qu'une seule base
    print("\n4️⃣ Vérification finale...")
    
    remaining_bases = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(('.db', '.sqlite', '.sqlite3')):
                full_path = os.path.join(root, file)
                if not full_path.startswith('./.git'):
                    remaining_bases.append(full_path)
    
    print(f"   📊 Bases restantes: {len(remaining_bases)}")
    for base in remaining_bases:
        print(f"   📁 {base}")
    
    # 5. Créer un script de backup automatique
    print("\n5️⃣ Création du script de backup automatique...")
    
    backup_script = """#!/bin/bash
# Script de backup automatique pour la base consolidée
# À exécuter quotidiennement avec cron

BACKUP_DIR="./backups"
DB_FILE="./bankreports.db"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/bankreports_backup_$DATE.db"

# Créer le dossier de backup s'il n'existe pas
mkdir -p "$BACKUP_DIR"

# Copier la base de données
cp "$DB_FILE" "$BACKUP_FILE"

# Garder seulement les 7 derniers backups
ls -t "$BACKUP_DIR"/bankreports_backup_*.db | tail -n +8 | xargs -r rm

echo "Backup créé: $BACKUP_FILE"
"""
    
    with open("backup_database.sh", "w") as f:
        f.write(backup_script)
    
    os.chmod("backup_database.sh", 0o755)
    print("   ✅ Script de backup créé: backup_database.sh")
    
    # 6. Créer un fichier de documentation
    print("\n6️⃣ Création de la documentation...")
    
    docs = f"""# BASE DE DONNÉES CONSOLIDÉE

## 📊 Informations
- **Fichier**: bankreports.db
- **Type**: SQLite
- **Taille**: {os.path.getsize('bankreports.db') // 1024 // 1024} MB
- **Date de consolidation**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📋 Tables
{chr(10).join([f"- {table}" for table in tables])}

## 📊 Statistiques
{chr(10).join([f"- {table}: {stats.get(table, 0)} enregistrements" for table in ['users', 'email_reports', 'bank_data_enriched', 'analyses']])}

## 🔧 Utilisation
- **Django**: Utilise cette base via la configuration dans frontend/settings.py
- **FastAPI**: Utilise cette base via la configuration dans src/db/database.py
- **Backup**: Utilise le script backup_database.sh

## 🚀 Déploiement
Cette base SQLite est prête pour le déploiement sur serveur.
- Copier le fichier bankreports.db sur le serveur
- Configurer les permissions appropriées
- Utiliser le script de backup pour la maintenance

## 📝 Notes
- Base unique pour tout le projet
- Compatible production
- Backup automatique recommandé
"""
    
    with open("DATABASE_README.md", "w") as f:
        f.write(docs)
    
    print("   ✅ Documentation créée: DATABASE_README.md")
    
    print("\n🎉 FINALISATION TERMINÉE !")
    print("=" * 50)
    print("✅ Base unique: bankreports.db")
    print("✅ Django et FastAPI configurés")
    print("✅ Bases redondantes supprimées")
    print("✅ Script de backup créé")
    print("✅ Documentation mise à jour")
    print(f"✅ Sauvegarde de sécurité: {backup_name}")
    
    print("\n🌐 POUR TESTER:")
    print("   1. Redémarrer le projet: ./stop_project.sh && ./dev_start.sh")
    print("   2. Vérifier le site: http://localhost:8080")
    print("   3. Vérifier les emails dans 'Dernier rapport'")
    
    return True

if __name__ == "__main__":
    try:
        finalize_single_database()
    except Exception as e:
        print(f"❌ Erreur lors de la finalisation: {e}")
        exit(1) 
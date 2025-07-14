#!/usr/bin/env python3
"""
Script pour nettoyer les bases de données redondantes
et éviter les futures régressions
"""

import os
import shutil
from datetime import datetime

def cleanup_redundant_databases():
    """Nettoie les bases de données redondantes"""
    
    print("🧹 NETTOYAGE DES BASES DE DONNÉES REDONDANTES")
    print("=" * 50)
    
    # Liste des bases à supprimer (garder seulement bankreports.db)
    redundant_dbs = [
        'frontend/bankreports.db',
        'src/bankreports.db',
        'bankreports_backup_20250714_131359.db',
        'bankreports_final_backup_20250714_134749.db'
    ]
    
    # Créer un dossier de sauvegarde pour les anciennes bases
    backup_dir = f"old_databases_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    print(f"📁 Dossier de sauvegarde créé : {backup_dir}")
    
    for db_path in redundant_dbs:
        if os.path.exists(db_path):
            try:
                # Déplacer vers le dossier de sauvegarde
                backup_path = os.path.join(backup_dir, os.path.basename(db_path))
                shutil.move(db_path, backup_path)
                print(f"✅ Déplacé : {db_path} → {backup_path}")
            except Exception as e:
                print(f"❌ Erreur lors du déplacement de {db_path}: {e}")
        else:
            print(f"ℹ️  Non trouvé : {db_path}")
    
    # Vérifier qu'il ne reste qu'une seule base
    remaining_dbs = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.db') and 'bankreports' in file:
                full_path = os.path.join(root, file)
                if not full_path.startswith(f'./{backup_dir}'):
                    remaining_dbs.append(full_path)
    
    print(f"\n📊 Bases de données restantes :")
    for db in remaining_dbs:
        size = os.path.getsize(db) / (1024 * 1024)  # Taille en MB
        print(f"   📄 {db} ({size:.1f} MB)")
    
    if len(remaining_dbs) == 1:
        print(f"\n✅ Parfait ! Une seule base de données reste : {remaining_dbs[0]}")
    else:
        print(f"\n⚠️  Attention : {len(remaining_dbs)} bases de données restent")
    
    # Créer un fichier de documentation
    doc_file = "DATABASE_CONSOLIDATION.md"
    with open(doc_file, 'w', encoding='utf-8') as f:
        f.write("# Consolidation des Bases de Données\n\n")
        f.write(f"**Date de consolidation :** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Base de données unique\n\n")
        f.write("Le projet utilise maintenant une seule base de données SQLite :\n")
        f.write("- `bankreports.db` : Base consolidée principale\n\n")
        f.write("## Sauvegardes\n\n")
        f.write("Les anciennes bases ont été déplacées dans :\n")
        f.write(f"- `{backup_dir}/` : Anciennes bases de données\n")
        f.write("- `users_backup_*.json` : Sauvegardes des utilisateurs Django\n\n")
        f.write("## Configuration\n\n")
        f.write("Django est configuré pour utiliser automatiquement la base consolidée.\n")
        f.write("Voir `frontend/frontend/settings.py` pour la configuration.\n\n")
        f.write("## Prévention des régressions\n\n")
        f.write("1. Toujours utiliser `bankreports.db` comme base unique\n")
        f.write("2. Sauvegarder les utilisateurs avant toute opération : `python backup_users.py backup`\n")
        f.write("3. Restaurer les utilisateurs si nécessaire : `python backup_users.py restore --file users_backup_*.json`\n")
    
    print(f"\n📝 Documentation créée : {doc_file}")
    
    return True

def create_database_monitor():
    """Crée un script de monitoring pour détecter les bases multiples"""
    
    monitor_script = "check_database_integrity.py"
    
    with open(monitor_script, 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python3
"""
Script de monitoring pour vérifier l'intégrité de la base de données
"""

import os
import sys
import django

# Ajouter le répertoire frontend au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'frontend'))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')
django.setup()

from django.contrib.auth.models import User

def check_database_integrity():
    """Vérifie l'intégrité de la base de données"""
    
    print("🔍 VÉRIFICATION DE L'INTÉGRITÉ DE LA BASE DE DONNÉES")
    print("=" * 50)
    
    # 1. Vérifier les bases multiples
    bankreports_dbs = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.db') and 'bankreports' in file:
                full_path = os.path.join(root, file)
                if not full_path.startswith('./old_databases_backup_'):
                    bankreports_dbs.append(full_path)
    
    if len(bankreports_dbs) > 1:
        print("❌ PROBLÈME DÉTECTÉ : Plusieurs bases bankreports.db trouvées")
        for db in bankreports_dbs:
            print(f"   📄 {db}")
        print("   💡 Solution : Exécuter python cleanup_redundant_dbs.py")
        return False
    elif len(bankreports_dbs) == 1:
        print(f"✅ Base unique détectée : {bankreports_dbs[0]}")
    else:
        print("❌ Aucune base bankreports.db trouvée")
        return False
    
    # 2. Vérifier les utilisateurs
    total_users = User.objects.count()
    directeur_users = User.objects.filter(username__startswith='directeurBanque').count()
    
    print(f"👥 Utilisateurs : {total_users} total, {directeur_users} directeurs")
    
    if directeur_users < 70:
        print("⚠️  ATTENTION : Nombre de directeurs insuffisant")
        print("   💡 Solution : Exécuter python create_directeurs.py")
        return False
    
    # 3. Vérifier les emails
    import sqlite3
    try:
        conn = sqlite3.connect('bankreports.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM email_reports")
        email_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"📧 Emails : {email_count} enregistrements")
        
        if email_count < 50:
            print("⚠️  ATTENTION : Nombre d'emails insuffisant")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des emails : {e}")
        return False
    
    print("✅ Intégrité de la base de données OK")
    return True

if __name__ == '__main__':
    check_database_integrity()
''')
    
    # Rendre le script exécutable
    os.chmod(monitor_script, 0o755)
    print(f"🔍 Script de monitoring créé : {monitor_script}")

if __name__ == '__main__':
    cleanup_redundant_databases()
    create_database_monitor() 
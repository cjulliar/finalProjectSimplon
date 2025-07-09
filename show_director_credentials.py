#!/usr/bin/env python3
"""
Script pour afficher les identifiants d'un directeur d'agence
"""

import sqlite3
import os

def show_director_credentials(agence_name=None):
    """Affiche les identifiants d'un directeur d'agence"""
    print("🏦 IDENTIFIANTS DIRECTEUR D'AGENCE")
    print("=" * 50)
    
    # Connexion à la base de données
    db_path = os.environ.get('BANKREPORTS_DB_PATH', 'bankreports.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if agence_name:
        # Afficher les identifiants pour une agence spécifique
        cursor.execute('SELECT DISTINCT agence FROM bank_data_enriched WHERE agence LIKE ? ORDER BY agence', (f'%{agence_name}%',))
        agences = [row[0] for row in cursor.fetchall()]
        
        if not agences:
            print(f"❌ Aucune agence trouvée avec '{agence_name}'")
            return
        
        agence = agences[0]
    else:
        # Afficher les identifiants pour la première agence
        cursor.execute('SELECT DISTINCT agence FROM bank_data_enriched ORDER BY agence LIMIT 1')
        agence = cursor.fetchone()[0]
    
    # Créer le nom d'utilisateur
    username = f"directeur{agence.replace(' ', '')}"
    
    print(f"🏢 Agence: {agence}")
    print(f"👤 Nom d'utilisateur: {username}")
    print(f"📧 Email: cyrjulliard@gmail.com")
    print(f"🔑 Mot de passe: directeur123")
    
    print(f"\n🌐 URL de connexion:")
    print(f"   http://localhost:8080/login/")
    
    print(f"\n📊 Données disponibles pour cette agence:")
    cursor.execute('SELECT COUNT(*) FROM bank_data_enriched WHERE agence = ?', (agence,))
    count = cursor.fetchone()[0]
    print(f"   • {count} enregistrements de données")
    
    # Afficher quelques statistiques
    cursor.execute('''
        SELECT 
            SUM(moy_global) as total_montant,
            AVG(moy_global) as moyenne_montant,
            COUNT(*) as nombre_semaines
        FROM bank_data_enriched 
        WHERE agence = ?
    ''', (agence,))
    
    stats = cursor.fetchone()
    if stats[0]:
        print(f"   • Montant total: {stats[0]:,.2f}€")
        print(f"   • Montant moyen: {stats[1]:,.2f}€")
        print(f"   • Nombre de semaines: {stats[2]}")
    
    conn.close()
    
    print(f"\n✅ Vous pouvez maintenant vous connecter avec ces identifiants!")
    print(f"💡 L'interface devrait afficher uniquement les données de {agence}")
    print(f"🎯 Nouvelles fonctionnalités disponibles:")
    print(f"   • Dernier rapport")
    print(f"   • Historique des rapports")
    print(f"   • Statistiques avec graphiques")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        agence_name = sys.argv[1]
        show_director_credentials(agence_name)
    else:
        show_director_credentials() 
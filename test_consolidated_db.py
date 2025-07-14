#!/usr/bin/env python3
"""
Script de test pour vérifier que la base consolidée fonctionne correctement
"""

import sqlite3
import requests
import time

def test_consolidated_database():
    """Test complet de la base consolidée"""
    
    print("🧪 TEST DE LA BASE CONSOLIDÉE")
    print("=" * 40)
    
    # 1. Test de la base de données
    print("\n1️⃣ Test de la base de données...")
    
    try:
        conn = sqlite3.connect("bankreports.db")
        cursor = conn.cursor()
        
        # Vérifier les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"   ✅ Tables présentes: {len(tables)}")
        
        # Vérifier les données importantes
        stats = {}
        for table in ['users', 'email_reports', 'bank_data_enriched', 'analyses']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            stats[table] = count
            print(f"   📊 {table}: {count} enregistrements")
        
        # Vérifier un email spécifique
        cursor.execute("SELECT id, bank_name, subject FROM email_reports LIMIT 1")
        email = cursor.fetchone()
        if email:
            print(f"   📧 Email trouvé: {email[2]} pour {email[1]}")
        else:
            print("   ⚠️  Aucun email trouvé")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Erreur base de données: {e}")
        return False
    
    # 2. Test des services web
    print("\n2️⃣ Test des services web...")
    
    services = [
        ("http://localhost:8080/login/", "Frontend Django (Login)"),
        ("http://localhost:8080/", "Frontend Django (Accueil)"),
        ("http://localhost:8001/health", "API FastAPI (Health)"),
        ("http://localhost:8001/docs", "API FastAPI (Documentation)"),
    ]
    
    for url, name in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name}: OK")
            else:
                print(f"   ⚠️  {name}: Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: Erreur - {e}")
    
    # 3. Test de l'API avec authentification
    print("\n3️⃣ Test de l'API avec authentification...")
    
    try:
        # Test de connexion avec un utilisateur
        login_data = {
            'username': 'directeurBanque_A',
            'password': 'admin'
        }
        
        response = requests.post(
            'http://localhost:8001/api/token',
            data=login_data,
            timeout=5
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"   ✅ Authentification API: OK")
            print(f"   🔑 Token obtenu: {token_data.get('access_token', '')[:20]}...")
        else:
            print(f"   ⚠️  Authentification API: Status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erreur authentification API: {e}")
    
    print("\n🎉 TEST TERMINÉ !")
    print("=" * 40)
    
    # Résumé
    print("\n📊 RÉSUMÉ DE LA CONSOLIDATION:")
    print(f"   • Base de données: {len(tables)} tables")
    print(f"   • Utilisateurs: {stats.get('users', 0)}")
    print(f"   • Emails: {stats.get('email_reports', 0)}")
    print(f"   • Données bancaires: {stats.get('bank_data_enriched', 0)}")
    print(f"   • Analyses: {stats.get('analyses', 0)}")
    print(f"   • Services web: 4/4 testés")
    
    return True

if __name__ == "__main__":
    test_consolidated_database() 
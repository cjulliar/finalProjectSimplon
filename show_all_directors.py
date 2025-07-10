#!/usr/bin/env python3
"""
Script pour afficher les identifiants de tous les directeurs d'agence
"""

import os
import sys
import django
import sqlite3

# Configuration Django
sys.path.append('frontend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')

try:
    django.setup()
    from django.contrib.auth.models import User
    
    def show_all_directors():
        """Affiche les identifiants de tous les directeurs d'agence"""
        print("🏦 IDENTIFIANTS DE TOUS LES DIRECTEURS D'AGENCE")
        print("=" * 60)
        
        # Récupérer tous les directeurs
        directors = User.objects.filter(username__startswith='directeur').order_by('username')
        
        print(f"📊 {directors.count()} directeurs d'agence configurés")
        print(f"\n🔐 INFORMATIONS DE CONNEXION:")
        print(f"   • URL: http://localhost:8080/login/")
        print(f"   • Email: cyrjulliard@gmail.com")
        print(f"   • Mot de passe: directeur123")
        print(f"\n👥 LISTE COMPLÈTE DES DIRECTEURS:")
        print("-" * 60)
        
        # Récupérer les agences depuis la base de données
        conn = sqlite3.connect('bankreports.db')
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT agence FROM bank_data_enriched ORDER BY agence')
        agences = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Créer un mapping agence -> directeur
        agence_to_director = {}
        for director in directors:
            agence_name = director.username.replace('directeur', '')
            agence_to_director[agence_name] = director.username
        
        # Afficher tous les directeurs avec leurs agences
        for i, agence in enumerate(agences, 1):
            director_username = agence_to_director.get(agence, f"directeur{agence.replace(' ', '')}")
            print(f"{i:2d}. {agence:15} → {director_username:20} | cyrjulliard@gmail.com | directeur123")
        
        print(f"\n📋 RÉSUMÉ:")
        print(f"   • Total agences: {len(agences)}")
        print(f"   • Total directeurs: {directors.count()}")
        print(f"   • Correspondance: {'✅ Parfaite' if len(agences) == directors.count() else '⚠️  Incomplète'}")
        
        print(f"\n💡 EXEMPLES D'UTILISATION:")
        print(f"   1. Ouvrir http://localhost:8080/login/")
        print(f"   2. Saisir un nom d'utilisateur (ex: directeurBanqueA)")
        print(f"   3. Saisir le mot de passe: directeur123")
        print(f"   4. Cliquer sur 'Se connecter'")
        
        print(f"\n🎯 FONCTIONNALITÉS DISPONIBLES:")
        print(f"   • Dashboard personnalisé par agence")
        print(f"   • Données bancaires filtrées")
        print(f"   • Rapports automatiques")
        print(f"   • Statistiques et graphiques")
        
        print(f"\n✅ Tous les directeurs d'agence peuvent maintenant accéder au site!")
    
    if __name__ == "__main__":
        show_all_directors()

except Exception as e:
    print(f"❌ Erreur: {e}")
    print("💡 Assurez-vous que Django est correctement configuré.")
    sys.exit(1) 
#!/usr/bin/env python3
"""
Démonstration des améliorations de formatage des emails
"""

import os
import sys
import django
import sqlite3

# Configuration Django
sys.path.append('frontend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')
django.setup()

def demo_email_formatting():
    """Démonstration du formatage des emails"""
    
    print("🎨 DÉMONSTRATION DU FORMATAGE DES EMAILS")
    print("=" * 60)
    
    # Connexion à la base de données
    conn = sqlite3.connect('bankreports.db')
    cursor = conn.cursor()
    
    # Compter les emails disponibles
    cursor.execute("SELECT COUNT(*) FROM email_reports")
    total_emails = cursor.fetchone()[0]
    
    print(f"📊 Statistiques:")
    print(f"   • Total d'emails en base: {total_emails}")
    
    # Compter par agence
    cursor.execute("SELECT bank_name, COUNT(*) FROM email_reports GROUP BY bank_name ORDER BY COUNT(*) DESC")
    agences = cursor.fetchall()
    
    print(f"   • Répartition par agence:")
    for agence, count in agences[:5]:
        print(f"     - {agence}: {count} emails")
    
    # Récupérer un exemple d'email
    cursor.execute("""
        SELECT bank_name, subject, content, sent_at 
        FROM email_reports 
        ORDER BY sent_at DESC 
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    if result:
        bank_name, subject, content, sent_at = result
        
        print(f"\n📧 EXEMPLE D'EMAIL:")
        print(f"   • Agence: {bank_name}")
        print(f"   • Sujet: {subject}")
        print(f"   • Date: {sent_at}")
        print(f"   • Taille: {len(content)} caractères")
        
        # Analyser le contenu
        lines = content.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        print(f"\n📋 ANALYSE DU CONTENU:")
        print(f"   • Lignes totales: {len(lines)}")
        print(f"   • Lignes non vides: {len(non_empty_lines)}")
        
        # Détecter les types de contenu
        titles = [line for line in non_empty_lines if line.isupper() and len(line) > 3]
        amounts = [line for line in non_empty_lines if '€' in line]
        lists = [line for line in non_empty_lines if line.startswith(('•', '-', '1.', '2.', '3.'))]
        
        print(f"   • Titres détectés: {len(titles)}")
        print(f"   • Montants détectés: {len(amounts)}")
        print(f"   • Éléments de liste: {len(lists)}")
        
        print(f"\n🎯 AMÉLIORATIONS APPORTÉES:")
        print(f"   ✅ Conversion automatique des retours à la ligne")
        print(f"   ✅ Détection et formatage des titres")
        print(f"   ✅ Mise en évidence des montants")
        print(f"   ✅ Formatage des listes")
        print(f"   ✅ Styles CSS intégrés")
        print(f"   ✅ Responsive design")
        
        print(f"\n🌐 ACCÈS AU SITE:")
        print(f"   • URL: http://localhost:8080")
        print(f"   • Identifiants: directeurBanqueA / directeur123")
        print(f"   • Pages concernées:")
        print(f"     - Dernier Rapport")
        print(f"     - Historique des Rapports")
        
    conn.close()
    
    print(f"\n✅ DÉMONSTRATION TERMINÉE")
    print(f"💡 Les emails s'affichent maintenant avec une mise en page professionnelle!")

if __name__ == "__main__":
    demo_email_formatting() 
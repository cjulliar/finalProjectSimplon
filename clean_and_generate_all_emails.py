#!/usr/bin/env python3
"""
Script pour nettoyer et générer tous les emails enrichis.
1. Supprimer les anciens emails (génération précédente)
2. Générer tous les emails pour les 74 banques
3. Vérifier la cohérence (74 emails = 74 banques)
"""
import sqlite3
import time
from datetime import datetime
from enhanced_email_system import (
    get_enhanced_bank_data_with_history,
    get_previous_email_analyses,
    send_enhanced_analysis_email
)

def clean_old_emails():
    """Supprimer les anciens emails de génération précédente."""
    conn = sqlite3.connect("bankreports.db")
    cursor = conn.cursor()
    
    print("🧹 NETTOYAGE DES ANCIENS EMAILS")
    print("=" * 40)
    
    # Lister les emails actuels
    cursor.execute("SELECT id, bank_name, subject, sent_at FROM email_reports ORDER BY sent_at")
    emails = cursor.fetchall()
    
    print(f"📧 Emails actuels en BDD: {len(emails)}")
    
    old_emails = []
    new_emails = []
    
    for email_id, bank_name, subject, sent_at in emails:
        # Identifier les anciens emails (sans "Enrichi" dans le sujet)
        if "Enrichi" not in subject or "Hebdomadaire" in subject:
            old_emails.append((email_id, subject, sent_at))
        else:
            new_emails.append((email_id, subject, sent_at))
    
    print(f"   🔴 Anciens emails à supprimer: {len(old_emails)}")
    print(f"   🟢 Emails enrichis à conserver: {len(new_emails)}")
    
    if old_emails:
        print(f"\n📋 Emails à supprimer:")
        for email_id, subject, sent_at in old_emails:
            print(f"   - {subject} ({sent_at})")
        
        # Confirmer la suppression
        confirm = input(f"\n❓ Supprimer ces {len(old_emails)} anciens emails ? (o/n): ").lower()
        
        if confirm == 'o':
            for email_id, _, _ in old_emails:
                cursor.execute("DELETE FROM email_reports WHERE id = ?", (email_id,))
            
            conn.commit()
            print(f"   ✅ {len(old_emails)} anciens emails supprimés")
        else:
            print(f"   ⏸️ Suppression annulée")
    else:
        print(f"   ✅ Aucun ancien email trouvé")
    
    conn.close()
    return len(old_emails), len(new_emails)

def get_all_bank_agencies():
    """Récupérer toutes les agences bancaires."""
    conn = sqlite3.connect("bankreports.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT agence 
        FROM bank_data_enriched 
        WHERE agence IS NOT NULL 
        ORDER BY agence
    """)
    
    agencies = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return agencies

def get_banks_without_enriched_emails():
    """Identifier les banques sans email enrichi."""
    conn = sqlite3.connect("bankreports.db")
    cursor = conn.cursor()
    
    # Toutes les banques
    all_banks = get_all_bank_agencies()
    
    # Banques avec email enrichi
    cursor.execute("""
        SELECT DISTINCT bank_name 
        FROM email_reports 
        WHERE subject LIKE '%Enrichi%'
    """)
    
    banks_with_emails = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    # Banques manquantes
    banks_missing = [bank for bank in all_banks if bank not in banks_with_emails]
    
    return banks_missing, banks_with_emails

def generate_missing_emails(banks_missing):
    """Générer les emails manquants pour les banques."""
    if not banks_missing:
        print("✅ Tous les emails enrichis sont déjà générés")
        return []
    
    print(f"\n📧 GÉNÉRATION DES EMAILS MANQUANTS")
    print("=" * 50)
    print(f"🎯 Banques à traiter: {len(banks_missing)}")
    
    results = []
    
    for i, agence in enumerate(banks_missing, 1):
        print(f"\n📨 {i}/{len(banks_missing)} - Génération pour {agence}...")
        
        try:
            # Récupérer données enrichies (8 semaines)
            data = get_enhanced_bank_data_with_history(agence, weeks_count=8)
            
            if not data:
                print(f"   ⚠️ Aucune donnée pour {agence}")
                results.append({"bank": agence, "status": "❌ Pas de données"})
                continue
            
            # Récupérer emails précédents
            previous_emails = get_previous_email_analyses(agence, limit=3)
            
            # Générer analyse enrichie
            analysis = f"""📊 **SYNTHÈSE EXÉCUTIVE**
Performance {agence} : score {data[0]['score_performance']}/100, rang {data[0]['rang_global']}/74 (percentile {((74-data[0]['rang_global'])/74*100):.1f}).

📈 **PERFORMANCE GLOBALE & POSITIONNEMENT**
CA total: {data[0]['ca_total']:,.0f}€. Position dans le réseau: {data[0]['rang_global']}/74. Analyse sur {len(data)} semaines disponibles.

👥 **ANALYSE SEGMENTIELLE APPROFONDIE**
Répartition: {data[0]['pourcentage_particuliers']:.1f}% Particuliers ({data[0]['ca_particuliers']:,.0f}€) vs {100-data[0]['pourcentage_particuliers']:.1f}% Pro ({data[0]['ca_professionnels']:,.0f}€).
Clients: {data[0]['occ_part']} particuliers + {data[0]['occ_pro']} professionnels = {data[0]['clients_totaux']} total.

💼 **VOLUMES BUSINESS & STRATÉGIE PRODUITS**
Particuliers: IARD {data[0]['vb_iard_part']}, Prévoyance {data[0]['vb_prev_part']}, Assurance-vie {data[0]['vb_ass_peri_pea_hiss']}.
Professionnels: IARD {data[0]['vb_iard_pro']}, Prévoyance {data[0]['vb_prev_pro']}, Contrats {data[0]['vb_contr_comm']}.

🎯 **EFFICACITÉ COMMERCIALE & ATTEINTE OBJECTIFS**
Objectif Pro: {data[0]['occ_pro']}/{data[0]['occ_pro_cible']} ({data[0]['taux_atteinte_objectif']:.1f}%).
Productivité: {(data[0]['ca_total']/data[0]['clients_totaux']):,.0f}€/client.

📊 **TENDANCES & ÉVOLUTIONS**
Rang particuliers: {data[0]['rang_part']}/74, Rang professionnels: {data[0]['rang_pro']}/74.
Historique disponible: {len(data)} semaines analysées.

🏆 **RECOMMANDATIONS STRATÉGIQUES**
1. **Optimiser segment dominant** ({data[0]['pourcentage_particuliers']:.0f}% du CA)
2. **Développer volumes business** prioritaires
3. **Maintenir position rang {data[0]['rang_global']}** dans le réseau"""
            
            print(f"   🧠 Analyse générée ({len(analysis)} caractères)")
            
            # Envoyer et sauvegarder
            success, message = send_enhanced_analysis_email(agence, analysis, data, previous_emails)
            
            if success:
                print(f"   📧 Email envoyé et sauvegardé")
                results.append({"bank": agence, "status": "✅ Envoyé"})
            else:
                print(f"   ❌ Erreur: {message}")
                results.append({"bank": agence, "status": "❌ Erreur", "error": message})
            
            # Pause entre envois pour éviter spam
            if i < len(banks_missing):
                time.sleep(1)
                
        except Exception as e:
            error_msg = f"Erreur générale: {str(e)}"
            print(f"   ❌ {error_msg}")
            results.append({"bank": agence, "status": "❌ Erreur", "error": error_msg})
    
    return results

def verify_email_completeness():
    """Vérifier que nous avons un email pour chaque banque."""
    conn = sqlite3.connect("bankreports.db")
    cursor = conn.cursor()
    
    print(f"\n✅ VÉRIFICATION DE COMPLÉTUDE")
    print("=" * 40)
    
    # Compter les banques
    cursor.execute("SELECT COUNT(DISTINCT agence) FROM bank_data_enriched")
    total_banks = cursor.fetchone()[0]
    
    # Compter les emails enrichis
    cursor.execute("SELECT COUNT(*) FROM email_reports WHERE subject LIKE '%Enrichi%'")
    total_emails = cursor.fetchone()[0]
    
    # Détail par banque
    cursor.execute("""
        SELECT bank_name, COUNT(*) as nb_emails
        FROM email_reports 
        WHERE subject LIKE '%Enrichi%'
        GROUP BY bank_name
        ORDER BY bank_name
    """)
    emails_by_bank = cursor.fetchall()
    
    print(f"📊 Banques dans données: {total_banks}")
    print(f"📧 Emails enrichis générés: {total_emails}")
    print(f"📈 Taux de complétude: {(total_emails/total_banks*100):.1f}%")
    
    if total_emails == total_banks:
        print(f"🎉 SUCCÈS: Complétude parfaite !")
    else:
        print(f"⚠️ ATTENTION: {total_banks - total_emails} emails manquants")
        
        # Identifier les banques manquantes
        banks_missing, _ = get_banks_without_enriched_emails()
        if banks_missing:
            print(f"\n📋 Banques sans email enrichi:")
            for bank in banks_missing[:10]:  # Afficher max 10
                print(f"   - {bank}")
            if len(banks_missing) > 10:
                print(f"   ... et {len(banks_missing) - 10} autres")
    
    # Détail emails par banque (top 10)
    if emails_by_bank:
        print(f"\n📋 Détail emails par banque (top 10):")
        for bank_name, nb_emails in emails_by_bank[:10]:
            print(f"   {bank_name}: {nb_emails} email(s)")
    
    conn.close()
    return total_banks, total_emails

def main():
    """Fonction principale."""
    print("🚀 NETTOYAGE ET GÉNÉRATION COMPLÈTE DES EMAILS")
    print("=" * 60)
    
    # 1. Nettoyer les anciens emails
    old_count, new_count = clean_old_emails()
    
    # 2. Identifier les banques manquantes
    banks_missing, banks_with_emails = get_banks_without_enriched_emails()
    
    print(f"\n📊 ÉTAT ACTUEL:")
    print(f"   🟢 Banques avec email enrichi: {len(banks_with_emails)}")
    print(f"   🔴 Banques sans email enrichi: {len(banks_missing)}")
    
    # 3. Générer les emails manquants
    if banks_missing:
        proceed = input(f"\n❓ Générer {len(banks_missing)} emails manquants ? (o/n): ").lower()
        
        if proceed == 'o':
            results = generate_missing_emails(banks_missing)
            
            # Résumé des résultats
            success_count = len([r for r in results if "✅" in r["status"]])
            print(f"\n🎯 RÉSULTATS GÉNÉRATION:")
            print(f"   ✅ Succès: {success_count}/{len(banks_missing)}")
            print(f"   ❌ Échecs: {len(banks_missing) - success_count}/{len(banks_missing)}")
        else:
            print(f"   ⏸️ Génération annulée")
    
    # 4. Vérification finale
    total_banks, total_emails = verify_email_completeness()
    
    print(f"\n🏁 PROCESSUS TERMINÉ")
    print(f"   📊 {total_banks} banques / {total_emails} emails enrichis")
    print(f"   📈 Complétude: {(total_emails/total_banks*100):.1f}%")
    
    if total_emails == total_banks:
        print(f"   🎉 OBJECTIF ATTEINT: 1 email enrichi par banque !")
    else:
        print(f"   ⚠️ OBJECTIF PARTIEL: {total_banks - total_emails} emails manquants")

if __name__ == "__main__":
    main() 
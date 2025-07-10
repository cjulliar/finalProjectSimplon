#!/usr/bin/env python3
"""
Version automatisée du nettoyage et génération des emails enrichis.
Pas de confirmation utilisateur - traitement automatique complet.
"""
import sqlite3
import time
from datetime import datetime
from enhanced_email_system import (
    get_enhanced_bank_data_with_history,
    get_previous_email_analyses,
    send_enhanced_analysis_email
)

def auto_clean_old_emails():
    """Supprimer automatiquement les anciens emails de génération précédente."""
    conn = sqlite3.connect("bankreports.db")
    cursor = conn.cursor()
    
    print("🧹 NETTOYAGE AUTOMATIQUE DES ANCIENS EMAILS")
    print("=" * 50)
    
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
    
    print(f"   🔴 Anciens emails détectés: {len(old_emails)}")
    print(f"   🟢 Emails enrichis conservés: {len(new_emails)}")
    
    if old_emails:
        print(f"\n📋 Suppression automatique de {len(old_emails)} anciens emails...")
        for email_id, subject, sent_at in old_emails:
            print(f"   - Suppression: {subject}")
            cursor.execute("DELETE FROM email_reports WHERE id = ?", (email_id,))
        
        conn.commit()
        print(f"   ✅ {len(old_emails)} anciens emails supprimés automatiquement")
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

def auto_generate_all_missing_emails():
    """Générer automatiquement tous les emails manquants."""
    banks_missing, banks_with_emails = get_banks_without_enriched_emails()
    
    print(f"\n📧 GÉNÉRATION AUTOMATIQUE DES EMAILS")
    print("=" * 50)
    print(f"🟢 Banques avec email enrichi: {len(banks_with_emails)}")
    print(f"🔴 Banques sans email enrichi: {len(banks_missing)}")
    
    if not banks_missing:
        print("✅ Tous les emails enrichis sont déjà générés")
        return []
    
    print(f"\n🚀 Génération automatique pour {len(banks_missing)} banques...")
    
    results = []
    
    for i, agence in enumerate(banks_missing, 1):
        print(f"\n📨 {i}/{len(banks_missing)} - {agence}...")
        
        try:
            # Récupérer données enrichies (8 semaines)
            data = get_enhanced_bank_data_with_history(agence, weeks_count=8)
            
            if not data:
                print(f"   ⚠️ Aucune donnée pour {agence}")
                results.append({"bank": agence, "status": "❌ Pas de données"})
                continue
            
            # Récupérer emails précédents
            previous_emails = get_previous_email_analyses(agence, limit=3)
            
            # Générer analyse enrichie compacte
            analysis = f"""📊 **SYNTHÈSE EXÉCUTIVE**
Performance {agence}: score {data[0]['score_performance']}/100, rang {data[0]['rang_global']}/74 ({((74-data[0]['rang_global'])/74*100):.1f}e percentile).

📈 **PERFORMANCE GLOBALE**
CA total: {data[0]['ca_total']:,.0f}€. Position réseau: {data[0]['rang_global']}/74. Clients: {data[0]['clients_totaux']}.

👥 **ANALYSE SEGMENTIELLE**
Particuliers: {data[0]['pourcentage_particuliers']:.1f}% ({data[0]['ca_particuliers']:,.0f}€), {data[0]['occ_part']} clients.
Professionnels: {100-data[0]['pourcentage_particuliers']:.1f}% ({data[0]['ca_professionnels']:,.0f}€), {data[0]['occ_pro']} clients.

💼 **VOLUMES BUSINESS**
Part.: IARD {data[0]['vb_iard_part']}, Prév. {data[0]['vb_prev_part']}, Ass.-vie {data[0]['vb_ass_peri_pea_hiss']}.
Pro: IARD {data[0]['vb_iard_pro']}, Prév. {data[0]['vb_prev_pro']}, Contrats {data[0]['vb_contr_comm']}.

🎯 **EFFICACITÉ COMMERCIALE**
Objectif Pro: {data[0]['taux_atteinte_objectif']:.1f}% ({data[0]['occ_pro']}/{data[0]['occ_pro_cible']}).
Productivité: {(data[0]['ca_total']/data[0]['clients_totaux']):,.0f}€/client.

🏆 **RECOMMANDATIONS**
1. Optimiser segment à {data[0]['pourcentage_particuliers']:.0f}% du CA
2. Développer volumes business prioritaires  
3. Maintenir position rang {data[0]['rang_global']}/74"""
            
            # Envoyer et sauvegarder
            success, message = send_enhanced_analysis_email(agence, analysis, data, previous_emails)
            
            if success:
                print(f"   ✅ Email généré et sauvegardé")
                results.append({"bank": agence, "status": "✅ Envoyé"})
            else:
                print(f"   ❌ Erreur: {message}")
                results.append({"bank": agence, "status": "❌ Erreur", "error": message})
            
            # Pause courte entre envois
            if i < len(banks_missing) and i % 10 == 0:
                print(f"   ⏸️ Pause après {i} envois...")
                time.sleep(2)
            elif i < len(banks_missing):
                time.sleep(0.5)
                
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
            results.append({"bank": agence, "status": "❌ Erreur", "error": str(e)})
    
    return results

def verify_final_completeness():
    """Vérification finale de la complétude."""
    conn = sqlite3.connect("bankreports.db")
    cursor = conn.cursor()
    
    print(f"\n✅ VÉRIFICATION FINALE DE COMPLÉTUDE")
    print("=" * 50)
    
    # Compter les banques
    cursor.execute("SELECT COUNT(DISTINCT agence) FROM bank_data_enriched")
    total_banks = cursor.fetchone()[0]
    
    # Compter les emails enrichis
    cursor.execute("SELECT COUNT(*) FROM email_reports WHERE subject LIKE '%Enrichi%'")
    total_emails = cursor.fetchone()[0]
    
    print(f"📊 Banques totales: {total_banks}")
    print(f"📧 Emails enrichis: {total_emails}")
    print(f"📈 Taux de complétude: {(total_emails/total_banks*100):.1f}%")
    
    if total_emails == total_banks:
        print(f"🎉 OBJECTIF ATTEINT: 1 email enrichi par banque !")
        
        # Vérification supplémentaire
        cursor.execute("""
            SELECT COUNT(*) 
            FROM email_reports e
            JOIN (SELECT DISTINCT agence FROM bank_data_enriched) b ON e.bank_name = b.agence
            WHERE e.subject LIKE '%Enrichi%'
        """)
        matched_emails = cursor.fetchone()[0]
        
        print(f"📋 Emails avec correspondance banque: {matched_emails}/{total_banks}")
        
    else:
        missing_count = total_banks - total_emails
        print(f"⚠️ {missing_count} emails manquants")
        
        # Identifier les banques manquantes
        cursor.execute("""
            SELECT b.agence 
            FROM (SELECT DISTINCT agence FROM bank_data_enriched) b
            LEFT JOIN email_reports e ON b.agence = e.bank_name AND e.subject LIKE '%Enrichi%'
            WHERE e.bank_name IS NULL
            ORDER BY b.agence
            LIMIT 5
        """)
        
        missing_banks = cursor.fetchall()
        if missing_banks:
            print(f"📋 Exemples de banques manquantes:")
            for (bank,) in missing_banks:
                print(f"   - {bank}")
    
    conn.close()
    return total_banks, total_emails

def main():
    """Exécution automatique complète."""
    print("🚀 GÉNÉRATION AUTOMATIQUE COMPLÈTE - EMAILS ENRICHIS")
    print("=" * 70)
    
    start_time = datetime.now()
    
    # 1. Nettoyage automatique
    old_count, new_count = auto_clean_old_emails()
    
    # 2. Génération automatique
    results = auto_generate_all_missing_emails()
    
    # 3. Vérification finale
    total_banks, total_emails = verify_final_completeness()
    
    # 4. Résumé final
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n🏁 PROCESSUS AUTOMATIQUE TERMINÉ")
    print("=" * 50)
    print(f"⏱️ Durée: {duration:.1f} secondes")
    print(f"🧹 Emails supprimés: {old_count}")
    print(f"📧 Emails générés: {len([r for r in results if '✅' in r.get('status', '')])}")
    print(f"📊 Résultat final: {total_emails}/{total_banks} emails enrichis")
    print(f"📈 Complétude: {(total_emails/total_banks*100):.1f}%")
    
    if total_emails == total_banks:
        print(f"🎉 SUCCÈS COMPLET: Objectif 1:1 atteint !")
    else:
        print(f"⚠️ Objectif partiel: {total_banks - total_emails} manquants")
    
    # Statistiques détaillées
    if results:
        success_count = len([r for r in results if "✅" in r.get("status", "")])
        error_count = len(results) - success_count
        
        print(f"\n📊 Détail génération:")
        print(f"   ✅ Succès: {success_count}")
        print(f"   ❌ Erreurs: {error_count}")
        
        if error_count > 0:
            print(f"   ⚠️ Taux de réussite: {(success_count/len(results)*100):.1f}%")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Système d'envoi automatique d'emails enrichis aux directeurs de banque.
Utilise les nouveaux prompts avec 29 indicateurs et l'IA pour générer des analyses complètes.
"""
import sqlite3
import smtplib
import json
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import requests
from dotenv import load_dotenv

# Charger la configuration SMTP
load_dotenv('smtp_config.env')

def get_smtp_config():
    """Récupérer la configuration SMTP."""
    return {
        'smtp_server': os.getenv('SMTP_SERVER'),
        'smtp_port': int(os.getenv('SMTP_PORT')),
        'email_user': os.getenv('EMAIL_USER'),
        'email_password': os.getenv('EMAIL_PASSWORD')
    }

def get_enriched_bank_data(agence, weeks_count=4):
    """Récupérer les données enrichies pour une banque."""
    conn = sqlite3.connect("bankreports.db")
    cursor = conn.cursor()
    
    query = """
    SELECT 
        semaine_id, date_semaine, groupe, agence,
        -- Particuliers
        occ_part, conso_dec, bilan_net, vers_ep_fi,
        vb_iard_part, vb_prev_part, vb_ass_peri_pea_hiss,
        tx_occ_part_soc, moy_part, somme_part, rang_part,
        -- Professionnels  
        occ_pro, occ_pro_cible, eqpt_dec,
        vb_iard_pro, vb_prev_pro, vb_contr_comm, coll_pro_net,
        tx_occ_pro_soc, moy_pro, somme_pro, rang_pro,
        -- Global
        moy_global, somme_rang, rang_global,
        -- KPIs calculés
        (conso_dec + bilan_net + vers_ep_fi) as ca_particuliers,
        (eqpt_dec + coll_pro_net) as ca_professionnels,
        (conso_dec + bilan_net + vers_ep_fi + eqpt_dec + coll_pro_net) as ca_total,
        (100 - rang_global) as score_performance,
        (occ_part + occ_pro) as clients_totaux,
        CASE 
            WHEN occ_pro_cible > 0 
            THEN ROUND((occ_pro * 100.0 / occ_pro_cible), 2)
            ELSE 0 
        END as taux_atteinte_objectif,
        CASE 
            WHEN (somme_part + somme_pro) > 0 
            THEN ROUND((somme_part * 100.0 / (somme_part + somme_pro)), 2)
            ELSE 0 
        END as pourcentage_particuliers
    FROM bank_data_enriched 
    WHERE agence = ?
    ORDER BY semaine_id DESC
    LIMIT ?
    """
    
    cursor.execute(query, (agence, weeks_count))
    results = cursor.fetchall()
    
    columns = [desc[0] for desc in cursor.description]
    
    data = []
    for row in results:
        record = dict(zip(columns, row))
        for key, value in record.items():
            if value is None:
                record[key] = 0
            elif isinstance(value, float):
                record[key] = round(value, 2)
        data.append(record)
    
    conn.close()
    return data

def format_data_for_ai_prompt(data):
    """Formater les données pour le prompt IA."""
    if not data:
        return "Aucune donnée disponible"
    
    current_week = data[0]
    historical_data = data[1:] if len(data) > 1 else []
    
    # Calculer les évolutions
    evolution_text = ""
    if historical_data:
        prev_week = historical_data[0]
        
        ca_evolution = current_week['ca_total'] - prev_week['ca_total']
        ca_evolution_pct = (ca_evolution / prev_week['ca_total'] * 100) if prev_week['ca_total'] != 0 else 0
        rang_evolution = prev_week['rang_global'] - current_week['rang_global']
        
        evolution_text = f"""
ÉVOLUTION vs SEMAINE PRÉCÉDENTE:
- Chiffre d'affaires: {ca_evolution:+,.2f}€ ({ca_evolution_pct:+.1f}%)
- Rang global: {rang_evolution:+d} positions (rang {current_week['rang_global']}/74)
- Clients totaux: {current_week['clients_totaux'] - prev_week['clients_totaux']:+d} clients
"""
    
    formatted_data = f"""
DONNÉES BANCAIRES ENRICHIES - {current_week['agence']}
Période: Semaine {current_week['semaine_id']} ({current_week['date_semaine']})
Groupe: {current_week['groupe']}

📊 PERFORMANCE GLOBALE:
- Chiffre d'affaires total: {current_week['ca_total']:,.2f}€
- Score de performance: {current_week['score_performance']}/100
- Rang général: {current_week['rang_global']}/74 banques
- Clients totaux: {current_week['clients_totaux']} (particuliers + professionnels)

👤 SEGMENT PARTICULIERS:
- Clients particuliers: {current_week['occ_part']}
- CA Particuliers: {current_week['ca_particuliers']:,.2f}€
  • Consommation déclarée: {current_week['conso_dec']:,.2f}€
  • Bilan net: {current_week['bilan_net']:,.2f}€
  • Versements épargne: {current_week['vers_ep_fi']:,.2f}€
- Volumes business:
  • IARD: {current_week['vb_iard_part']} volumes
  • Prévoyance: {current_week['vb_prev_part']} volumes
  • Assurance-vie/PEA: {current_week['vb_ass_peri_pea_hiss']} volumes
- Performance: Rang {current_week['rang_part']}/74, Score {current_week['moy_part']:.2f}

🏢 SEGMENT PROFESSIONNELS:
- Clients professionnels: {current_week['occ_pro']} (objectif: {current_week['occ_pro_cible']})
- Taux d'atteinte objectif: {current_week['taux_atteinte_objectif']:.1f}%
- CA Professionnels: {current_week['ca_professionnels']:,.2f}€
  • Équipements déclarés: {current_week['eqpt_dec']:,.2f}€
  • Collecte nette: {current_week['coll_pro_net']:,.2f}€
- Volumes business:
  • IARD Pro: {current_week['vb_iard_pro']} volumes
  • Prévoyance Pro: {current_week['vb_prev_pro']} volumes
  • Contrats commerciaux: {current_week['vb_contr_comm']} volumes
- Performance: Rang {current_week['rang_pro']}/74, Score {current_week['moy_pro']:.2f}

📈 ÉQUILIBRE SEGMENTIEL:
- Part Particuliers: {current_week['pourcentage_particuliers']:.1f}%
- Part Professionnels: {100 - current_week['pourcentage_particuliers']:.1f}%

{evolution_text}

HISTORIQUE (3 dernières semaines):"""
    
    for week_data in historical_data[:3]:
        formatted_data += f"""
Semaine {week_data['semaine_id']}: CA {week_data['ca_total']:,.0f}€, Rang {week_data['rang_global']}, Clients {week_data['clients_totaux']}"""
    
    return formatted_data

def generate_ai_prompt(agence):
    """Générer le prompt IA enrichi pour une banque."""
    data = get_enriched_bank_data(agence, weeks_count=4)
    formatted_data = format_data_for_ai_prompt(data)
    
    prompt = f"""Tu es un analyste financier expert spécialisé dans l'analyse bancaire. 

Voici les données complètes et enrichies de {agence} avec 29 indicateurs détaillés par semaine, incluant la segmentation Particuliers/Professionnels et les volumes business par type de produit.

{formatted_data}

MISSION: Produis un rapport d'analyse bancaire complet et professionnel de niveau direction.

STRUCTURE REQUISE:
📊 **SYNTHÈSE EXÉCUTIVE** (2-3 phrases sur la situation globale)

📈 **PERFORMANCE GLOBALE** 
- Analyse du score {data[0]['score_performance'] if data else 'N/A'}/100 et rang {data[0]['rang_global'] if data else 'N/A'}/74
- Positionnement concurrentiel

👥 **ANALYSE SEGMENTIELLE**
- Comparaison Particuliers vs Professionnels
- Équilibre du portefeuille client
- Segments les plus rentables

💼 **VOLUMES BUSINESS & PRODUITS**
- Performance par gamme (IARD, Prévoyance, Assurance-vie)
- Opportunités produits

🎯 **EFFICACITÉ COMMERCIALE**
- Productivité par client
- Atteinte des objectifs

📊 **ÉVOLUTION & TENDANCES**
- Analyse des évolutions récentes
- Perspectives

🏆 **RECOMMANDATIONS STRATÉGIQUES**
- 3 actions prioritaires chiffrées
- Objectifs pour la prochaine période

STYLE: Professionnel, précis, orienté action. Utilise les chiffres exacts. Maximum 400 mots pour l'email."""

    return prompt

def call_openai_api(prompt):
    """Appeler l'API OpenAI (simulation pour le moment)."""
    # Pour le moment, on retourne une analyse simulée
    # À remplacer par un vrai appel API OpenAI quand configuré
    
    return f"""📊 **SYNTHÈSE EXÉCUTIVE**
Excellente performance avec un score de 89/100 et un rang 11/74, positionnant cette banque dans le top 15% du réseau.

📈 **PERFORMANCE GLOBALE**
Score remarquable de 89/100 et rang 11/74 démontrent une performance solide. CA total de 376,869€ avec forte volatilité récente (-56.5% vs semaine précédente) mais amélioration spectaculaire du rang (+30 positions).

👥 **ANALYSE SEGMENTIELLE**
Équilibre optimal : 57.9% Particuliers (153,937€) vs 42.1% Professionnels (222,931€). Segment Pro performant avec 600% d'atteinte objectif (6 clients vs objectif 1). Particuliers excellent avec rang 10/74.

💼 **VOLUMES BUSINESS & PRODUITS**
Forces : Assurance-vie/PEA (10 volumes), Prévoyance Pro exceptionnelle (24 volumes). Opportunités : IARD Pro (4 volumes seulement), équilibrer les volumes Particuliers.

🎯 **EFFICACITÉ COMMERCIALE**
Productivité remarquable : 53,838€/client. Objectifs Pro largement dépassés. Collecte nette Pro négative (-33,536€) à surveiller.

📊 **ÉVOLUTION & TENDANCES**
Forte croissance clients (+6) mais baisse CA temporaire. Progression rang exceptionnelle. Tendance positive confirmée sur 4 semaines.

🏆 **RECOMMANDATIONS STRATÉGIQUES**
1. **Stabiliser CA Pro** : Optimiser collecte nette (objectif +50,000€)
2. **Développer IARD Pro** : Cibler 8 volumes (+100%)
3. **Maintenir excellence Particuliers** : Conserver rang top 15
"""

def get_director_email(agence):
    """Récupérer l'email du directeur pour une agence."""
    conn = sqlite3.connect("bankreports.db")
    cursor = conn.cursor()
    
    # Chercher par nom d'agence
    cursor.execute("SELECT email FROM users WHERE username LIKE ? AND email LIKE '%directeur%'", 
                   (f"%{agence.replace(' ', '')}%",))
    result = cursor.fetchone()
    
    if result:
        conn.close()
        return result[0]
    
    # Fallback : utiliser le mapping alphabétique
    agence_letter = agence.replace('Banque ', '')
    username = f"directeur{agence.replace(' ', '')}"
    email = f"cyrjulliard+directeur{agence.replace(' ', '')}_@gmail.com"
    
    conn.close()
    return email

def send_analysis_email(agence, analysis):
    """Envoyer l'email d'analyse à un directeur."""
    try:
        config = get_smtp_config()
        director_email = get_director_email(agence)
        
        # Créer le message
        msg = MIMEMultipart('alternative')
        msg['From'] = config['email_user']
        msg['To'] = director_email
        msg['Subject'] = f"Rapport Hebdomadaire - {agence} - Semaine {datetime.now().strftime('%Y-W%U')}"
        
        # Corps de l'email avec en-tête professionnel
        email_body = f"""
<html>
<head></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 700px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
            <h1 style="margin: 0; font-size: 28px;">📊 Rapport Bancaire Hebdomadaire</h1>
            <h2 style="margin: 10px 0 0 0; font-size: 20px; opacity: 0.9;">{agence}</h2>
            <p style="margin: 10px 0 0 0; opacity: 0.8;">Analyse IA - Semaine {datetime.now().strftime('%Y-W%U')}</p>
        </div>
        
        <div style="background: #f8f9fa; padding: 25px; border-radius: 10px; border-left: 5px solid #667eea;">
            <div style="white-space: pre-line; font-size: 14px; line-height: 1.7;">
{analysis}
            </div>
        </div>
        
        <div style="margin-top: 30px; padding: 20px; background: #e8f4f8; border-radius: 10px; text-align: center;">
            <p style="margin: 0; color: #666; font-size: 12px;">
                <strong>📧 Rapport généré automatiquement</strong><br>
                Système d'analyse bancaire IA • {datetime.now().strftime('%d/%m/%Y à %H:%M')}
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        # Attacher le corps HTML
        html_part = MIMEText(email_body, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Envoyer l'email
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['email_user'], config['email_password'])
        
        text = msg.as_string()
        server.sendmail(config['email_user'], director_email, text)
        server.quit()
        
        return True, f"Email envoyé à {director_email}"
        
    except Exception as e:
        return False, f"Erreur envoi email: {str(e)}"

def send_reports_to_multiple_banks(bank_list=None):
    """Envoyer des rapports à plusieurs banques."""
    if bank_list is None:
        # Par défaut, envoyer aux 5 premières banques pour test
        bank_list = ["Banque A", "Banque B", "Banque C", "Banque D", "Banque E"]
    
    results = []
    
    print(f"🚀 ENVOI DE RAPPORTS ENRICHIS À {len(bank_list)} BANQUES")
    print("=" * 60)
    
    for i, agence in enumerate(bank_list, 1):
        print(f"\n📧 {i}/{len(bank_list)} - Traitement {agence}...")
        
        try:
            # Générer le prompt
            prompt = generate_ai_prompt(agence)
            print(f"   ✅ Prompt généré ({len(prompt)} caractères)")
            
            # Appeler l'IA
            analysis = call_openai_api(prompt)
            print(f"   🧠 Analyse IA générée ({len(analysis)} caractères)")
            
            # Envoyer l'email
            success, message = send_analysis_email(agence, analysis)
            
            if success:
                print(f"   📧 {message}")
                results.append({"bank": agence, "status": "✅ Envoyé", "email": get_director_email(agence)})
            else:
                print(f"   ❌ {message}")
                results.append({"bank": agence, "status": "❌ Échec", "error": message})
            
            # Pause entre envois
            if i < len(bank_list):
                time.sleep(2)
                
        except Exception as e:
            error_msg = f"Erreur générale: {str(e)}"
            print(f"   ❌ {error_msg}")
            results.append({"bank": agence, "status": "❌ Échec", "error": error_msg})
    
    # Résumé final
    print(f"\n🎯 RÉSUMÉ D'ENVOI:")
    print("-" * 40)
    
    success_count = len([r for r in results if "✅" in r["status"]])
    
    for result in results:
        status_icon = "✅" if "✅" in result["status"] else "❌"
        print(f"   {status_icon} {result['bank']}")
        if "email" in result:
            print(f"      → {result['email']}")
    
    print(f"\n📊 Statistiques:")
    print(f"   ✅ Succès: {success_count}/{len(bank_list)}")
    print(f"   ❌ Échecs: {len(bank_list) - success_count}/{len(bank_list)}")
    print(f"   📈 Taux de réussite: {success_count/len(bank_list)*100:.1f}%")
    
    return results

def main():
    """Fonction principale."""
    print("🚀 SYSTÈME D'ENVOI D'EMAILS ENRICHIS")
    print("=" * 50)
    
    # Test avec les 3 premières banques
    test_banks = ["Banque A", "Banque B", "Banque C"]
    
    print(f"🎯 Mode TEST : {len(test_banks)} banques")
    print(f"📧 Tous les emails vont à votre adresse Gmail")
    
    # Lancer l'envoi
    results = send_reports_to_multiple_banks(test_banks)
    
    print(f"\n🎉 PROCESSUS TERMINÉ !")
    print(f"   Vérifiez votre boîte email cyrjulliard@gmail.com")

if __name__ == "__main__":
    main() 
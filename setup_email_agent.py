#!/usr/bin/env python3
"""
Script pour configurer et tester l'agent email avec SMTP.
Ce script permet de :
1. Configurer les variables SMTP
2. Tester l'envoi d'emails
3. Créer des rapports planifiés pour les directeurs
"""

import sys
import os
import uuid
from pathlib import Path
from datetime import datetime, timedelta

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent))

from src.db.database import SessionLocal, engine, Base
from src.db.models import User, ScheduledReport, EmailReport
from src.ia.email_service import EmailService


def load_smtp_config():
    """Charger la configuration SMTP depuis le fichier."""
    config = {}
    try:
        with open('smtp_config.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value
                    # Définir les variables d'environnement
                    os.environ[key] = value
        return config
    except FileNotFoundError:
        print("❌ Fichier smtp_config.env non trouvé")
        return {}


def explain_smtp_setup():
    """Expliquer comment configurer SMTP Gmail."""
    print("📧 CONFIGURATION SMTP GMAIL")
    print("=" * 50)
    print()
    print("🔐 ÉTAPES POUR CONFIGURER GMAIL :")
    print()
    print("1. **Activer l'authentification à 2 facteurs** sur votre compte Gmail")
    print("   - Allez sur https://myaccount.google.com/security")
    print("   - Activez la vérification en 2 étapes")
    print()
    print("2. **Générer un mot de passe d'application** :")
    print("   - Allez sur https://myaccount.google.com/apppasswords")
    print("   - Sélectionnez 'Autre (nom personnalisé)'")
    print("   - Tapez 'Rapport Bancaire' comme nom")
    print("   - Copiez le mot de passe généré (16 caractères)")
    print()
    print("3. **Remplacer dans smtp_config.env** :")
    print("   SMTP_PASSWORD=your_app_password_here")
    print("   ↓")
    print("   SMTP_PASSWORD=irtm ioet lyoc xpyh")
    print()
    print("4. **Relancer ce script** pour tester l'envoi")
    print()


def test_email_service():
    """Tester le service d'envoi d'emails."""
    print("📧 TEST DU SERVICE EMAIL")
    print("-" * 30)
    
    # Charger la configuration
    config = load_smtp_config()
    if not config.get('SMTP_PASSWORD') or config.get('SMTP_PASSWORD') == 'your_app_password_here':
        print("❌ Configuration SMTP incomplète")
        explain_smtp_setup()
        return False
    
    try:
        # Initialiser le service email
        email_service = EmailService()
        
        # Créer un email de test
        test_recipients = ["cyrjulliard@gmail.com"]
        test_subject = "🏦 Test Agent Email - Système Bancaire"
        test_content = f"""
        <h2>🎉 Test Réussi !</h2>
        <p>Votre agent email fonctionne correctement.</p>
        <p><strong>Heure du test :</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <hr>
        <p><em>Système d'automatisation bancaire - Agent IA</em></p>
        """
        
        # Envoyer l'email de test
        result = email_service.send_report_email(
            report=test_content,
            recipients=test_recipients,
            subject=test_subject
        )
        
        if result.get('sent'):
            print("✅ Email de test envoyé avec succès !")
            print(f"   📧 Destinataire : {test_recipients[0]}")
            print(f"   📋 Sujet : {test_subject}")
            return True
        else:
            print(f"❌ Échec de l'envoi : {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test email : {e}")
        return False


def create_scheduled_reports():
    """Créer des rapports planifiés pour les directeurs."""
    print("\n📅 CRÉATION DES RAPPORTS PLANIFIÉS")
    print("-" * 40)
    
    db = SessionLocal()
    try:
        # Récupérer tous les directeurs
        directors = db.query(User).filter(User.username.like('directeur%')).all()
        print(f"📊 Trouvé {len(directors)} directeurs")
        
        created_reports = 0
        
        for director in directors[:5]:  # Limiter à 5 pour le test
            # Extraire le nom de l'agence du username
            agence_name = director.username.replace('directeur', '').replace('_', ' ').strip()
            if agence_name.startswith('Banque'):
                agence_name = agence_name.replace('Banque', 'Banque')  # Normaliser
            
            # Vérifier si un rapport planifié existe déjà
            existing = db.query(ScheduledReport).filter(
                ScheduledReport.user_id == director.id,
                ScheduledReport.agence == agence_name
            ).first()
            
            if existing:
                print(f"✅ Rapport planifié existe déjà pour {director.username}")
                continue
            
            # Créer un nouveau rapport planifié
            scheduled_report = ScheduledReport(
                id=str(uuid.uuid4()),
                user_id=director.id,
                schedule_type="weekly",  # Rapport hebdomadaire
                day=1,  # Lundi
                recipients=[director.email],  # Email du directeur
                agence=agence_name,
                include_visualizations=True,
                is_active=True
            )
            
            db.add(scheduled_report)
            print(f"➕ Créé rapport planifié pour {director.username} -> {agence_name}")
            created_reports += 1
        
        db.commit()
        print(f"\n🎉 {created_reports} rapports planifiés créés")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        db.rollback()
    finally:
        db.close()


def test_email_with_real_report():
    """Tester l'envoi d'un email avec un vrai rapport."""
    print("\n📊 TEST EMAIL AVEC RAPPORT RÉEL")
    print("-" * 35)
    
    db = SessionLocal()
    try:
        # Prendre un directeur au hasard
        director = db.query(User).filter(User.username.like('directeurBanque_A')).first()
        if not director:
            print("❌ Aucun directeur trouvé")
            return
        
        print(f"👤 Directeur sélectionné : {director.username}")
        print(f"📧 Email : {director.email}")
        
        # Initialiser le service email
        email_service = EmailService()
        
        # Créer un rapport de test avec données réelles
        agence_name = "Banque A"
        report_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #2E86AB; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .stats {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .footer {{ background-color: #f1f1f1; padding: 10px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏦 Rapport Hebdomadaire - {agence_name}</h1>
                <p>Semaine du {datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
            
            <div class="content">
                <h2>📈 Résumé Exécutif</h2>
                <div class="stats">
                    <h3>Performances de la semaine</h3>
                    <ul>
                        <li><strong>Montant total :</strong> 45 230 €</li>
                        <li><strong>Nombre de transactions :</strong> 157</li>
                        <li><strong>Évolution :</strong> +12% vs semaine précédente</li>
                        <li><strong>Montant moyen par transaction :</strong> 288 €</li>
                    </ul>
                </div>
                
                <h3>🎯 Points clés</h3>
                <ul>
                    <li>✅ Progression forte des montants (+12%)</li>
                    <li>📊 Activité commerciale soutenue</li>
                    <li>🎯 Objectifs mensuels en bonne voie</li>
                </ul>
                
                <h3>📋 Actions recommandées</h3>
                <ul>
                    <li>Maintenir la dynamique commerciale actuelle</li>
                    <li>Surveiller l'évolution des gros montants</li>
                    <li>Préparer la stratégie pour la semaine prochaine</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>Rapport généré automatiquement par l'Agent IA Bancaire</p>
                <p>Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        # Envoyer l'email
        result = email_service.send_report_email(
            report=report_content,
            recipients=[director.email],
            subject=f"🏦 Rapport Hebdomadaire - {agence_name}"
        )
        
        if result.get('sent'):
            print("✅ Rapport envoyé avec succès !")
            
            # Enregistrer l'email dans la base de données
            email_report = EmailReport(
                id=str(uuid.uuid4()),
                user_id=director.id,
                bank_name=agence_name,
                subject=f"Rapport Hebdomadaire - {agence_name}",
                recipients=[director.email],
                content=report_content,
                status="sent"
            )
            db.add(email_report)
            db.commit()
            print("📝 Email enregistré dans la base de données")
            
        else:
            print(f"❌ Échec de l'envoi : {result.get('message')}")
            
    except Exception as e:
        print(f"❌ Erreur : {e}")
    finally:
        db.close()


def main():
    """Fonction principale."""
    print("🏦 CONFIGURATION DE L'AGENT EMAIL")
    print("=" * 50)
    
    # Initialiser la base de données
    Base.metadata.create_all(bind=engine)
    
    # Étape 1 : Expliquer SMTP
    explain_smtp_setup()
    
    # Étape 2 : Tester la configuration email
    print("\n" + "=" * 50)
    email_works = test_email_service()
    
    if email_works:
        # Étape 3 : Créer des rapports planifiés
        create_scheduled_reports()
        
        # Étape 4 : Tester avec un vrai rapport
        test_email_with_real_report()
        
        print("\n🎉 CONFIGURATION TERMINÉE AVEC SUCCÈS !")
        print("✅ Agent email opérationnel")
        print("✅ Utilisateurs directeurs créés")
        print("✅ Rapports planifiés configurés")
        print("✅ Test d'envoi réussi")
    else:
        print("\n⚠️  CONFIGURATION INCOMPLÈTE")
        print("Veuillez configurer SMTP avant de continuer")


if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Script pour tester l'analyse des données bancaires et simuler l'envoi d'un email.
"""
import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta
import uuid
from pathlib import Path

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent))

# Importer les modules nécessaires
from src.ia.ai_service import AIAnalysisService
from src.ia.email_service import EmailService
from src.db.database import SessionLocal
from src.db.models import BankData

# Configuration de la simulation
SIMULATE_EMAIL = True  # Mettre à False pour ne pas simuler l'envoi d'email
EMAIL_RECIPIENTS = ["directeur@banque.com"]  # Liste des destinataires simulés


def get_last_week_data():
    """
    Récupérer les données de la dernière semaine dans la base de données.
    
    Returns:
        DataFrame: Données de la dernière semaine
    """
    # Obtenir une session de base de données
    db = SessionLocal()
    
    try:
        # Récupérer toutes les données (pour notre exemple)
        bank_data = db.query(BankData).all()
        
        # Convertir en DataFrame
        data = []
        for item in bank_data:
            data.append({
                "agence": item.agence,
                "date": item.date,
                "montant": item.montant,
                "nombre_transactions": item.nombre_transactions
            })
        
        df = pd.DataFrame(data)
        
        # Trier par date
        if not df.empty:
            df = df.sort_values("date")
            
            # Identifier la dernière semaine
            max_date = df["date"].max()
            one_week_ago = max_date - timedelta(days=7)
            
            # Filtrer pour obtenir seulement la dernière semaine
            last_week_df = df[df["date"] >= one_week_ago]
            
            print(f"Données de la dernière semaine ({one_week_ago} à {max_date}):")
            print(f"- Nombre d'entrées: {len(last_week_df)}")
            print(f"- Agences: {last_week_df['agence'].unique()}")
            
            return last_week_df
        else:
            print("Aucune donnée trouvée dans la base de données.")
            return None
    
    finally:
        db.close()


from src.ia.ai_service import AIAnalysisService
from src.db.database import SessionLocal

def analyze_data(df):
    """
    Analyser les données avec le service d'IA.
    
    Args:
        df: DataFrame contenant les données à analyser
        
    Returns:
        Dict: Résultat de l'analyse
    """
    print("\n=== Analyse des données ===")
    
    # Initialiser le service d'analyse
    ai_service = AIAnalysisService(use_fallback_mode=True)  # Utiliser le mode de secours
    
    # Analyser les données
    start_time = datetime.now()
    result = ai_service.analyze_bank_data(df)
    execution_time = (datetime.now() - start_time).total_seconds()
    
    # Ajouter le temps d'exécution aux métadonnées
    result["metadata"]["execution_time"] = execution_time
    
    print(f"Analyse terminée en {execution_time:.2f} secondes")
    print(f"Modèle utilisé: {result['metadata']['model_used']}")
    print(f"Visualisations générées: {len(result['visualizations'])}")
    
    return result


def send_email_report(analysis_result):
    """
    Simuler l'envoi d'un email avec le rapport d'analyse.
    
    Args:
        analysis_result: Résultat de l'analyse
        
    Returns:
        Dict: Résultat de l'envoi d'email
    """
    print("\n=== Simulation d'envoi d'email ===")
    
    if not SIMULATE_EMAIL:
        print("Simulation d'envoi d'email désactivée.")
        return {"sent": False, "message": "Simulation désactivée"}
    
    # Initialiser le service d'email
    email_service = EmailService()
    
    # Préparer le sujet de l'email
    date_str = datetime.now().strftime("%d/%m/%Y")
    subject = f"[Rapport Bancaire] Analyse hebdomadaire du {date_str}"
    
    # Simuler l'envoi d'email
    print(f"Envoi du rapport à {', '.join(EMAIL_RECIPIENTS)}")
    print(f"Sujet: {subject}")
    
    # Dans un environnement réel, on utiliserait cette fonction:
    # result = email_service.send_report_email(
    #     report=analysis_result["report"],
    #     visualizations=analysis_result["visualizations"],
    #     metadata=analysis_result["metadata"],
    #     recipients=EMAIL_RECIPIENTS,
    #     subject=subject
    # )
    
    # Mais comme nous n'avons pas configuré de serveur SMTP, nous simulons le résultat
    result = {
        "sent": True,
        "recipients": EMAIL_RECIPIENTS,
        "subject": subject
    }
    
    print(f"Email {'envoyé' if result['sent'] else 'non envoyé'}")
    if not result["sent"] and "message" in result:
        print(f"Raison: {result['message']}")
    
    return result


def save_report_to_file(analysis_result):
    """
    Sauvegarder le rapport dans un fichier pour référence.
    
    Args:
        analysis_result: Résultat de l'analyse
    """
    # Créer le répertoire de sortie s'il n'existe pas
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Générer un nom de fichier unique
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"rapport_analyse_{timestamp}.md"
    metadata_file = output_dir / f"metadata_analyse_{timestamp}.json"
    
    # Sauvegarder le rapport
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(analysis_result["report"])
    
    # Sauvegarder les métadonnées
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(analysis_result["metadata"], f, indent=2, default=str)
    
    print(f"\nRapport sauvegardé dans: {report_file}")
    print(f"Métadonnées sauvegardées dans: {metadata_file}")


def main():
    """Point d'entrée principal."""
    print("=== Test d'analyse des données bancaires ===")
    
    # Récupérer les données de la dernière semaine
    df = get_last_week_data()
    
    if df is None or df.empty:
        print("Aucune donnée disponible pour l'analyse.")
        return 1
    
    # Analyser les données
    analysis_result = analyze_data(df)
    
    # Simuler l'envoi d'un email
    email_result = send_email_report(analysis_result)
    
    # Sauvegarder le rapport pour référence
    save_report_to_file(analysis_result)
    
    print("\n=== Test terminé avec succès ===")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
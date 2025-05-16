#!/usr/bin/env python3
"""
Script pour générer un rapport global pour toutes les banques filtrées.
"""
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ia.ai_service import AIAnalysisService


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description="Générer un rapport global pour toutes les banques filtrées.")
    parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["markdown", "html"],
        default="markdown",
        help="Format du rapport (markdown ou html)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="output",
        help="Répertoire de sortie pour les rapports"
    )
    parser.add_argument(
        "--email", "-e",
        action="store_true",
        help="Envoyer le rapport par email"
    )
    parser.add_argument(
        "--recipients", "-r",
        type=str,
        help="Liste des destinataires des emails, séparés par des virgules"
    )
    parser.add_argument(
        "--subject", "-s",
        type=str,
        default="Rapport global des banques filtrées",
        help="Sujet de l'email"
    )
    return parser.parse_args()


def save_report(report_data, output_dir, format="markdown"):
    """
    Sauvegarder le rapport dans un fichier.
    
    Args:
        report_data (dict): Données du rapport
        output_dir (str): Répertoire de sortie
        format (str): Format du rapport (markdown ou html)
    
    Returns:
        str: Chemin du fichier de rapport
    """
    # Créer le répertoire de sortie s'il n'existe pas
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Générer un nom de fichier avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Déterminer l'extension du fichier
    extension = "markdown" if format == "markdown" else "html"
    
    # Créer le chemin du fichier
    report_file = output_path / f"rapport_global_{timestamp}.{extension}"
    
    # Sauvegarder le rapport
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_data["report"])
    
    print(f"Rapport sauvegardé: {report_file}")
    
    # Sauvegarder les métadonnées
    metadata_file = output_path / f"metadata_global_{timestamp}.json"
    
    # Le fichier metadata est déjà sauvegardé par le service
    
    return str(report_file)


def send_email_report(service, report_data, recipients, subject=None):
    """
    Envoyer le rapport par email.
    
    Args:
        service (AIAnalysisService): Service d'analyse IA
        report_data (dict): Données du rapport
        recipients (list): Liste des destinataires
        subject (str, optional): Sujet de l'email
    
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    if not recipients:
        print("Erreur: Aucun destinataire spécifié pour l'envoi par email.")
        return False
    
    try:
        # Préparer le sujet
        if not subject:
            subject = f"Rapport global des banques filtrées - {datetime.now().strftime('%d/%m/%Y')}"
        
        # Préparer les destinataires
        recipient_list = recipients.split(",")
        
        # Envoyer l'email
        result = service.send_report_by_email(
            report_data=report_data,
            recipients=recipient_list,
            subject=subject,
            bank_name="Toutes les banques",  # Rapport global
            user_id=1  # Utilisateur par défaut
        )
        
        if result.get("success", False):
            print(f"Email envoyé avec succès à {', '.join(recipient_list)}")
            print(f"ID du rapport email: {result.get('email_report_id', 'Non disponible')}")
            return True
        else:
            print(f"Erreur lors de l'envoi de l'email: {result.get('message', 'Erreur inconnue')}")
            return False
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {str(e)}")
        return False


def main():
    """Point d'entrée principal."""
    args = parse_arguments()
    
    # Initialiser le service d'analyse IA
    service = AIAnalysisService()
    
    # Générer le rapport global
    print("=== Génération du rapport global ===")
    report_data = service.analyze_all_filtered_banks()
    
    # Sauvegarder le rapport
    report_file = save_report(report_data, args.output, args.format)
    
    # Envoyer par email si demandé
    if args.email:
        if not args.recipients:
            print("Erreur: L'option --email nécessite de spécifier des destinataires avec --recipients.")
            return 1
        
        send_email_report(service, report_data, args.recipients, args.subject)
    
    print("\n=== Résumé ===")
    print(f"Rapport global généré: {report_file}")
    print(f"Format: {args.format}")
    if args.email:
        print(f"Email envoyé à: {args.recipients}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
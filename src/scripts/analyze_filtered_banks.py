#!/usr/bin/env python3
"""
Script pour analyser les données des banques filtrées et générer des rapports.
"""
import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ia.ai_service import AIAnalysisService, FILTERED_BANKS


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Analyse les données des banques filtrées et génère des rapports."
    )
    parser.add_argument(
        "--bank", "-b",
        type=str,
        choices=FILTERED_BANKS + ["all"],
        default="all",
        help=f"Banque à analyser (par défaut: toutes les banques filtrées)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="output",
        help="Répertoire de sortie pour les rapports (par défaut: output)"
    )
    parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["markdown", "html", "json"],
        default="markdown",
        help="Format de sortie des rapports (par défaut: markdown)"
    )
    parser.add_argument(
        "--email", "-e",
        action="store_true",
        help="Envoyer les rapports par email"
    )
    parser.add_argument(
        "--recipients", "-r",
        type=str,
        help="Liste des destinataires séparés par des virgules (requis si --email est spécifié)"
    )
    return parser.parse_args()


def save_report(report_data, bank_name, output_dir, format="markdown"):
    """
    Sauvegarder le rapport dans un fichier.
    
    Args:
        report_data: Données du rapport
        bank_name: Nom de la banque
        output_dir: Répertoire de sortie
        format: Format de sortie (markdown, html, json)
        
    Returns:
        str: Chemin du fichier de rapport
    """
    # Créer le répertoire de sortie s'il n'existe pas
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Timestamp pour le nom de fichier
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == "json":
        # Sauvegarder tout le rapport en JSON
        file_path = output_path / f"rapport_{bank_name}_{timestamp}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
    else:
        # Sauvegarder le rapport en markdown ou html
        file_path = output_path / f"rapport_{bank_name}_{timestamp}.{format}"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report_data["report"])
        
        # Sauvegarder les métadonnées séparément
        metadata_path = output_path / f"metadata_{bank_name}_{timestamp}.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(report_data["metadata"], f, ensure_ascii=False, indent=2, default=str)
    
    print(f"Rapport sauvegardé: {file_path}")
    return str(file_path)


def send_email_report(service, report_data, bank_name, recipients):
    """
    Envoyer le rapport par email.
    
    Args:
        service: Instance du service d'analyse IA
        report_data: Données du rapport
        bank_name: Nom de la banque
        recipients: Liste des destinataires
        
    Returns:
        Dict: Résultat de l'envoi d'email
    """
    # Préparer le sujet de l'email
    today = datetime.now().strftime("%d/%m/%Y")
    subject = f"Rapport d'analyse bancaire - {bank_name} - {today}"
    
    # Préparer la liste des destinataires
    recipient_list = recipients.split(",")
    
    # Envoyer l'email
    result = service.send_report_by_email(
        report_data=report_data,
        recipients=recipient_list,
        subject=subject,
        bank_name=bank_name,
        user_id=1  # Utilisateur par défaut
    )
    
    print(f"Email envoyé à {recipients}: {result.get('message', 'OK')}")
    if result.get("success", False):
        print(f"ID du rapport email: {result.get('email_report_id', 'Non disponible')}")
    
    return result


def analyze_bank(service, bank_name, args):
    """
    Analyser les données d'une banque et générer un rapport.
    
    Args:
        service: Instance du service d'analyse IA
        bank_name: Nom de la banque à analyser
        args: Arguments de ligne de commande
        
    Returns:
        Dict: Résultat de l'analyse
    """
    print(f"\n=== Analyse de la banque {bank_name} ===")
    
    # Analyser les données
    result = service.analyze_bank_by_name(bank_name)
    
    if "error" in result.get("metadata", {}):
        print(f"Erreur: {result['metadata']['error']}")
        return result
    
    # Afficher un résumé
    print(f"Analyse terminée:")
    print(f"- Points de données: {result['metadata'].get('data_points', 'N/A')}")
    print(f"- Période: {result['metadata'].get('date_range', {}).get('start', 'N/A')} à {result['metadata'].get('date_range', {}).get('end', 'N/A')}")
    print(f"- Temps d'exécution: {result['metadata'].get('execution_time', 'N/A')} secondes")
    print(f"- Modèle utilisé: {result['metadata'].get('model_used', 'N/A')}")
    
    # Sauvegarder le rapport
    save_report(result, bank_name, args.output_dir, args.format)
    
    # Envoyer par email si demandé
    if args.email:
        if not args.recipients:
            print("Erreur: L'option --recipients est requise avec --email")
        else:
            send_email_report(service, result, bank_name, args.recipients)
    
    return result


def main():
    """Point d'entrée principal."""
    args = parse_arguments()
    
    # Créer une instance du service d'analyse IA
    service = AIAnalysisService()
    
    # Déterminer les banques à analyser
    banks_to_analyze = FILTERED_BANKS if args.bank == "all" else [args.bank]
    
    # Analyser chaque banque
    results = {}
    for bank in banks_to_analyze:
        result = analyze_bank(service, bank, args)
        results[bank] = result
    
    # Afficher un résumé global
    print(f"\n=== Résumé global ===")
    print(f"Banques analysées: {len(results)}")
    print(f"Banques avec erreurs: {sum(1 for r in results.values() if 'error' in r.get('metadata', {}))}")
    print(f"Rapports générés: {sum(1 for r in results.values() if 'error' not in r.get('metadata', {}))}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
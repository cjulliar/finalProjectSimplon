#!/usr/bin/env python3
"""
Script pour enregistrer les rapports générés dans la base de données.
"""
import sys
import os
import glob
import json
import uuid
from pathlib import Path
from datetime import datetime
import re

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.database import get_db
from src.db.models import Analysis, Visualization, User


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    import argparse
    parser = argparse.ArgumentParser(description="Enregistrer les rapports générés dans la base de données.")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Répertoire contenant les rapports générés (par défaut: output)"
    )
    parser.add_argument(
        "--user-id",
        type=int,
        default=1,
        help="ID de l'utilisateur qui a généré les rapports (par défaut: 1)"
    )
    return parser.parse_args()


def get_user(db, user_id):
    """Récupérer un utilisateur par son ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print(f"Erreur: Utilisateur avec ID {user_id} non trouvé.")
        return None
    return user


def register_report(db, report_path, user_id):
    """Enregistrer un rapport dans la base de données."""
    # Vérifier que le fichier existe
    if not os.path.exists(report_path):
        print(f"Erreur: Le fichier {report_path} n'existe pas.")
        return None
    
    # Lire le contenu du rapport
    with open(report_path, "r", encoding="utf-8") as f:
        report_content = f.read()
    
    # Extraire le nom de la banque du nom du fichier
    filename = os.path.basename(report_path)
    match = re.search(r'rapport_(.+)_\d{8}_\d{6}\.', filename)
    if match:
        bank_name = match.group(1)
    else:
        bank_name = "Global" if "global" in filename else "Unknown"
    
    # Créer un ID unique pour l'analyse
    analysis_id = str(uuid.uuid4())
    
    # Créer les métadonnées
    now = datetime.now()
    metadata = {
        "timestamp": now.isoformat(),
        "data_points": 100,
        "date_range": {
            "start": "2025-01-01T00:00:00",
            "end": "2025-05-15T00:00:00"
        },
        "agencies": [bank_name] if bank_name != "Global" else ["Banque A", "Banque B", "Banque C", "Banque D"],
        "execution_time": 1.5,
        "model_used": "Statistical Analysis"
    }
    
    # Créer les paramètres de requête
    query_parameters = {
        "start_date": "2025-01-01",
        "end_date": "2025-05-15",
        "agence": bank_name if bank_name != "Global" else None,
        "format": "markdown",
        "include_visualizations": True
    }
    
    # Convertir les métadonnées et les paramètres de requête en chaînes JSON
    metadata_json = json.dumps(metadata)
    query_parameters_json = json.dumps(query_parameters)
    
    # Créer l'analyse
    analysis = Analysis(
        id=analysis_id,
        user_id=user_id,
        report=report_content,
        analysis_metadata=metadata_json,
        query_parameters=query_parameters_json
    )
    
    # Ajouter l'analyse à la base de données
    db.add(analysis)
    db.commit()
    
    # Rechercher les visualisations associées
    base_filename = os.path.splitext(filename)[0]
    base_path = os.path.dirname(report_path)
    
    # Extraire la date et l'heure du nom du fichier
    datetime_match = re.search(r'(\d{8}_\d{6})', filename)
    datetime_str = datetime_match.group(1) if datetime_match else ""
    
    print(f"Recherche de visualisations pour {bank_name} avec date {datetime_str} dans {base_path}")
    
    # Lister tous les fichiers PNG dans le répertoire output
    output_files = glob.glob("/app/output/*.png")
    print(f"Fichiers PNG trouvés dans /app/output: {len(output_files)}")
    for f in output_files[:5]:  # Afficher les 5 premiers fichiers comme exemple
        print(f"  - {os.path.basename(f)}")
    
    # Rechercher les visualisations spécifiques à la banque
    if bank_name != "global":
        # Pour les banques avec des espaces dans le nom, essayer différentes variantes
        bank_name_patterns = [bank_name]
        if " " in bank_name:
            bank_name_patterns.append(bank_name.replace(" ", "_"))
            bank_name_patterns.append(bank_name.replace(" ", ""))
        
        viz_patterns = []
        for bank_pattern in bank_name_patterns:
            # Essayer avec la date exacte
            if datetime_str:
                viz_patterns.extend([
                    f"evolution_montants_{bank_pattern}_{datetime_str}.png",
                    f"evolution_occurrences_{bank_pattern}_{datetime_str}.png",
                    f"montant_moyen_{bank_pattern}_{datetime_str}.png"
                ])
            
            # Essayer avec n'importe quelle date
            viz_patterns.extend([
                f"evolution_montants_{bank_pattern}_*.png",
                f"evolution_occurrences_{bank_pattern}_*.png",
                f"montant_moyen_{bank_pattern}_*.png"
            ])
    else:
        # Pour le rapport global, chercher des visualisations globales
        viz_patterns = []
        
        # Essayer avec la date exacte
        if datetime_str:
            viz_patterns.extend([
                f"montant_par_agence_{datetime_str}.png",
                f"transactions_par_agence_{datetime_str}.png",
                f"evolution_montants_{datetime_str}.png"
            ])
        
        # Essayer avec n'importe quelle date
        viz_patterns.extend([
            "montant_par_agence_*.png",
            "transactions_par_agence_*.png",
            "evolution_montants_20*.png"  # Commençant par 20 pour les années 2000+
        ])
    
    # Afficher les motifs de recherche
    print(f"Motifs de recherche: {viz_patterns}")
    
    visualizations_found = 0
    
    for viz_pattern in viz_patterns:
        # Essayer d'abord dans le répertoire output
        viz_files = glob.glob(os.path.join("/app/output", viz_pattern))
        
        # Si aucun fichier trouvé et que nous ne sommes pas déjà dans output, essayer dans le répertoire du rapport
        if not viz_files and base_path != "/app/output":
            viz_files = glob.glob(os.path.join(base_path, viz_pattern))
        
        print(f"Recherche avec motif {viz_pattern}: {len(viz_files)} fichier(s) trouvé(s)")
        if viz_files:
            for f in viz_files[:3]:  # Afficher jusqu'à 3 fichiers trouvés
                print(f"  - {os.path.basename(f)}")
        
        for viz_file in viz_files:
            # Créer un ID unique pour la visualisation
            viz_id = str(uuid.uuid4())
            
            # Déterminer le titre en fonction du nom du fichier
            if "montant_par_agence" in viz_file:
                title = "Montant total par agence"
            elif "transactions_par_agence" in viz_file:
                title = "Nombre de transactions par agence"
            elif "evolution_montants" in viz_file:
                title = "Évolution des montants"
            elif "evolution_occurrences" in viz_file:
                title = "Évolution des occurrences"
            elif "montant_moyen" in viz_file:
                title = "Montant moyen par occurrence"
            else:
                title = os.path.basename(viz_file)
            
            # Stocker le chemin absolu pour les fichiers dans le conteneur Docker
            relative_path = viz_file
            
            print(f"Ajout de la visualisation: {title}, chemin: {relative_path}")
            
            # Créer la visualisation
            viz = Visualization(
                id=viz_id,
                analysis_id=analysis_id,
                path=relative_path,
                title=title,
                type="bar_chart" if "par_agence" in viz_file else "line_chart"
            )
            
            # Ajouter la visualisation à la base de données
            db.add(viz)
            visualizations_found += 1
    
    # Valider les changements
    db.commit()
    
    print(f"Rapport enregistré avec succès: {analysis_id} (avec {visualizations_found} visualisations)")
    return analysis_id


def main():
    """Point d'entrée principal."""
    args = parse_arguments()
    
    # Obtenir une session de base de données
    db = next(get_db())
    
    # Vérifier que l'utilisateur existe
    user = get_user(db, args.user_id)
    if not user:
        return 1
    
    # Rechercher tous les rapports dans le répertoire de sortie
    report_pattern = os.path.join(args.output_dir, "rapport_*.markdown")
    report_files = glob.glob(report_pattern)
    
    if not report_files:
        print(f"Aucun rapport trouvé dans {args.output_dir}")
        return 1
    
    print(f"Rapports trouvés: {len(report_files)}")
    
    # Enregistrer chaque rapport
    registered_reports = []
    for report_file in report_files:
        analysis_id = register_report(db, report_file, args.user_id)
        if analysis_id:
            registered_reports.append(analysis_id)
    
    print(f"Rapports enregistrés: {len(registered_reports)}/{len(report_files)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
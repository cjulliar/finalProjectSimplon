#!/usr/bin/env python3
"""
Script pour valider que le contenu des fichiers de réponse LLM 
correspond bien au nom du fichier (détection d'erreurs de copier-coller).
"""

import os
import re
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_bank_name_from_filename(filename):
    """
    Extraire le nom de la banque depuis le nom de fichier.
    
    Args:
        filename: Nom du fichier (ex: mail_Banque_A_semaine_2025_24.txt)
    
    Returns:
        Nom de la banque extrait (ex: Banque A)
    """
    # Supprimer l'extension et le préfixe/suffixe
    name_part = filename.replace("mail_", "").replace(".txt", "")
    # Supprimer la partie semaine
    name_part = re.sub(r"_semaine_\d{4}_\d{2}$", "", name_part)
    # Remplacer les underscores par des espaces
    bank_name = name_part.replace("_", " ")
    return bank_name

def extract_bank_names_from_content(content):
    """
    Extraire les noms de banques mentionnés dans le contenu.
    
    Args:
        content: Contenu du fichier
    
    Returns:
        Set des noms de banques trouvés dans le contenu
    """
    bank_names = set()
    
    # Patterns pour trouver les références aux banques dans le contenu
    patterns = [
        r"(?:AGENCE|Agence|banque|Banque)\s+([A-Z]{1,2}(?:\s|$))",  # Banque A, Agence1, etc.
        r"(?:de\s+)?(?:la\s+)?(?:l')?(?:agence|banque)\s+([A-Z]+(?:\s+[A-Z]+)?)",  # la banque AA, l'agence BC
        r"([A-Z]+(?:\s+[A-Z]+)?)\s+(?:présente|montre|affiche|réalise)",  # Banque A présente
        r"performances?\s+de\s+(?:la\s+)?(?:banque|agence)\s+([A-Z]+(?:\s+[A-Z]+)?)",  # performances de la banque A
        r"(?:Banque|Agence)\s+([A-Z]{1,2}(?:\d)?)\b",  # Banque A, Agence1
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            # Nettoyer et normaliser
            bank_name = match.strip()
            if bank_name and len(bank_name) <= 10:  # Éviter les faux positifs trop longs
                bank_names.add(bank_name)
    
    return bank_names

def check_file_consistency(filepath):
    """
    Vérifier la cohérence entre le nom de fichier et son contenu.
    
    Args:
        filepath: Chemin vers le fichier
    
    Returns:
        Dict avec les résultats de la vérification
    """
    filename = os.path.basename(filepath)
    expected_bank = extract_bank_name_from_filename(filename)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            return {
                "filename": filename,
                "expected_bank": expected_bank,
                "status": "VIDE",
                "message": "Le fichier est vide",
                "found_banks": set(),
                "consistent": False
            }
        
        # Vérifier si c'est juste le template non rempli
        if "[Réponse à coller ici]" in content or "[Coller ici la réponse du LLM" in content:
            return {
                "filename": filename,
                "expected_bank": expected_bank,
                "status": "TEMPLATE",
                "message": "Le fichier contient encore le template par défaut",
                "found_banks": set(),
                "consistent": False
            }
        
        found_banks = extract_bank_names_from_content(content)
        
        # Vérifier la cohérence
        expected_variations = {
            expected_bank,
            expected_bank.replace(" ", ""),  # Sans espace
            expected_bank.replace(" ", "_"),  # Avec underscore
        }
        
        consistent = bool(expected_variations.intersection(found_banks))
        
        return {
            "filename": filename,
            "expected_bank": expected_bank,
            "status": "OK" if consistent else "INCOHÉRENT",
            "message": f"Attendu: {expected_bank}, Trouvé: {', '.join(found_banks) if found_banks else 'Aucun'}",
            "found_banks": found_banks,
            "consistent": consistent
        }
        
    except Exception as e:
        return {
            "filename": filename,
            "expected_bank": expected_bank,
            "status": "ERREUR",
            "message": f"Erreur lors de la lecture: {str(e)}",
            "found_banks": set(),
            "consistent": False
        }

def main():
    """Fonction principale de validation."""
    logger.info("=== VALIDATION DES RÉPONSES LLM ===")
    
    responses_dir = Path("prompts_analysis/llm_responses")
    
    if not responses_dir.exists():
        logger.error(f"Le dossier {responses_dir} n'existe pas")
        return
    
    # Récupérer tous les fichiers de réponse
    response_files = list(responses_dir.glob("mail_*.txt"))
    
    if not response_files:
        logger.warning("Aucun fichier de réponse trouvé")
        return
    
    logger.info(f"Validation de {len(response_files)} fichiers de réponse...")
    
    # Statistiques
    stats = {
        "total": 0,
        "ok": 0,
        "incohérent": 0,
        "vide": 0,
        "template": 0,
        "erreur": 0
    }
    
    inconsistent_files = []
    empty_files = []
    template_files = []
    error_files = []
    
    # Vérifier chaque fichier
    for filepath in sorted(response_files):
        result = check_file_consistency(filepath)
        stats["total"] += 1
        
        if result["status"] == "OK":
            stats["ok"] += 1
            logger.info(f"✅ {result['filename']} - Cohérent")
        elif result["status"] == "INCOHÉRENT":
            stats["incohérent"] += 1
            inconsistent_files.append(result)
            logger.warning(f"⚠️  {result['filename']} - {result['message']}")
        elif result["status"] == "VIDE":
            stats["vide"] += 1
            empty_files.append(result)
            logger.warning(f"📄 {result['filename']} - Fichier vide")
        elif result["status"] == "TEMPLATE":
            stats["template"] += 1
            template_files.append(result)
            logger.warning(f"📝 {result['filename']} - Template non rempli")
        elif result["status"] == "ERREUR":
            stats["erreur"] += 1
            error_files.append(result)
            logger.error(f"❌ {result['filename']} - {result['message']}")
    
    # Rapport final
    logger.info("\n=== RAPPORT DE VALIDATION ===")
    logger.info(f"Total fichiers analysés: {stats['total']}")
    logger.info(f"✅ Cohérents: {stats['ok']}")
    logger.info(f"⚠️  Incohérents: {stats['incohérent']}")
    logger.info(f"📄 Vides: {stats['vide']}")
    logger.info(f"📝 Templates non remplis: {stats['template']}")
    logger.info(f"❌ Erreurs: {stats['erreur']}")
    
    # Détails des problèmes
    if inconsistent_files:
        print(f"\n🔍 FICHIERS INCOHÉRENTS ({len(inconsistent_files)}):")
        for result in inconsistent_files:
            print(f"  - {result['filename']}: {result['message']}")
    
    if template_files:
        print(f"\n📝 TEMPLATES NON REMPLIS ({len(template_files)}):")
        for result in template_files:
            print(f"  - {result['filename']}")
    
    if empty_files:
        print(f"\n📄 FICHIERS VIDES ({len(empty_files)}):")
        for result in empty_files:
            print(f"  - {result['filename']}")
    
    if error_files:
        print(f"\n❌ FICHIERS EN ERREUR ({len(error_files)}):")
        for result in error_files:
            print(f"  - {result['filename']}: {result['message']}")
    
    # Recommandations
    print(f"\n💡 RECOMMANDATIONS:")
    if stats["ok"] == stats["total"]:
        print("🎉 Toutes les réponses sont cohérentes ! Vous pouvez procéder à l'enregistrement en BDD.")
    else:
        if inconsistent_files:
            print(f"⚠️  Vérifiez les {len(inconsistent_files)} fichiers incohérents pour détecter d'éventuelles erreurs de copier-coller.")
        if template_files:
            print(f"📝 {len(template_files)} fichiers contiennent encore le template. Complétez-les ou excluez-les de l'import.")
        if empty_files:
            print(f"📄 {len(empty_files)} fichiers sont vides. Générez les réponses manquantes.")
    
    return stats

if __name__ == "__main__":
    main() 
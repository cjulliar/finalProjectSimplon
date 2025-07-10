#!/usr/bin/env python3
"""
Script pour créer les fichiers de réponses LLM vides.
Génère un fichier vide pour chaque prompt existant.
"""

import os
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def create_response_files():
    """Créer les fichiers de réponses vides correspondant aux prompts existants."""
    
    prompts_dir = Path("prompts_analysis/enriched_preprompts")
    responses_dir = Path("prompts_analysis/llm_responses")
    
    # Créer le dossier s'il n'existe pas
    responses_dir.mkdir(parents=True, exist_ok=True)
    
    # Lister tous les prompts existants
    prompt_files = list(prompts_dir.glob("preprompt_*_semaine_2025_28.txt"))
    logger.info(f"Trouvé {len(prompt_files)} prompts pour la semaine 2025_28")
    
    created_count = 0
    
    for prompt_file in prompt_files:
        try:
            # Extraire le nom de l'agence du nom de fichier
            filename = prompt_file.stem  # preprompt_Banque_A_semaine_2025_28
            agence = filename.replace("preprompt_", "").replace("_semaine_2025_28", "")
            
            # Créer le nom du fichier de réponse correspondant
            response_filename = f"mail_{agence}_semaine_2025_28.txt"
            response_filepath = responses_dir / response_filename
            
            # Créer un fichier vide
            with open(response_filepath, 'w', encoding='utf-8') as f:
                f.write("")
            
            created_count += 1
            logger.info(f"  ✅ Fichier créé: {response_filename}")
            
        except Exception as e:
            logger.error(f"  ❌ Erreur lors de la création du fichier pour {prompt_file.name}: {str(e)}")
    
    logger.info(f"\n=== RÉSUMÉ ===")
    logger.info(f"Fichiers de réponses créés: {created_count}")
    logger.info(f"Dossier: {responses_dir}")
    logger.info(f"\n🎯 PROCHAINES ÉTAPES:")
    logger.info(f"1. Copiez les prompts depuis {prompts_dir}/")
    logger.info(f"2. Envoyez-les à ChatGPT")
    logger.info(f"3. Collez les réponses dans les fichiers correspondants de {responses_dir}/")
    logger.info(f"4. Les emails seront ensuite intégrés en BDD et affichés dans le front")

if __name__ == "__main__":
    create_response_files() 
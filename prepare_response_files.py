#!/usr/bin/env python3
"""
Script pour préparer les fichiers de réponses LLM.
Vide tous les fichiers et les prépare pour recevoir les emails générés par ChatGPT.
"""

import os
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def prepare_response_files():
    """Préparer tous les fichiers de réponses LLM."""
    
    responses_dir = Path("prompts_analysis/llm_responses")
    
    if not responses_dir.exists():
        logger.error(f"Le dossier {responses_dir} n'existe pas")
        return
    
    # Compter les fichiers
    response_files = list(responses_dir.glob("mail_*.txt"))
    logger.info(f"Trouvé {len(response_files)} fichiers de réponses à préparer")
    
    prepared_count = 0
    
    for file_path in response_files:
        try:
            # Extraire le nom de l'agence du nom de fichier
            filename = file_path.stem  # mail_Banque_A_semaine_2025_28
            agence = filename.replace("mail_", "").replace("_semaine_2025_28", "")
            
            # Créer le contenu vide avec structure simple
            content = f"""=== EMAIL GÉNÉRÉ PAR LLM ===
AGENCE: {agence}
SEMAINE: 2025_28

[Coller ici l'email généré par ChatGPT pour {agence}]

=== INSTRUCTIONS ===
1. Copiez le contenu du fichier preprompt_{agence}_semaine_2025_28.txt
2. Envoyez-le à ChatGPT ou votre LLM préféré
3. Collez la réponse (email) complète ci-dessous
4. Sauvegardez ce fichier

=== EMAIL À COLLER ICI ===

"""
            
            # Écrire le contenu dans le fichier
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            prepared_count += 1
            logger.info(f"  ✅ Fichier préparé: {file_path.name}")
            
        except Exception as e:
            logger.error(f"  ❌ Erreur lors de la préparation de {file_path.name}: {str(e)}")
    
    logger.info(f"\n=== RÉSUMÉ ===")
    logger.info(f"Fichiers préparés: {prepared_count}/{len(response_files)}")
    logger.info(f"Dossier: {responses_dir}")
    logger.info(f"\n🎯 PROCHAINES ÉTAPES:")
    logger.info(f"1. Copiez les prompts depuis prompts_analysis/enriched_preprompts/")
    logger.info(f"2. Envoyez-les à ChatGPT")
    logger.info(f"3. Collez les réponses dans les fichiers correspondants de {responses_dir}/")
    logger.info(f"4. Les emails seront ensuite intégrés en BDD et affichés dans le front")

if __name__ == "__main__":
    prepare_response_files() 
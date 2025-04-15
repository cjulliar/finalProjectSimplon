# Proof of Concept : Analyse de Données Bancaires avec IA

## Présentation

Ce POC (Proof of Concept) démontre l'intégration d'une solution d'Intelligence Artificielle pour l'analyse automatique de données bancaires et la génération de rapports structurés. Cette approche s'inscrit dans l'objectif global du projet d'automatisation des rapports bancaires, en permettant une analyse détaillée des performances des différentes agences.

## Fonctionnalités implémentées

Le POC implémente les fonctionnalités suivantes :

1. **Génération de données simulées** : Création d'un jeu de données représentatif des données bancaires réelles
2. **Visualisation des données** : Génération automatique de graphiques pour faciliter l'analyse
3. **Analyse IA** : Utilisation d'un modèle de langage pour analyser les données et identifier les tendances
4. **Génération de rapports** : Production automatique d'un rapport structuré destiné aux directeurs

## Architecture technique

Le POC est construit autour des technologies suivantes :

- **Python** comme langage principal
- **Pandas** pour la manipulation des données
- **Matplotlib** pour la visualisation
- **API OpenAI** pour l'analyse IA (avec fallback sur une simulation locale)
- **API HuggingFace** comme alternative d'IA (avec fallback sur une simulation locale)

L'architecture est modulaire et permet facilement de substituer le modèle d'IA utilisé sans modifier le reste du code.

## Utilisation

### Prérequis

```bash
pip install openai pandas matplotlib python-dotenv requests
```

### Exécution

```bash
python src/poc/ia_analyse_poc.py
```

### Configuration

Le POC utilise les variables d'environnement suivantes (via un fichier `.env`) :

- `LLM_API_KEY` : Clé API pour OpenAI
- `HUGGINGFACE_API_KEY` : Clé API alternative pour HuggingFace

Si aucune clé n'est fournie, le POC fonctionnera en mode simulation.

## Résultats et artefacts

L'exécution du POC génère les artefacts suivants dans le dossier `output/` :

1. **Rapport d'analyse** : Fichier Markdown contenant l'analyse détaillée (`rapport_bancaire_[timestamp].md`)
2. **Visualisation des montants** : Graphique montrant l'évolution des montants par agence (`evolution_montants.png`)
3. **Comparaison des agences** : Graphiques comparant les performances des agences (`montant_par_agence.png` et `transactions_par_agence.png`)

## Exemples de prompts

Le POC utilise un système de prompting soigneusement conçu pour obtenir des analyses pertinentes :

```
Analyser les données bancaires suivantes et générer un rapport détaillé pour le directeur.

STATISTIQUES GLOBALES:
- Montant total: {stats['total_montant']}
- Transactions totales: {stats['total_transactions']}
- Montant moyen par transaction: {stats['moyenne_montant']}
- Évolution sur la semaine: {stats['evolution_semaine']}

STATISTIQUES PAR AGENCE:
...

INSTRUCTIONS:
1. Analyser les performances de chaque agence
2. Identifier les tendances et anomalies
3. Proposer des recommandations stratégiques
4. Rédiger un rapport structuré en français, avec introduction, analyse et conclusion
5. Le rapport doit être destiné au directeur du groupe bancaire
```

Cette structure de prompt guide le modèle d'IA pour produire un rapport professionnel et pertinent.

## Intégration dans le projet global

Ce POC s'intègre dans le projet global de la manière suivante :

1. Le module d'analyse IA peut être connecté à la base de données réelle pour accéder aux données bancaires
2. Le système de génération de rapports peut être couplé à un module d'envoi d'emails pour l'automatisation complète
3. Les visualisations peuvent être intégrées directement dans les rapports envoyés

## Limites actuelles et évolutions futures

### Limites

- Fonctionne avec des données simulées (pas encore connecté à la base de données réelle)
- N'inclut pas encore de système RAG (Retrieval Augmented Generation)
- Ne dispose pas de module d'envoi d'emails

### Évolutions prévues

- Implémentation d'un système RAG pour enrichir l'analyse avec des données historiques
- Connexion à la base de données pour utiliser les données réelles
- Ajout d'un module d'envoi automatique d'emails avec le rapport et les visualisations
- Interface utilisateur pour configurer les paramètres d'analyse

## Conclusion

Ce POC démontre avec succès la faisabilité de l'utilisation d'IA pour l'analyse automatique de données bancaires et la génération de rapports structurés. Les résultats obtenus confirment l'intérêt de cette approche pour le projet global d'automatisation des rapports bancaires.

Les prochaines étapes consisteront à développer les fonctionnalités manquantes et à intégrer ce module dans l'architecture globale du projet. 
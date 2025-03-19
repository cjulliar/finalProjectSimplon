# Projet d'Automatisation des Rapports Bancaires

## Contexte et Objectifs
Le projet prend en compte la grille d'evaluation comme objectif, le projet ne peut pas être fini tant que tous les points ne sont pas cochés.
Pendant le développement du projet, si un point qui n'était pas coché est réalisé, alors il faut cocher le point en question en transformant '[ ]' en '[X]'.

L'objectif global du projet est d'automatiser des rapports par mail aux directeurs des différentes banques du groupe. Ces rapports seront hebdomadaires et contiendront une analyse des chiffres faite par Intelligence artificielle.

## Architecture Technique

### Technologies Principales
- Python pour le développement du projet
- LLM : pour la génération du mail avec une analyse des chiffres
- Agent IA : pour l'envoi du mail, générer des graphiques pertinents (ce sont les tools) et l'interaction avec le LLM. Agent. LangChain
- Docker pour la conteneurisation
- FastAPI pour l'API REST
- PostgreSQL pour la base de données
- GitLab CI/CD pour l'intégration et le déploiement continus
- Prometheus et Grafana pour le monitoring

### Sources de Données
1. Données bancaires hebdomadaires :
   - Format actuel : docs/DonneeBanque.xlsx
   - Migration prévue vers une base de données PostgreSQL
   - Contient les données de toutes les agences sur plusieurs semaines
2. Historique des rapports précédents :
   - Stockage en base de données PostgreSQL
   - Utilisé pour l'analyse comparative et l'évolution des chiffres

## Plan de Développement

### Phase 1 : Préparation et Architecture (E1)
1. Documentation initiale :
   - Spécifications techniques détaillées
   - Modélisation Merise de la base de données
   - Documentation RGPD
   - Diagrammes de flux de données

2. Mise en place de l'environnement :
   - Configuration Git et GitLab
   - Création des conteneurs Docker
   - Configuration de l'environnement Python

3. Développement du système de données :
   - Création de la base PostgreSQL
   - Scripts ETL pour l'import des données Excel
   - Mise en place des requêtes SQL d'agrégation
   - Développement de l'API REST pour l'accès aux données

### Phase 2 : Intelligence Artificielle (E2)
1. Veille technologique :
   - Mise en place d'un système de veille sur les LLMs et agents IA
   - Documentation des choix technologiques
   - Benchmark des solutions d'IA

2. Intégration IA :
   - Configuration du LLM choisi
   - Mise en place de l'agent LangChain
   - Développement des prompts et des tools

### Phase 3 : API et Services IA (E3)
1. Développement API :
   - Création de l'API REST avec FastAPI
   - Implémentation de l'authentification
   - Documentation OpenAPI
   - Tests automatisés

2. Intégration des services :
   - Configuration des endpoints IA
   - Mise en place du monitoring
   - Tests d'intégration

### Phase 4 : Application Principale (E4)
1. Développement core :
   - Création du service de génération de rapports
   - Intégration avec l'API IA
   - Système d'envoi de mails
   - Interface utilisateur web (si nécessaire)

2. Tests et Qualité :
   - Tests unitaires
   - Tests d'intégration
   - Tests de performance
   - Validation RGPD

### Phase 5 : Monitoring et Maintenance (E5)
1. Mise en place du monitoring :
   - Configuration Prometheus
   - Tableaux de bord Grafana
   - Alerting

2. Documentation opérationnelle :
   - Procédures de déploiement
   - Guide de maintenance
   - Procédures de debug

## Infrastructure et Déploiement

### Docker
- Conteneur PostgreSQL
- Conteneur Application Python
- Conteneur API
- Conteneur LLM
- Conteneur Monitoring

### CI/CD
1. Pipeline de test :
   - Linting
   - Tests unitaires
   - Tests d'intégration
   - Analyse de sécurité

2. Pipeline de déploiement :
   - Build des images Docker
   - Tests de déploiement
   - Déploiement en production

### Sécurité
- Authentification API
- Chiffrement des données
- Conformité RGPD
- Gestion des secrets

## Livrables Attendus

### Documentation
- Documentation technique complète
- Documentation utilisateur
- Documentation d'API (OpenAPI)
- Registre RGPD
- Rapports de tests

### Code Source
- Scripts Python
- Configuration Docker
- Scripts CI/CD
- Tests automatisés
- Configuration monitoring

### Base de Données
- Schéma SQL
- Scripts de migration
- Procédures de sauvegarde
- Documentation RGPD

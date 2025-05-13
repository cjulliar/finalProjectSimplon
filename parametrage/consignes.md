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
- Github CI/CD pour l'intégration et le déploiement continus
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

## Prochaines étapes de développement

## Interface utilisateur Django

### 1. Configuration initiale

- Créer une application Django pour l'interface utilisateur
- Configurer les modèles nécessaires pour communiquer avec l'API existante
- Mettre en place l'authentification utilisateur compatible avec le système JWT existant

### 2. Structure de l'interface

- Page d'accueil avec tableau de bord des données bancaires
- Page de visualisation des statistiques par agence
- Page de visualisation des statistiques par période
- Page d'analyse IA avec formulaire de demande et affichage des résultats
- Système de gestion des utilisateurs (admin seulement)

### 3. Intégration avec l'API

- Créer un service client pour communiquer avec l'API FastAPI
- Implémenter les appels pour récupérer les données bancaires
- Implémenter les appels pour l'authentification
- Implémenter les appels pour les analyses IA

### 4. Visualisation des données

- Utiliser une bibliothèque de visualisation comme Chart.js
- Créer des graphiques dynamiques basés sur les données de l'API
- Permettre le filtrage des données par agence, date, etc.
- Implémenter des tableaux de bord interactifs

### 5. Gestion des rapports IA

- Créer une interface pour demander une analyse IA
- Afficher les rapports générés par l'IA avec mise en forme appropriée
- Permettre le téléchargement des rapports en PDF
- Historique des analyses précédentes

### 6. Tests et sécurité

- Écrire des tests unitaires pour les vues Django
- Écrire des tests d'intégration pour l'interaction avec l'API
- Mettre en place la protection CSRF
- Configurer des redirections sécurisées

### 7. Déploiement

- Configurer un fichier Dockerfile pour l'application Django
- Mettre à jour le docker-compose.yml pour inclure l'interface utilisateur
- Configurer les variables d'environnement nécessaires
- Intégrer au pipeline CI/CD existant

## Développement de l'IA avec LangChain

### 1. Agent IA avec LangChain

- Développer un agent LangChain capable d'analyser les données bancaires
- Implémenter des chaînes de raisonnement pour l'identification des tendances
- Configurer des outils pour l'accès à la base de données
- Mettre en place un système de mémoire pour les conversations

### 2. Module d'envoi d'emails automatisés

- Créer un service d'envoi d'emails avec SMTP
- Développer des templates d'emails pour les rapports
- Intégrer le service d'emails comme outil pour l'agent LangChain
- Implémenter un système de planification pour l'envoi automatique

### 3. Rapports avancés

- Améliorer la génération de visualisations dynamiques
- Créer des rapports personnalisés par type d'utilisateur
- Implémenter l'exportation des rapports en différents formats (PDF, Excel)
- Ajouter des fonctionnalités de comparaison entre périodes

### 4. Fonctionnalités d'IA avancées

- Implémenter un système RAG (Retrieval Augmented Generation)
- Ajouter des capacités prédictives pour anticiper les tendances
- Développer des alertes automatiques basées sur l'IA
- Créer un système de feedback pour améliorer les analyses

### 5. Tests et optimisation

- Écrire des tests unitaires pour les fonctionnalités d'IA
- Mettre en place des tests d'intégration pour le système complet
- Optimiser les performances de l'agent LangChain
- Gérer les cas d'erreur et la robustesse

### 6. Documentation

- Documenter l'architecture du système d'IA
- Créer un guide d'utilisation pour les utilisateurs finaux
- Documenter les prompts et leur fonctionnement
- Mettre à jour la documentation RGPD avec les aspects IA

## Planification

### Sprint 1 (1-2 semaines)
- Configuration initiale de Django
- Structure de base de l'interface utilisateur
- Développement de l'agent LangChain simple

### Sprint 2 (1-2 semaines)
- Intégration API-Django
- Visualisation des données
- Module d'envoi d'emails

### Sprint 3 (1-2 semaines)
- Interface de gestion des rapports IA
- Amélioration des analyses IA
- Tests et sécurisation

### Sprint 4 (1-2 semaines)
- Finalisation de l'interface utilisateur
- Fonctionnalités d'IA avancées
- Documentation complète
- Déploiement

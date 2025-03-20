# Documentation RGPD du Système d'Automatisation des Rapports Bancaires

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Statut](https://img.shields.io/badge/statut-validé-green)
![Mise à jour](https://img.shields.io/badge/dernière_mise_à_jour-`date du jour`-lightgrey)

## Présentation

Cette documentation regroupe l'ensemble des documents relatifs à la conformité RGPD (Règlement Général sur la Protection des Données) du Système d'Automatisation des Rapports Bancaires. Ces documents sont versionnés dans le système de gestion de versions du code source de l'application pour assurer leur traçabilité et leur mise à jour régulière.

Le système traite exclusivement des données appartenant à la banque elle-même (agrégats financiers par agence) et des informations concernant des utilisateurs internes à l'entreprise. Aucune donnée personnelle relative aux clients de la banque n'est traitée par ce système.

## Documents disponibles

| Document | Description | Version | Dernière mise à jour |
|----------|-------------|---------|----------------------|
| [Documentation RGPD](./RGPD_DOCUMENTATION.md) | Document principal décrivant les mesures RGPD mises en place | 1.0.0 | `date du jour` |
| [Registre des Activités de Traitement](./RGPD_REGISTRE_TRAITEMENT.md) | Registre détaillé des traitements conformément à l'Article 30 du RGPD | 1.0.0 | `date du jour` |
| [Politique de Confidentialité](./RGPD_POLITIQUE_CONFIDENTIALITE.md) | Politique interne de confidentialité et de protection des données | 1.0.0 | `date du jour` |

## Contexte spécifique du projet

Ce projet présente un contexte particulier concernant les données traitées :

1. **Données en environnement fermé** : Les données ne sortent pas du cadre de l'entreprise et ne sont pas publiées sur internet ou en dehors de la société.

2. **Propriété des données** : Les données utilisées sont générées par la banque et lui appartiennent intégralement.

3. **Communication interne uniquement** : Tous les emails envoyés le sont exclusivement sur des adresses professionnelles de la banque, à des directeurs d'agences ou de groupe de la banque.

4. **Absence de données client** : Aucune donnée personnelle des clients de la banque n'est traitée dans ce système.

## Mesures principales mises en place

### 1. Minimisation des données

Le système est conçu selon le principe de minimisation des données :
- Seules les données strictement nécessaires sont collectées et traitées
- Les données bancaires sont agrégées par agence, sans lien avec des personnes physiques
- Les informations utilisateur sont limitées au strict minimum professionnel

### 2. Sécurité des accès

L'accès au système est sécurisé par :
- Authentification forte avec JWT (JSON Web Tokens)
- Mots de passe hashés avec Bcrypt
- Contrôle d'accès basé sur les rôles
- Journalisation des accès et des actions

### 3. Conservation limitée

Les durées de conservation sont définies et justifiées :
- Données bancaires : maximum 5 ans pour l'analyse et la conformité réglementaire
- Données utilisateurs : durée d'emploi + 1 an pour l'archivage

### 4. Gouvernance

Une organisation claire des responsabilités est établie :
- Direction des Systèmes d'Information comme responsable du traitement
- Délégué à la Protection des Données désigné
- Formation et sensibilisation des utilisateurs

## Processus de mise à jour

Cette documentation fait l'objet d'une revue régulière :
- Revue annuelle complète
- Mise à jour en cas de modification substantielle du système
- Versionnement systématique des documents

## Historique des versions

| Version | Date | Auteur | Description des modifications |
|---------|------|--------|-------------------------------|
| 1.0.0 | `date du jour` | [Votre nom] | Version initiale de la documentation RGPD |

---

© 2025 Banque Populaire du Nord - Document interne 
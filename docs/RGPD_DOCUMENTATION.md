# Documentation RGPD - Système d'Automatisation des Rapports Bancaires

**Version:** 1.0.0  
**Date de mise à jour:** 20/03/2025
**Statut:** Validé pour environnement interne bancaire uniquement

## Sommaire

1. [Introduction](#introduction)
2. [Base légale du traitement](#base-légale-du-traitement)
3. [Données traitées](#données-traitées)
4. [Mesures de sécurité](#mesures-de-sécurité)
5. [Droits des personnes concernées](#droits-des-personnes-concernées)
6. [Registre des activités de traitement](#registre-des-activités-de-traitement)
7. [Rétention des données](#rétention-des-données)
8. [Transfert des données](#transfert-des-données)
9. [Analyse d'impact relative à la protection des données (AIPD)](#analyse-dimpact-relative-à-la-protection-des-données-aipd)
10. [Responsabilités et contacts](#responsabilités-et-contacts)
11. [Historique des modifications](#historique-des-modifications)

## Introduction

Ce document décrit les mesures prises dans le cadre du Système d'Automatisation des Rapports Bancaires pour assurer la conformité avec le Règlement Général sur la Protection des Données (RGPD).

Le système traite exclusivement des données appartenant à la banque elle-même (agrégats financiers par agence) et des informations concernant des utilisateurs internes à l'entreprise. Aucune donnée personnelle relative aux clients de la banque n'est traitée par ce système.

## Base légale du traitement

Le traitement des données dans cette application repose sur les bases légales suivantes:

- **Intérêt légitime** (Article 6.1.f du RGPD): La banque a un intérêt légitime à analyser ses propres données agrégées d'activité pour des fins de reporting interne et de pilotage d'activité.
- **Exécution d'un contrat** (Article 6.1.b du RGPD): Pour les utilisateurs du système, le traitement de leurs données est nécessaire à l'exécution de leur contrat de travail.

## Données traitées

### Données bancaires agrégées

```
class BankData(Base):
    __tablename__ = "bank_data"

    id = Column(Integer, primary_key=True, index=True)
    agence = Column(String, index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    montant = Column(Float, nullable=False)
    nombre_transactions = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
```

Ces données sont:
- Des agrégats ne contenant aucune donnée personnelle identifiable (DPI)
- Appartenant à l'entreprise et générées par ses systèmes internes
- Non rattachées à des personnes physiques identifiables

### Données utilisateurs internes

```
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
```

Ces données concernent uniquement les collaborateurs internes autorisés à utiliser l'application:
- Identifiant professionnel (username)
- Email professionnel (email)
- Mot de passe hashé (non-réversible)
- Statut du compte

## Mesures de sécurité

Les mesures suivantes ont été mises en place pour garantir la sécurité des données:

### Sécurité technique

1. **Authentification:** 
   - Système d'authentification par jeton JWT
   - Mots de passe hashés avec Bcrypt
   - Déconnexion automatique après période d'inactivité

2. **Autorisations:**
   - Accès limité selon les rôles des utilisateurs
   - Principe du moindre privilège appliqué

3. **Sécurité des données:**
   - Chiffrement des mots de passe
   - Base de données isolée du réseau externe
   - Absence de stockage de données sensibles

4. **Journalisation:**
   - Journalisation des accès et actions importantes
   - Suivi des modifications des données avec horodatage

5. **Sécurité du code:**
   - Tests automatisés de sécurité
   - CI/CD avec vérification de sécurité
   - Maintenance régulière et mises à jour

### Sécurité organisationnelle

1. **Accès limité:**
   - Uniquement par les employés autorisés
   - Utilisation limitée au réseau interne de la banque

2. **Formation:**
   - Formation des utilisateurs aux bonnes pratiques
   - Sensibilisation à la sécurité et à la confidentialité

3. **Procédures:**
   - Procédure de revue d'accès périodique
   - Processus de gestion des incidents

## Droits des personnes concernées

Pour les utilisateurs du système (employés de la banque), les droits suivants sont assurés:

- **Droit d'accès:** Les utilisateurs peuvent consulter leurs propres données via l'API `/users/me`.
- **Droit de rectification:** Les informations incorrectes peuvent être corrigées sur demande à l'administrateur.
- **Droit à l'effacement:** Les comptes non utilisés peuvent être désactivés plutôt que supprimés pour maintenir l'intégrité des journaux.
- **Droit à la limitation du traitement:** L'accès peut être temporairement désactivé sur demande.

Ces droits peuvent être exercés par une demande auprès du responsable de la protection des données de la banque.

## Registre des activités de traitement

| Activité de traitement | Finalité | Catégorie de données | Base légale | Durée de conservation | Destinataires | Mesures de sécurité |
|------------------------|----------|----------------------|------------|----------------------|--------------|---------------------|
| Gestion des utilisateurs | Administration et sécurité de l'application | Identifiants professionnels | Exécution du contrat | Durée d'emploi + 1 an | Administrateurs système | Authentification, hachage, journalisation |
| Importation des données bancaires | Alimentation de la base de données | Données agrégées par agence | Intérêt légitime | 5 ans | Utilisateurs autorisés | Contrôle d'accès, journalisation |
| Génération de rapports | Analyse de performance | Données agrégées | Intérêt légitime | Durée de vie du rapport | Directeurs d'agence, managers | Contrôle d'accès, envoi sécurisé |

## Rétention des données

### Données bancaires
- **Durée de conservation:** 5 ans maximum
- **Justification:** Nécessaire pour l'analyse des tendances et la conformité réglementaire bancaire
- **Mécanisme de purge:** Processus automatisé de purge des données datant de plus de 5 ans (à implémenter)

### Données utilisateurs
- **Durée de conservation:** Durée d'emploi + 1 an
- **Justification:** Archivage à des fins d'audit et de sécurité
- **Mécanisme de désactivation:** Désactivation des comptes lorsqu'un employé quitte l'entreprise

## Transfert des données

- **Aucun transfert hors de l'organisation:** Les données restent exclusivement au sein de l'infrastructure de la banque.
- **Communication interne:** Les rapports générés sont envoyés uniquement aux emails professionnels internes à la banque.
- **Absence de sous-traitants:** Aucun sous-traitant n'a accès aux données du système.

## Analyse d'impact relative à la protection des données (AIPD)

Une analyse d'impact complète n'est pas requise pour ce traitement car:
- Les données traitées sont principalement des agrégats non-personnels
- Les données utilisateurs sont limitées aux employés dans un contexte professionnel
- Le système opère exclusivement en environnement fermé et contrôlé
- Aucune donnée sensible n'est traitée

## Responsabilités et contacts

- **Responsable du traitement:** Direction des Systèmes d'Information de la Banque
- **Délégué à la protection des données (DPO):** [Nom et coordonnées du DPO de la banque]
- **Administrateur système:** [Nom et coordonnées de l'administrateur système]

Pour toute question ou exercice de droits relatifs aux données personnelles, veuillez contacter le DPO à l'adresse [email].

## Historique des modifications

| Version | Date | Auteur | Description des modifications |
|---------|------|--------|-------------------------------|
| 1.0.0 | `date du jour` | [Votre nom] | Version initiale du document |

---

© 2025 Banque Populaire du Nord - Document interne confidentiel 
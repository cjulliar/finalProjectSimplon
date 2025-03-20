# Politique de Confidentialité et de Protection des Données

**Version:** 1.0.0  
**Date de mise à jour:** 20/03/2025 
**Statut:** Document interne validé

## Préambule

Banque Populaire du Nord s'engage à protéger la confidentialité et la sécurité des données traitées par le Système d'Automatisation des Rapports Bancaires. Cette politique de confidentialité détaille comment les données sont collectées, traitées, stockées et protégées conformément au Règlement Général sur la Protection des Données (RGPD) et aux autres réglementations applicables.

Ce document s'adresse aux utilisateurs internes du système et complète les politiques générales de sécurité des systèmes d'information de l'établissement.

## 1. Définitions

- **Données personnelles** : Toute information se rapportant à une personne physique identifiée ou identifiable.
- **Traitement** : Toute opération effectuée sur des données personnelles (collecte, enregistrement, organisation, structuration, conservation, etc.).
- **Responsable de traitement** : La Direction des Systèmes d'Information de Banque Populaire du Nord.
- **Personne concernée** : Personne physique dont les données personnelles font l'objet d'un traitement.
- **DPO** : Délégué à la Protection des Données, chargé de veiller à la conformité au RGPD.

## 2. Données traitées

### 2.1 Données bancaires agrégées

Le système traite des données agrégées relatives à l'activité des agences bancaires, incluant :
- Identifiants d'agence
- Dates des transactions
- Montants totaux agrégés
- Nombre de transactions

Ces données sont agrégées et ne contiennent pas d'informations personnelles identifiables concernant les clients de la banque.

### 2.2 Données des utilisateurs internes

Le système traite les données suivantes concernant ses utilisateurs (employés de la banque) :
- Nom d'utilisateur professionnel
- Adresse email professionnelle
- Mot de passe (stocké sous forme hashée)
- Informations de connexion et d'activité

## 3. Finalités du traitement

Les données sont traitées pour les finalités suivantes :

1. **Administration du système** : Gestion des comptes utilisateurs, authentification et autorisation des accès.
2. **Reporting bancaire** : Production de rapports d'activité agrégés par agence et par période.
3. **Analyse des performances** : Évaluation des performances commerciales des agences.
4. **Sécurité informatique** : Détection et prévention des accès non autorisés et des incidents de sécurité.

## 4. Base légale du traitement

Les traitements effectués reposent sur les bases légales suivantes :

- **Intérêt légitime** (Article 6.1.f du RGPD) : Pour l'analyse des données agrégées d'activité bancaire à des fins de pilotage interne.
- **Exécution d'un contrat** (Article 6.1.b du RGPD) : Pour le traitement des données des utilisateurs dans le cadre de leurs fonctions professionnelles.

## 5. Durée de conservation

### 5.1 Données bancaires agrégées
- Conservation pendant une durée maximale de 5 ans, en conformité avec les obligations légales et les besoins d'analyse.
- À l'issue de cette période, les données sont archivées selon la politique d'archivage de la banque.

### 5.2 Données des utilisateurs
- Conservation pendant la durée d'emploi de l'utilisateur.
- À la fin du contrat de travail, le compte est désactivé et les données conservées pour une durée d'un an à des fins d'audit, puis supprimées ou anonymisées.

## 6. Mesures de protection des données

### 6.1 Sécurité technique
- Authentification forte des utilisateurs (JWT, hachage des mots de passe avec Bcrypt)
- Chiffrement des communications (TLS)
- Isolation de la base de données
- Journalisation des accès et des actions
- Mises à jour régulières et correctifs de sécurité

### 6.2 Contrôles d'accès
- Attribution des droits selon le principe du moindre privilège
- Séparation des rôles et responsabilités
- Revue périodique des droits d'accès
- Désactivation immédiate en cas de départ ou de changement de fonction

### 6.3 Sensibilisation et formation
- Formation initiale obligatoire pour tous les utilisateurs
- Rappels périodiques des bonnes pratiques de sécurité
- Sensibilisation aux risques de sécurité informatique

## 7. Droits des utilisateurs

Les utilisateurs du système disposent des droits suivants concernant leurs données personnelles :

- **Droit d'accès** : Consultation des données les concernant via l'API ou sur demande au DPO.
- **Droit de rectification** : Correction des informations inexactes.
- **Droit à la limitation** : Possibilité de demander la limitation du traitement.
- **Droit d'opposition** : Dans les limites des obligations professionnelles.

Pour exercer ces droits, les utilisateurs peuvent contacter le Délégué à la Protection des Données à l'adresse [email du DPO].

## 8. Communication des données

### 8.1 Destinataires internes
Les données traitées sont accessibles uniquement aux personnes autorisées :
- Administrateurs du système
- Utilisateurs ayant reçu les autorisations appropriées
- Direction des agences concernées

### 8.2 Absence de transfert externe
- Aucune donnée n'est transférée à des tiers extérieurs à la banque.
- Aucun transfert n'est effectué en dehors de l'Union Européenne.

## 9. Incidents et violations de données

En cas d'incident de sécurité affectant des données personnelles :

1. L'incident est immédiatement signalé au DPO et à l'équipe de sécurité informatique.
2. Une analyse d'impact est réalisée pour évaluer les risques potentiels.
3. Les mesures correctives sont mises en œuvre sans délai.
4. Si nécessaire, une notification est adressée à la CNIL dans les 72 heures.

## 10. Gouvernance

### 10.1 Responsabilités
- **Direction des Systèmes d'Information** : Responsable du traitement
- **Délégué à la Protection des Données** : Supervise la conformité au RGPD
- **Administrateurs système** : Mettent en œuvre les mesures techniques
- **Utilisateurs** : Respectent les consignes de sécurité et de confidentialité

### 10.2 Documentation et contrôles
- Tenue du registre des activités de traitement
- Audits périodiques de sécurité
- Revue annuelle de cette politique
- Rapports d'activité au Comité de Sécurité

## 11. Mise à jour de la politique

Cette politique fait l'objet d'une revue annuelle et est mise à jour en fonction :
- Des évolutions réglementaires
- Des changements dans les traitements effectués
- Des recommandations issues des audits
- Des incidents de sécurité survenus

## 12. Historique des versions

| Version | Date | Auteur | Description des modifications |
|---------|------|--------|-------------------------------|
| 1.0.0 | `date du jour` | [Votre nom] | Version initiale |

---

**Validation :**

| Fonction | Nom | Date | Signature |
|----------|-----|------|-----------|
| Directeur des Systèmes d'Information | | | |
| Délégué à la Protection des Données | | | |
| Responsable de la Sécurité des SI | | | |

© 2025 Banque Populaire du Nord - Document interne confidentiel 
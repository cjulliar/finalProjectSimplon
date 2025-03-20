# Registre des Activités de Traitement - Système d'Automatisation des Rapports Bancaires

**Version:** 1.0.0  
**Date de mise à jour:** 20/03/2025
**Statut:** Document interne à usage limité

## Préambule

Conformément à l'article 30 du Règlement Général sur la Protection des Données (RGPD), ce document constitue le registre des activités de traitement réalisées par le Système d'Automatisation des Rapports Bancaires. Ce registre est maintenu et versionnée dans le système de gestion de versions du code source de l'application.

## Identification du responsable de traitement

**Organisme:** Banque Populaire du Nord
**Adresse:** [Adresse du siège social]  
**Représentant légal:** [Nom du représentant légal]  
**SIRET:** [Numéro SIRET]

## Délégué à la Protection des Données (DPO)

**Nom et prénom:** [Nom et prénom du DPO]  
**Adresse professionnelle:** [Adresse professionnelle du DPO]  
**Email professionnel:** [Email du DPO]  
**Téléphone professionnel:** [Téléphone du DPO]

## Liste des traitements

### 1. Gestion des utilisateurs du système

| Caractéristique | Description |
|-----------------|-------------|
| **Finalité principale** | Authentification et autorisation des utilisateurs internes |
| **Base légale** | Exécution du contrat de travail (Art. 6.1.b du RGPD) |
| **Catégories de personnes concernées** | Employés de la banque ayant accès au système |
| **Catégories de données traitées** | Identifiants professionnels (nom d'utilisateur, email), mots de passe hashés, journaux d'activité |
| **Données sensibles** | Non |
| **Source des données** | Directe (création de compte par l'administrateur) |
| **Durée de conservation** | Durée d'emploi + 1 an pour archivage |
| **Destinataires internes** | Administrateurs système, équipe de sécurité informatique |
| **Destinataires externes** | Aucun |
| **Transfert hors UE** | Non |
| **Mesures de sécurité** | Authentification multi-facteurs, hachage des mots de passe, chiffrement des communications, journalisation, contrôles d'accès |
| **Documentation associée** | Politique de sécurité des utilisateurs (réf. SEC-USR-001) |

### 2. Importation et stockage des données bancaires

| Caractéristique | Description |
|-----------------|-------------|
| **Finalité principale** | Centralisation des données d'activité bancaire pour reporting |
| **Base légale** | Intérêt légitime (Art. 6.1.f du RGPD) |
| **Catégories de personnes concernées** | Aucune (données agrégées par agence) |
| **Catégories de données traitées** | Identifiant d'agence, date, montant total des transactions, nombre de transactions |
| **Données sensibles** | Non |
| **Source des données** | Systèmes internes de la banque (fichiers Excel) |
| **Durée de conservation** | 5 ans maximum |
| **Destinataires internes** | Utilisateurs autorisés du système, directeurs d'agence, managers |
| **Destinataires externes** | Aucun |
| **Transfert hors UE** | Non |
| **Mesures de sécurité** | Contrôles d'accès, validation des données, journalisation des imports, base de données sécurisée |
| **Documentation associée** | Procédure d'import de données (réf. PROC-IMP-001) |

### 3. Génération et distribution de rapports

| Caractéristique | Description |
|-----------------|-------------|
| **Finalité principale** | Analyse et pilotage de l'activité bancaire |
| **Base légale** | Intérêt légitime (Art. 6.1.f du RGPD) |
| **Catégories de personnes concernées** | Aucune (données agrégées par agence) |
| **Catégories de données traitées** | Statistiques agrégées, métriques de performance par agence |
| **Données sensibles** | Non |
| **Source des données** | Base de données interne |
| **Durée de conservation** | Durée de vie du rapport (variable selon type) |
| **Destinataires internes** | Directeurs d'agence, managers, personnel autorisé |
| **Destinataires externes** | Aucun |
| **Transfert hors UE** | Non |
| **Mesures de sécurité** | Authentification des destinataires, envoi sécurisé, contrôles d'accès aux rapports |
| **Documentation associée** | Politique de distribution des rapports (réf. POL-REP-001) |

## Sous-traitants impliqués

Aucun sous-traitant n'a accès aux données traitées par le système. L'ensemble des traitements est réalisé en interne, sur l'infrastructure de la banque.

## Mesures de sécurité organisationnelles

1. **Politique de confidentialité interne:**
   - Document référence: POL-CONF-001
   - Portée: Tous les employés ayant accès au système
   - Dernière mise à jour: [date]

2. **Formation et sensibilisation:**
   - Fréquence: Annuelle
   - Contenu: Bonnes pratiques RGPD, sécurité informatique, confidentialité
   - Public: Utilisateurs et administrateurs du système

3. **Gestion des accès:**
   - Revue périodique des droits (trimestrielle)
   - Processus de révocation immédiate en cas de départ
   - Traçabilité des attributions de droits

4. **Gestion des incidents:**
   - Procédure de notification interne: PROC-INC-001
   - Délai de notification au DPO: 24h maximum
   - Registre des incidents

## Mesures de sécurité techniques

1. **Authentification:**
   - Méthode: JWT (JSON Web Tokens)
   - Durée de validité des sessions: 8 heures
   - Stockage des mots de passe: Hachage avec Bcrypt et salt

2. **Sécurité du stockage:**
   - Chiffrement de la base de données: AES-256
   - Sauvegardes: Quotidiennes, chiffrées
   - Isolation réseau: Base de données accessible uniquement depuis l'application

3. **Sécurité des communications:**
   - Protocole: HTTPS avec TLS 1.3
   - Certificats: Renouvellement automatique tous les 90 jours
   - Validation des en-têtes HTTP de sécurité

4. **Journalisation:**
   - Éléments journalisés: Authentification, actions d'administration, imports de données
   - Durée de conservation des journaux: 1 an
   - Protection contre la modification: Hachage des journaux

## Analyse des risques

| Risque | Probabilité | Impact | Mesures d'atténuation |
|--------|-------------|--------|------------------------|
| Accès non autorisé | Faible | Moyen | Authentification forte, contrôle d'accès, surveillance |
| Perte de données | Très faible | Élevé | Sauvegardes régulières, validation d'intégrité |
| Fuite de données | Faible | Moyen | Isolation réseau, chiffrement, contrôles d'accès |
| Indisponibilité du service | Faible | Moyen | Monitoring, plan de continuité, redondance |

## Révisions du registre

| Version | Date | Auteur | Description des modifications |
|---------|------|--------|-------------------------------|
| 1.0.0 | `date du jour` | [Votre nom] | Version initiale du registre |

---

Ce registre est maintenu à jour par le Délégué à la Protection des Données.  
Contact: [email du DPO]  
© 2025 Banque Populaire du Nord  - Document interne confidentiel 
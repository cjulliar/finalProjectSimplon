# 📊 DÉFINITIONS DES COLONNES - DONNÉES BANCAIRES ENRICHIES

## 📋 Structure des données analysée

Ce fichier contient les définitions et interprétations de chaque colonne 
du dataset bancaire enrichi, basé sur `DonneeBanque.xlsx`, feuille "Donnee DataSet".

## 🔍 Interprétations détaillées des colonnes

### 📅 Dimensions Temporelles
- **semaine_id**: Identifiant de semaine au format YYYYWW (ex: 202507 = semaine 7 de 2025)
- **annee**: Année extraite de semaine_id
- **numero_semaine**: Numéro de semaine dans l'année
- **date_semaine**: Date calculée du lundi de la semaine (format ISO)

### 🏦 Identifiants
- **groupe**: Groupe bancaire (Groupe A, Groupe B, etc.)
- **agence**: Nom de l'agence/banque (Banque A, Banque B, etc.)

### 👤 Indicateurs Particuliers (Clients Particuliers)
- **occ_part**: Nombre d'occupations/clients particuliers
- **conso_dec**: Montant de consommation déclarée (€)
- **bilan_net**: Bilan net particuliers (€)
- **vers_ep_fi**: Versements épargne financière (€)
- **vb_iard_part**: Volume business IARD particuliers
- **vb_prev_part**: Volume business prévoyance particuliers
- **vb_ass_peri_pea_hiss**: Volume business assurance PERI/PEA/assurance vie
- **tx_occ_part_soc**: Taux d'occupation particuliers société (%)
- **moy_part**: Moyenne particuliers
- **somme_part**: Somme totale particuliers
- **rang_part**: Rang/classement particuliers

### 🏢 Indicateurs Professionnels (Clients Entreprises)
- **occ_pro**: Nombre d'occupations/clients professionnels
- **occ_pro_cible**: Objectif d'occupation professionnelle
- **eqpt_dec**: Équipement déclaré professionnels (€)
- **vb_iard_pro**: Volume business IARD professionnels
- **vb_prev_pro**: Volume business prévoyance professionnels
- **vb_contr_comm**: Volume business contrats commerciaux
- **coll_pro_net**: Collecte professionnelle nette (€)
- **tx_occ_pro_soc**: Taux d'occupation professionnels société (%)
- **moy_pro**: Moyenne professionnels
- **somme_pro**: Somme totale professionnels
- **rang_pro**: Rang/classement professionnels

### 📊 Indicateurs Globaux
- **moy_global**: Moyenne globale de l'agence
- **somme_rang**: Somme des rangs (particuliers + professionnels)
- **rang_global**: Rang global de l'agence

### 🔧 Métadonnées
- **id**: Clé primaire auto-incrémentée
- **created_at**: Horodatage de création
- **updated_at**: Horodatage de dernière mise à jour

## 📊 KPIs Calculables

### 💰 Indicateurs Financiers Principaux
```sql
-- Chiffre d'affaires total estimé
(conso_dec + bilan_net + vers_ep_fi + eqpt_dec + coll_pro_net) AS ca_total

-- Performance particuliers
(conso_dec + bilan_net + vers_ep_fi) AS ca_particuliers

-- Performance professionnels  
(eqpt_dec + coll_pro_net) AS ca_professionnels
```

### 📈 Indicateurs de Performance
```sql
-- Score de performance global
(100 - rang_global) AS score_performance

-- Équilibre part/pro
(somme_part / (somme_part + somme_pro)) * 100 AS pourcentage_particuliers
```

### 🎯 Indicateurs d'Activité
```sql
-- Volume total d'activité
(occ_part + occ_pro) AS clients_totaux

-- Efficacité professionnelle
(occ_pro / occ_pro_cible) * 100 AS taux_atteinte_objectif
```

## 🗄️ Structure de la base de données

```sql
CREATE TABLE bank_data_enriched (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Métadonnées temporelles
    semaine_id INTEGER NOT NULL,
    annee INTEGER,
    numero_semaine INTEGER,
    date_semaine DATE,
    
    -- Identifiants
    groupe VARCHAR(50),
    agence VARCHAR(100) NOT NULL,
    
    -- Indicateurs Particuliers (PART)
    occ_part INTEGER DEFAULT 0,
    conso_dec DECIMAL(15,2) DEFAULT 0,
    bilan_net DECIMAL(15,2) DEFAULT 0,
    vers_ep_fi DECIMAL(15,2) DEFAULT 0,
    vb_iard_part INTEGER DEFAULT 0,
    vb_prev_part INTEGER DEFAULT 0,
    vb_ass_peri_pea_hiss INTEGER DEFAULT 0,
    tx_occ_part_soc DECIMAL(10,4) DEFAULT 0,
    moy_part DECIMAL(10,4) DEFAULT 0,
    somme_part INTEGER DEFAULT 0,
    rang_part INTEGER DEFAULT 0,
    
    -- Indicateurs Professionnels (PRO)
    occ_pro INTEGER DEFAULT 0,
    occ_pro_cible INTEGER DEFAULT 0,
    eqpt_dec DECIMAL(15,2) DEFAULT 0,
    vb_iard_pro INTEGER DEFAULT 0,
    vb_prev_pro INTEGER DEFAULT 0,
    vb_contr_comm INTEGER DEFAULT 0,
    coll_pro_net DECIMAL(15,2) DEFAULT 0,
    tx_occ_pro_soc DECIMAL(10,4) DEFAULT 0,
    moy_pro DECIMAL(10,4) DEFAULT 0,
    somme_pro DECIMAL(15,2) DEFAULT 0,
    rang_pro INTEGER DEFAULT 0,
    
    -- Indicateurs Globaux
    moy_global DECIMAL(10,4) DEFAULT 0,
    somme_rang DECIMAL(15,2) DEFAULT 0,
    rang_global INTEGER DEFAULT 0,
    
    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes
    UNIQUE(agence, semaine_id)
);
```

### 🔍 Index pour les performances
```sql
CREATE INDEX idx_agence ON bank_data_enriched(agence);
CREATE INDEX idx_semaine ON bank_data_enriched(semaine_id);
CREATE INDEX idx_agence_semaine ON bank_data_enriched(agence, semaine_id);
CREATE INDEX idx_groupe ON bank_data_enriched(groupe);
CREATE INDEX idx_date ON bank_data_enriched(date_semaine);
```

## 📈 Cas d'usage pour l'IA

### 🎯 Prompts recommandés pour l'analyse
1. **Performance globale**: Utiliser `rang_global`, `moy_global`, `somme_rang`
2. **Analyse sectorielle**: Comparer `ca_particuliers` vs `ca_professionnels`
3. **Tendances temporelles**: Analyser l'évolution par `semaine_id`
4. **Benchmarking**: Comparer les rangs entre agences du même groupe
5. **Détection d'anomalies**: Identifier les variations importantes entre semaines

---
*Généré automatiquement le 2025-06-12 14:16:50*
# Documentation C4 : Base de données et importation de données

## Présentation

Ce document détaille l'implémentation du critère C4 : "Créer une base de données dans le respect du RGPD".

L'application permet d'importer des données bancaires depuis un fichier Excel (`docs/DonneeBanque.xlsx`) vers une base de données SQLite, qui sera utilisée pour générer des rapports bancaires hebdomadaires.

## Structure du modèle de données

Le modèle de données a été conçu pour stocker les informations bancaires essentielles :

```python
class BankData(Base):
    """Modèle pour les données bancaires hebdomadaires"""
    __tablename__ = "bank_data"

    id = Column(Integer, primary_key=True, index=True)
    agence = Column(String, index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    montant = Column(Float, nullable=False)
    nombre_transactions = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
```

Ce modèle permet de stocker :
- L'identifiant de l'agence bancaire
- La date des transactions
- Le montant total des transactions
- Le nombre de transactions
- La date d'insertion des données (pour le suivi)

## Procédure d'importation

### Étapes du processus ETL (Extract, Transform, Load)

1. **Extraction** : Lecture du fichier Excel avec pandas
2. **Transformation** : 
   - Validation des colonnes requises
   - Conversion des types de données
   - Nettoyage des valeurs manquantes ou incorrectes
3. **Chargement** : Insertion des données dans la base SQLite par lots pour optimiser les performances

### Utilisation du script d'importation

Pour importer les données du fichier Excel dans la base de données, utilisez la commande suivante :

```bash
python -m src.main --import-excel
```

Pour spécifier un fichier Excel différent :

```bash
python -m src.main --import-excel --file chemin/vers/fichier.xlsx
```

### Script d'importation autonome

Un script d'importation autonome est également disponible :

```bash
python src/scripts/import_data.py
```

## Visualisation des données

Pour visualiser les données importées dans la base de données :

```bash
python src/scripts/view_db.py
```

Options disponibles :
- `--limit` ou `-l` : Limite le nombre de lignes affichées (défaut : 10)
- `--agence` ou `-a` : Filtre par agence
- `--stats` ou `-s` : Affiche des statistiques sur les données

## Tests

Des tests automatisés ont été créés pour valider le bon fonctionnement de la base de données et du processus d'importation :

```bash
python tests/run_c4_tests.py
```

Ces tests vérifient :
- La connexion à la base de données
- Le modèle de données
- La lecture du fichier Excel
- Le nettoyage et la transformation des données
- L'insertion des données dans la base
- Les performances d'insertion par lots
- Les requêtes et le filtrage des données

## Conformité RGPD

Pour assurer la conformité RGPD, les mesures suivantes ont été prises :

1. **Minimisation des données** : Seules les données nécessaires sont stockées.
2. **Sécurité des données** : La base de données est sécurisée et accessible uniquement via l'application.
3. **Traçabilité** : La date d'insertion est enregistrée pour chaque entrée.
4. **Rétention limitée** : Un mécanisme de purge des données anciennes sera implémenté dans une version future.

## Dépendances

Ce module dépend des bibliothèques suivantes :
- SQLAlchemy : ORM pour la gestion de la base de données
- Pandas : Manipulation des données et lecture des fichiers Excel
- Openpyxl : Support du format Excel pour Pandas

## Structure des fichiers

```
src/
├── db/
│   ├── __init__.py
│   ├── database.py    # Configuration de la base de données
│   └── models.py      # Modèles de données (BankData)
├── etl/
│   ├── __init__.py
│   └── excel_import.py # Module d'importation Excel
└── scripts/
    ├── __init__.py
    ├── import_data.py  # Script d'importation autonome
    └── view_db.py      # Script de visualisation
tests/
├── test_database.py   # Tests de la base de données
├── test_excel_import.py # Tests de l'importation Excel
└── run_c4_tests.py    # Script d'exécution des tests C4
``` 
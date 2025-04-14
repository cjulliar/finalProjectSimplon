# Système d'Automatisation des Rapports Bancaires

Ce projet vise à automatiser la génération et l'envoi de rapports hebdomadaires aux directeurs des différentes banques du groupe, en utilisant l'intelligence artificielle pour analyser les données et générer des rapports pertinents.

## Prérequis

- Docker et Docker Compose
- Python 3.10
- Git

## Installation

1. Cloner le repository :
```bash
git clone <votre-repo-url>
cd finalProjectSimplon
```

2. Copier le fichier .env.example en .env et configurer les variables :
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

3. Créer et activer l'environnement virtuel :
```bash
python3.10 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

4. Installer les dépendances :
```bash
python3.10 -m pip install -r requirements.txt
```

## Fonctionnalités principales

### 1. Importation et traitement des données

L'application permet d'importer des données bancaires depuis un fichier Excel vers une base de données SQLite :

```bash
# Importer les données du fichier Excel par défaut (docs/DonneeBanque.xlsx)
python3.10 -m src.main --import-excel

# Spécifier un fichier Excel différent
python3.10 -m src.main --import-excel --file chemin/vers/fichier.xlsx

# Afficher les données importées
python3.10 src/scripts/view_db.py

# Afficher des statistiques
python3.10 src/scripts/view_db.py --stats
```

Pour plus de détails sur l'importation de données, consultez la [documentation C4](docs/C4_README.md).

### 2. API REST pour accéder aux données

L'application expose une API REST sécurisée pour accéder aux données bancaires :

```bash
# Créer un utilisateur administrateur
python3.10 src/scripts/create_admin.py --username admin --password votremotdepasse --email admin@example.com

# Lancer l'API
python3.10 src/scripts/run_api.py --reload
```

L'API offre les fonctionnalités suivantes :
- Authentification sécurisée avec JWT (JSON Web Tokens)
- Accès aux données bancaires avec filtrage et pagination
- Statistiques par agence et par date
- Documentation interactive avec Swagger UI et ReDoc

Pour accéder à la documentation de l'API :
- Swagger UI : http://localhost:8000/docs
- ReDoc : http://localhost:8000/redoc

Pour plus de détails sur l'API, consultez la [documentation API](docs/API_README.md).

### 3. Analyse des données avec IA (à venir)

L'application utilisera un modèle d'IA pour analyser les données et générer des rapports pertinents.

### 4. Génération et envoi de rapports (à venir)

L'application générera des rapports hebdomadaires et les enverra par email aux directeurs des différentes banques.

## Structure du Projet

```
.
├── docker/                 # Configurations Docker
├── docs/                   # Documentation et données
│   ├── API_README.md       # Documentation de l'API
│   ├── C4_README.md        # Documentation sur l'importation de données
│   └── DonneeBanque.xlsx   # Fichier de données bancaires
├── src/                    # Code source
│   ├── api/                # API FastAPI
│   ├── db/                 # Modèles et connexions à la base de données
│   ├── etl/                # Scripts d'extraction, transformation et chargement
│   ├── scripts/            # Scripts utilitaires
│   └── utils/              # Utilitaires divers
├── tests/                  # Tests automatisés
├── .env                    # Variables d'environnement
├── docker-compose.yml      # Configuration Docker Compose
└── requirements.txt        # Dépendances Python
```

## Développement

### Tests
Pour exécuter les tests :
```bash
python3.10 -m pytest tests/
```

Pour exécuter les tests spécifiques à l'importation de données :
```bash
python3.10 tests/run_c4_tests.py
```

Pour exécuter les tests de l'API :
```bash
python3.10 -m pytest tests/test_api.py
```

### Exécution locale
Pour lancer l'application en local :
```bash
python3.10 src/main.py
```

## Déploiement

Le déploiement est automatisé via GitHub Actions :
- La branche `develop` déploie en environnement de staging
- La branche `main` déploie en production (après validation manuelle)

## Monitoring

- Prometheus : http://localhost:9090
- Grafana : http://localhost:3000

## Documentation

La documentation complète est disponible dans le dossier `docs/` :

- [Documentation API](docs/API_README.md) - Détails sur l'API REST
- [Documentation C4](docs/C4_README.md) - Informations sur la base de données et l'importation
- [Documentation RGPD](docs/RGPD_README.md) - Conformité avec le RGPD
- [Technologies](docs/TECHNOLOGIES.md) - Justification des choix technologiques

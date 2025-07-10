# Système d'Automatisation des Rapports Bancaires

Ce projet vise à automatiser la génération et l'envoi de rapports hebdomadaires aux directeurs des différentes banques du groupe, en utilisant l'intelligence artificielle pour analyser les données et générer des rapports pertinents.

## Prérequis

- Docker et Docker Compose
- Python 3.10
- Git

## 🗄️ Architecture de Base de Données

Le projet utilise une **architecture hybride intelligente** avec fallback automatique :

- **🐘 PostgreSQL** : Base principale (production, performance)
- **🗄️ SQLite** : Fallback automatique (développement, résilience)

### Avantages
- ✅ **Résilience** : Basculement transparent en cas de panne
- ✅ **Performance** : PostgreSQL pour la production
- ✅ **Simplicité** : SQLite pour le développement
- ✅ **Flexibilité** : Configuration automatique selon l'environnement

### Vérification du statut
```bash
# Script de vérification des bases de données
python check_database_status.py

# Endpoint API
curl http://localhost:8000/api/database-info
```

📚 **Documentation complète** : [docs/DATABASE_ARCHITECTURE.md](docs/DATABASE_ARCHITECTURE.md)

### Scripts utilitaires
```bash
# Vérifier le statut des bases de données
./scripts/database_utils.sh status

# Tester le système de fallback
./scripts/database_utils.sh full-test

# Afficher les commandes disponibles
./scripts/database_utils.sh
```

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

## Scripts d'exécution

### Initialisation et démarrage du projet

Pour initialiser et démarrer le projet complet avec Docker Compose :

```bash
./init_project.sh
```

Ce script effectue les opérations suivantes :
- Vérifie que Docker et Docker Compose sont installés
- Installe les dépendances Python
- Initialise la base de données avec Alembic
- Construit les images Docker
- Lance les conteneurs Docker

### Démarrage du projet (après initialisation)

Pour démarrer le projet après l'initialisation :

```bash
./run_project.sh
```

Ce script effectue les opérations suivantes :
- Vérifie que Docker et Docker Compose sont installés
- Vérifie si des conteneurs sont déjà en cours d'exécution
- Lance ou redémarre les conteneurs Docker
- Vérifie que tous les conteneurs sont en cours d'exécution
- Affiche les informations d'accès aux différents services

### Gestion des migrations de base de données

Pour gérer les migrations de la base de données :

```bash
# Initialiser la base de données
python -m src.scripts.init_db

# Créer une nouvelle migration
python -m src.scripts.create_migration "Description de la migration" --autogenerate

# Appliquer les migrations
python -m src.scripts.apply_migrations

# Afficher l'historique des migrations
python -m src.scripts.show_migrations
```

Pour plus d'informations sur les migrations, consultez le [Guide des Migrations](MIGRATIONS_README.md).

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

### 3. Analyse des données avec IA

L'application utilise un modèle d'IA pour analyser les données bancaires et générer des rapports pertinents :

```bash
# Analyser les données d'une banque spécifique
python3.10 src/scripts/analyze_bank.py --bank "Banque A" --format markdown

# Analyser toutes les banques filtrées
python3.10 src/scripts/analyze_filtered_banks.py --format markdown

# Générer un rapport global pour toutes les banques
python3.10 src/scripts/generate_global_report.py --format markdown
```

L'analyse inclut :
- Statistiques globales sur les montants et les transactions
- Tendances sur la période analysée
- Visualisations graphiques (histogrammes, courbes d'évolution)
- Recommandations basées sur l'analyse des données

### 4. Génération et envoi de rapports

L'application génère des rapports hebdomadaires et les envoie par email aux directeurs des différentes banques :

```bash
# Envoyer un rapport par email
python3.10 src/scripts/generate_global_report.py --format markdown --email --recipients "directeur@banque.com"

# Programmer l'envoi automatique des rapports
python3.10 src/scripts/schedule_reports.py --day Monday --time "08:00" --format markdown --email --recipients "directeur@banque.com"
```

Les rapports envoyés par email sont également stockés dans la base de données pour consultation ultérieure via l'interface utilisateur.

### 5. Interface utilisateur

L'application dispose d'une interface utilisateur web pour consulter les rapports et les visualisations :

```bash
# Lancer l'interface utilisateur Django
python3.10 manage.py runserver
```

L'interface utilisateur offre les fonctionnalités suivantes :
- Consultation des rapports générés
- Visualisation des graphiques par banque
- Historique des rapports envoyés par email
- Tableaux de bord interactifs

Pour accéder à l'interface utilisateur :
- URL : http://localhost:8000
- Identifiants par défaut : 
  - Utilisateur : `admin`
  - Mot de passe : `admin`

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

### Prometheus
- URL : http://localhost:9090
- Pas d'authentification requise
- Si le site est inaccessible, vérifiez que les conteneurs Docker sont bien lancés avec `docker-compose ps`
- Vous pouvez redémarrer Prometheus avec `docker-compose restart prometheus`

### Grafana
- URL : http://localhost:3000
- Identifiants par défaut : 
  - Utilisateur : `admin`
  - Mot de passe : `admin`
- Lors de la première connexion, Grafana vous demandera de changer le mot de passe par défaut

### Résolution des problèmes d'accès
Si vous ne pouvez pas accéder à Prometheus, Grafana ou l'API après avoir exécuté `init_project.sh`, vérifiez l'état des conteneurs Docker :

```bash
docker-compose ps
```

Si certains conteneurs ne sont pas en cours d'exécution, vous pouvez les redémarrer :

```bash
docker-compose restart [nom_du_service]
```

Ou redémarrer tous les services :

```bash
docker-compose down
docker-compose up -d
```

Alternativement, utilisez le script `run_project.sh` qui vérifiera l'état des conteneurs et les redémarrera si nécessaire :

```bash
./run_project.sh
```

## Documentation

La documentation complète est disponible dans le dossier `docs/` :

- [Documentation API](docs/API_README.md) - Détails sur l'API REST
- [Documentation C4](docs/C4_README.md) - Informations sur la base de données et l'importation
- [Documentation RGPD](docs/RGPD_README.md) - Conformité avec le RGPD
- [Documentation des Migrations](MIGRATIONS_README.md) - Guide pour gérer les migrations de base de données
- [Documentation des Rapports par Email](docs/EMAIL_REPORTS_README.md) - Guide pour les rapports par email et l'interface utilisateur
- [Technologies](docs/TECHNOLOGIES.md) - Justification des choix technologiques

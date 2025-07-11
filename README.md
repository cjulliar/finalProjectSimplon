# 🏦 Système d'Analyse et de Génération de Rapports Bancaires

Un système complet d'automatisation pour l'analyse et la génération de rapports bancaires utilisant FastAPI, Django, Celery et l'IA.

## 🚀 Démarrage Rapide

### Option 1: Installation complète (recommandée)
```bash
git clone https://github.com/cjulliar/finalProjectSimplon.git
cd finalProjectSimplon
chmod +x install_and_run.sh
./install_and_run.sh
```

### Option 2: Lancement rapide avec Docker
```bash
git clone https://github.com/cjulliar/finalProjectSimplon.git
cd finalProjectSimplon
chmod +x quick_start.sh
./quick_start.sh
```

### Option 3: Développement local
```bash
git clone https://github.com/cjulliar/finalProjectSimplon.git
cd finalProjectSimplon
chmod +x dev_start.sh
./dev_start.sh
```

## 🌐 Accès aux services

Une fois le projet lancé, vous pouvez accéder aux services suivants :

- **Frontend Django**: http://localhost:8080
- **API FastAPI**: http://localhost:8000 (Docker) ou http://localhost:8001 (Local)
- **Documentation API**: http://localhost:8000/docs (Docker) ou http://localhost:8001/docs (Local)
- **Monitoring Prometheus**: http://localhost:9090 (Docker uniquement)
- **Dashboard Grafana**: http://localhost:3000 (admin/admin) (Docker uniquement)

## 🔐 Identifiants de test

- **Email**: cyrjulliard@gmail.com
- **Mot de passe**: directeur123
- **Exemples d'utilisateurs**:
  - directeurBanqueA
  - directeurBanqueBG
  - directeurBanqueC

## 📊 Fonctionnalités

- **Dashboard personnalisé** par agence bancaire
- **74 directeurs d'agence** configurés avec données réelles
- **Données bancaires enrichies** avec analyses automatiques
- **Rapports automatiques** générés par IA
- **Analyses prédictives** et insights business
- **Interface responsive** et moderne
- **API REST complète** avec documentation Swagger
- **Monitoring en temps réel** avec Prometheus et Grafana
- **Traitement asynchrone** avec Celery et Redis

## 🛠️ Architecture

Le projet utilise une architecture microservices moderne :

- **Frontend**: Django 4.2 avec interface moderne et responsive
- **API**: FastAPI avec documentation automatique
- **Base de données**: PostgreSQL avec migrations Alembic
- **Cache et tâches**: Redis + Celery pour le traitement asynchrone
- **Monitoring**: Prometheus + Grafana
- **Conteneurisation**: Docker + Docker Compose
- **IA**: Intégration OpenAI et HuggingFace

## 📋 Prérequis

### Pour le mode Docker (recommandé)
- Docker
- Docker Compose

### Pour le mode local
- Python 3.10+
- pip3

## 🚀 Scripts de lancement

### `install_and_run.sh`
Script complet qui :
- Vérifie les prérequis
- Installe toutes les dépendances
- Configure la base de données
- Crée les utilisateurs de test
- Propose le choix entre Docker et local
- Lance le projet

### `quick_start.sh`
Script rapide pour Docker qui :
- Vérifie Docker
- Arrête les conteneurs existants
- Construit et démarre tous les services
- Affiche les URLs d'accès

### `dev_start.sh`
Script pour le développement local qui :
- Crée l'environnement virtuel
- Installe les dépendances
- Configure la base de données
- Lance les services en mode développement
- Active le rechargement automatique

### `start_project.sh`
Script de lancement existant (mode local uniquement)

### `stop_project.sh`
Script pour arrêter tous les services

## 🔧 Configuration

### Variables d'environnement

Le projet utilise des variables d'environnement par défaut pour le développement. Pour la production, créez un fichier `.env` :

```env
# Base de données
POSTGRES_HOST=localhost
POSTGRES_DB=bankreports
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# API
API_SECRET_KEY=your-secret-key
API_ALGORITHM=HS256
API_ACCESS_TOKEN_EXPIRE_MINUTES=30

# IA
LLM_API_KEY=your-openai-key
HUGGINGFACE_API_KEY=your-huggingface-key
USE_OPENAI=true
USE_HUGGINGFACE=false

# Celery
REDIS_URL=redis://localhost:6379/0
```

### Configuration SMTP

Pour l'envoi d'emails, créez un fichier `smtp_config.env` :

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 📁 Structure du projet

```
finalProjectSimplon/
├── src/                    # Code source principal
│   ├── api/               # API FastAPI
│   ├── db/                # Modèles et configuration DB
│   ├── ia/                # Services d'IA
│   ├── scripts/           # Scripts utilitaires
│   └── tasks/             # Tâches Celery
├── frontend/              # Interface Django
│   ├── bankapp/          # Application principale
│   ├── dashboard/        # Dashboard personnalisé
│   ├── ai_reports/       # Rapports IA
│   └── templates/        # Templates HTML
├── docker/                # Configuration Docker
├── scripts/               # Scripts de lancement
├── migrations/            # Migrations Alembic
├── requirements.txt       # Dépendances Python
├── docker-compose.yml     # Configuration Docker Compose
├── install_and_run.sh     # Script d'installation complet
├── quick_start.sh         # Script de lancement rapide
├── dev_start.sh           # Script de développement
└── README.md             # Ce fichier
```

## 🧪 Tests

```bash
# Exécuter tous les tests
python tests/run_all_tests.py

# Tests avec pytest
pytest tests/ -v

# Tests de l'API
python -m pytest tests/test_api.py -v
```

## 🚀 Déploiement

### CI/CD

Le projet utilise GitHub Actions pour le CI/CD :

1. **Tests automatiques** sur chaque push
2. **Build Docker** automatique
3. **Déploiement staging** sur la branche `develop`
4. **Déploiement production** sur la branche `main`

### Production

```bash
# Build pour la production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Variables d'environnement de production
export ADMIN_PASSWORD=your-secure-password
export API_SECRET_KEY=your-secure-secret-key
export LLM_API_KEY=your-production-openai-key
```

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour toute question ou problème :

1. Consultez la [documentation de l'API](http://localhost:8000/docs)
2. Vérifiez les [issues GitHub](https://github.com/cjulliar/finalProjectSimplon/issues)
3. Créez une nouvelle issue si nécessaire

## 🔄 Mises à jour

```bash
# Mettre à jour le code
git pull origin main

# Mettre à jour les dépendances
pip install -r requirements.txt --upgrade

# Redémarrer les services Docker
docker-compose down && docker-compose up -d
```

## 📊 Données

Le projet inclut :
- **Base de données SQLite** avec données bancaires enrichies
- **74 directeurs d'agence** avec profils complets
- **Données de transactions** réelles
- **Analyses prédictives** générées par IA
- **Rapports automatiques** personnalisés

## 🎯 Objectifs du projet

Ce système permet aux directeurs d'agence de :
- Visualiser leurs performances en temps réel
- Recevoir des analyses prédictives
- Générer des rapports automatiques
- Comparer leurs résultats avec d'autres agences
- Prendre des décisions basées sur l'IA

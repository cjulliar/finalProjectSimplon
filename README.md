# Système d'Analyse et de Génération de Rapports Bancaires

Un système complet d'automatisation pour l'analyse et la génération de rapports bancaires utilisant FastAPI, Django, Celery et l'IA.

## 🚀 Fonctionnalités

- **API REST** avec FastAPI pour la gestion des données bancaires
- **Interface web** avec Django pour la visualisation et l'administration
- **Traitement asynchrone** avec Celery pour les tâches en arrière-plan
- **Intégration IA** pour l'analyse automatique des données
- **Base de données** PostgreSQL avec migrations Alembic
- **Monitoring** avec Prometheus et Grafana
- **Déploiement** avec Docker et CI/CD GitHub Actions

## 📋 Prérequis

- Python 3.10+
- Docker et Docker Compose
- Git

## 🛠️ Installation

### Option 1: Développement local

1. **Cloner le repository**
   ```bash
   git clone https://github.com/cjulliar/finalProjectSimplon.git
   cd finalProjectSimplon
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Configurer la base de données**
   ```bash
   # Créer les tables
   python src/main.py
   
   # Créer un utilisateur administrateur
   python src/scripts/setup_admin.py --username admin --password admin123
   ```

5. **Démarrer l'API**
   ```bash
   python src/scripts/run_api.py
   ```

### Option 2: Docker (Recommandé)

1. **Cloner le repository**
   ```bash
   git clone https://github.com/cjulliar/finalProjectSimplon.git
   cd finalProjectSimplon
   ```

2. **Démarrer avec Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Créer un utilisateur administrateur**
   ```bash
   docker-compose exec api python src/scripts/setup_admin.py --username admin --password admin123
   ```

## 🌐 Accès aux services

- **API FastAPI**: http://localhost:8000
  - Documentation Swagger: http://localhost:8000/docs
  - Documentation ReDoc: http://localhost:8000/redoc

- **Interface Django**: http://localhost:8080
  - Admin: http://localhost:8080/admin

- **Monitoring**:
  - Prometheus: http://localhost:9090
  - Grafana: http://localhost:3000 (admin/admin)

## 📊 Utilisation

### 1. Import de données

```bash
# Importer des données Excel
python src/main.py --import-excel --file docs/DonneeBanque.xlsx
```

### 2. API REST

```bash
# Authentification
curl -X POST "http://localhost:8000/api/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Récupérer les données
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/bank-data"
```

### 3. Interface web

1. Accédez à http://localhost:8080
2. Connectez-vous avec les identifiants admin/admin123
3. Naviguez dans l'interface pour visualiser les données

## 🔧 Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet :

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
├── docker/                # Configuration Docker
├── tests/                 # Tests
├── docs/                  # Documentation
├── migrations/            # Migrations Alembic
├── requirements.txt       # Dépendances Python
├── docker-compose.yml     # Configuration Docker Compose
└── README.md             # Ce fichier
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
git pull origin develop

# Mettre à jour les dépendances
pip install -r requirements.txt --upgrade

# Redémarrer les services Docker
docker-compose down && docker-compose up -d
```

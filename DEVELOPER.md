# 👨‍💻 Guide du Développeur

Ce guide contient toutes les informations techniques nécessaires pour contribuer au projet.

## 🏗️ Architecture Technique

### Stack Technologique

- **Backend API**: FastAPI (Python 3.11)
- **Frontend**: Django 4.2 (Python 3.11)
- **Base de données**: PostgreSQL + SQLite (développement)
- **Cache & Tâches**: Redis + Celery
- **Monitoring**: Prometheus + Grafana
- **Conteneurisation**: Docker + Docker Compose
- **IA**: OpenAI API + HuggingFace

### Structure des Services

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API FastAPI   │    │   Base de       │
│   Django        │◄──►│   (Port 8000)   │◄──►│   Données       │
│   (Port 8080)   │    │                 │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Monitoring    │    │   Celery        │    │   Redis         │
│   Grafana       │    │   Workers       │    │   Cache         │
│   Prometheus    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Environnement de Développement

### Prérequis

```bash
# Python 3.11+
python3 --version

# pip3
pip3 --version

# Docker (optionnel)
docker --version
docker-compose --version

# Git
git --version
```

### Installation pour le Développement

1. **Cloner le projet**
   ```bash
   git clone https://github.com/cjulliar/finalProjectSimplon.git
   cd finalProjectSimplon
   ```

2. **Créer l'environnement virtuel**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows
   ```

3. **Installer les dépendances**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r frontend/requirements.txt
   ```

4. **Configurer la base de données**
   ```bash
   # Copier la base de données de développement
   cp bankreports.db frontend/bankreports.db
   
   # Appliquer les migrations Django
   cd frontend
   python manage.py makemigrations
   python manage.py migrate
   cd ..
   ```

5. **Créer les utilisateurs de test**
   ```bash
   python create_users.py
   python create_director_users.py
   ```

### Lancement en Mode Développement

```bash
# Option 1: Script automatique
./dev_start.sh

# Option 2: Manuel
# Terminal 1 - API FastAPI
cd src
python -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Frontend Django
cd frontend
python manage.py runserver 0.0.0.0:8080
```

## 📁 Structure du Code

### Backend (src/)

```
src/
├── api/                    # API FastAPI
│   ├── main.py            # Point d'entrée de l'API
│   ├── models.py          # Modèles Pydantic
│   ├── routes/            # Routes de l'API
│   └── dependencies.py    # Dépendances FastAPI
├── db/                    # Configuration base de données
│   ├── models.py          # Modèles SQLAlchemy
│   ├── database.py        # Configuration DB
│   └── migrations/        # Migrations Alembic
├── ia/                    # Services d'IA
│   ├── openai_service.py  # Service OpenAI
│   ├── analysis.py        # Analyses IA
│   └── prompts.py         # Prompts IA
├── tasks/                 # Tâches Celery
│   ├── email_tasks.py     # Tâches d'email
│   └── analysis_tasks.py  # Tâches d'analyse
└── utils/                 # Utilitaires
    ├── helpers.py         # Fonctions utilitaires
    └── validators.py      # Validateurs
```

### Frontend (frontend/)

```
frontend/
├── bankapp/               # Application principale
│   ├── models.py          # Modèles Django
│   ├── views.py           # Vues Django
│   ├── urls.py            # URLs Django
│   └── forms.py           # Formulaires
├── dashboard/             # Dashboard personnalisé
│   ├── views.py           # Vues du dashboard
│   └── templates/         # Templates du dashboard
├── ai_reports/            # Rapports IA
│   ├── views.py           # Vues des rapports
│   └── templates/         # Templates des rapports
├── templates/             # Templates globaux
│   ├── base.html          # Template de base
│   └── components/        # Composants réutilisables
└── static/                # Fichiers statiques
    ├── css/               # Styles CSS
    ├── js/                # JavaScript
    └── images/            # Images
```

## 🔧 Configuration

### Variables d'Environnement

Créez un fichier `.env` à la racine :

```env
# Base de données
POSTGRES_HOST=localhost
POSTGRES_DB=bankreports
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
USE_POSTGRES=false  # true pour PostgreSQL, false pour SQLite

# API
API_SECRET_KEY=your-secret-key-here
API_ALGORITHM=HS256
API_ACCESS_TOKEN_EXPIRE_MINUTES=30

# IA
LLM_API_KEY=your-openai-api-key
HUGGINGFACE_API_KEY=your-huggingface-key
USE_OPENAI=true
USE_HUGGINGFACE=false
USE_FALLBACK_MODE=true

# Celery
REDIS_URL=redis://localhost:6379/0

# Django
DEBUG=True
SECRET_KEY=django-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

### Configuration SMTP

Pour les emails, créez `smtp_config.env` :

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 🧪 Tests

### Exécution des Tests

```bash
# Tests unitaires
python -m pytest tests/ -v

# Tests d'intégration
python -m pytest tests/integration/ -v

# Tests de l'API
python -m pytest tests/test_api.py -v

# Tests Django
cd frontend
python manage.py test
cd ..

# Tests avec couverture
python -m pytest tests/ --cov=src --cov=frontend --cov-report=html
```

### Tests Manuels

```bash
# Test de l'API
curl -X GET "http://localhost:8001/health"

# Test du frontend
curl -X GET "http://localhost:8080/login/"

# Test d'authentification
curl -X POST "http://localhost:8001/api/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=cyrjulliard@gmail.com&password=directeur123"
```

## 🔍 Debugging

### Logs

```bash
# Logs Django
tail -f frontend/django.log

# Logs FastAPI
tail -f src/api.log

# Logs Celery
tail -f celery.log

# Logs Docker
docker-compose logs -f
```

### Debugging Python

```python
# Dans le code Python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Message de debug")
```

### Debugging avec VS Code

Créez `.vscode/launch.json` :

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "src.api.main:app",
                "--host", "0.0.0.0",
                "--port", "8001",
                "--reload"
            ],
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: Django",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/frontend/manage.py",
            "args": [
                "runserver",
                "0.0.0.0:8080"
            ],
            "cwd": "${workspaceFolder}/frontend"
        }
    ]
}
```

## 📊 Base de Données

### Modèles Principaux

```python
# src/db/models.py
class BankReport(Base):
    __tablename__ = "bank_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    director_name = Column(String, index=True)
    agency_name = Column(String, index=True)
    transaction_amount = Column(Float)
    transaction_count = Column(Integer)
    date = Column(Date)
    analysis = Column(Text)

# frontend/bankapp/models.py
class Director(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    agency = models.CharField(max_length=100)
    password = models.CharField(max_length=128)
```

### Migrations

```bash
# Créer une migration
cd frontend
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Migrations Alembic (backend)
cd src
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## 🔄 API Endpoints

### Authentification

```bash
# Obtenir un token
POST /api/token
Content-Type: application/x-www-form-urlencoded

username=cyrjulliard@gmail.com&password=directeur123
```

### Données Bancaires

```bash
# Récupérer les rapports
GET /api/bank-reports
Authorization: Bearer <token>

# Récupérer un rapport spécifique
GET /api/bank-reports/{report_id}
Authorization: Bearer <token>

# Créer un rapport
POST /api/bank-reports
Authorization: Bearer <token>
Content-Type: application/json

{
    "director_name": "John Doe",
    "agency_name": "Agence Paris",
    "transaction_amount": 150000.0,
    "transaction_count": 45
}
```

### Analyses IA

```bash
# Générer une analyse
POST /api/analysis/generate
Authorization: Bearer <token>
Content-Type: application/json

{
    "director_name": "John Doe",
    "analysis_type": "performance"
}
```

## 🚀 Déploiement

### Production avec Docker

```bash
# Build pour la production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Variables d'environnement de production
export ADMIN_PASSWORD=your-secure-password
export API_SECRET_KEY=your-secure-secret-key
export LLM_API_KEY=your-production-openai-key
```

### Production sans Docker

```bash
# Installer les dépendances de production
pip install -r requirements.txt
pip install gunicorn

# Démarrer avec Gunicorn
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Démarrer Django avec Gunicorn
cd frontend
gunicorn frontend.wsgi:application -w 4 --bind 0.0.0.0:8080
```

## 🤝 Contribution

### Workflow Git

1. **Fork le projet**
2. **Créer une branche feature**
   ```bash
   git checkout -b feature/nouvelle-fonctionnalite
   ```
3. **Développer et tester**
   ```bash
   # Tests
   python -m pytest tests/ -v
   
   # Linting
   flake8 src/ frontend/
   
   # Formatage
   black src/ frontend/
   ```
4. **Commiter les changements**
   ```bash
   git add .
   git commit -m "feat: ajouter nouvelle fonctionnalité"
   ```
5. **Pousser vers GitHub**
   ```bash
   git push origin feature/nouvelle-fonctionnalite
   ```
6. **Créer une Pull Request**

### Standards de Code

- **Python**: PEP 8, Black, Flake8
- **Django**: Style guide Django
- **FastAPI**: Style guide FastAPI
- **Commits**: Conventional Commits
- **Documentation**: Docstrings en français

### Tests Obligatoires

Avant chaque PR, assurez-vous que :

```bash
# Tous les tests passent
python -m pytest tests/ -v

# Le code est formaté
black src/ frontend/

# Pas d'erreurs de linting
flake8 src/ frontend/

# La documentation est à jour
python -m pydocstyle src/
```

## 📚 Ressources

- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation Django](https://docs.djangoproject.com/)
- [Documentation Celery](https://docs.celeryproject.org/)
- [Documentation Docker](https://docs.docker.com/)
- [Guide PEP 8](https://www.python.org/dev/peps/pep-0008/) 
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

## Structure du Projet

```
.
├── docker/                 # Configurations Docker
├── docs/                   # Documentation et données
├── src/                    # Code source
│   ├── api/               # API FastAPI
│   ├── core/              # Logique métier
│   ├── db/                # Modèles et migrations
│   └── utils/             # Utilitaires
├── tests/                 # Tests
├── .env                   # Variables d'environnement
├── docker-compose.yml     # Configuration Docker Compose
└── requirements.txt       # Dépendances Python
```

## Développement

### Tests
Pour exécuter les tests :
```bash
python3.10 -m pytest tests/
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

La documentation complète est disponible dans le dossier `docs/`.

# 🏦 Système de Rapports Bancaires Intelligents

Un système moderne de génération de rapports bancaires utilisant l'intelligence artificielle pour analyser les données financières et générer des insights automatisés.

## 🚀 Technologies

Le projet utilise une architecture moderne :

- **Frontend**: Django 4.2 avec interface moderne et responsive
- **API**: FastAPI avec documentation automatique
- **Base de données**: SQLite consolidée
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

Pour l'envoi d'emails, configurez les variables SMTP :

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 📊 Fonctionnalités

### 🎯 Rapports Automatisés
- Génération automatique de rapports hebdomadaires
- Analyse des tendances et performances
- Détection d'anomalies
- Recommandations personnalisées

### 🤖 Intelligence Artificielle
- Intégration OpenAI GPT pour l'analyse de texte
- Modèles HuggingFace pour le traitement spécialisé
- Génération automatique de contenu
- Analyse sémantique des données

### 📈 Dashboard Interactif
- Visualisations en temps réel
- Graphiques interactifs
- Filtres dynamiques
- Export de données

### 🔐 Sécurité
- Authentification JWT
- Gestion des rôles et permissions
- Chiffrement des données sensibles
- Audit trail complet

## 🗄️ Base de données

Le projet utilise une base SQLite consolidée (`bankreports.db`) qui contient :
- Données bancaires enrichies
- Rapports générés par IA
- Utilisateurs et authentification
- Historique des analyses

## 🚀 Démarrage rapide

1. **Cloner le projet** :
   ```bash
   git clone <repository-url>
   cd finalProjectSimplon
   ```

2. **Lancer avec Docker** :
   ```bash
   ./quick_start.sh
   ```

3. **Ou lancer en local** :
   ```bash
   ./dev_start.sh
   ```

4. **Accéder à l'application** :
   - Frontend : http://localhost:8080
   - API : http://localhost:8001
   - Documentation API : http://localhost:8001/docs

## 👥 Utilisateurs par défaut

- **Admin** : `admin` / `admin123`
- **Directeurs** : `directeurBanqueX` / `directeur123` (où X = A, B, C, etc.)
- **Test** : `testuser` / `test123`

## 📚 Documentation

- [Guide de production](PRODUCTION_README.md)
- [Architecture technique](DEVELOPER.md)
- [API Documentation](http://localhost:8001/docs)

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème :
1. Consulter la [documentation](PRODUCTION_README.md)
2. Vérifier les [issues](https://github.com/your-repo/issues)
3. Créer une nouvelle issue si nécessaire

---

**Développé avec ❤️ pour Simplon**

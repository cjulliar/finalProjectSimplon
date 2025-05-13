# Scripts de gestion du projet d'Automatisation des Rapports Bancaires

Ce dossier contient des scripts utilitaires pour faciliter le lancement, l'arrêt et la surveillance du projet.

## Prérequis

- Docker et Docker Compose installés et fonctionnels
- Bash (Linux/macOS) ou Git Bash (Windows)

## Scripts disponibles

### 1. `run_project.sh`

Ce script lance tous les services nécessaires au fonctionnement du projet :
- L'API FastAPI
- Le frontend Django
- Les services de monitoring (si configurés)

**Utilisation :**
```bash
./run_project.sh
```

Le script effectue les actions suivantes :
1. Vérifie que Docker et Docker Compose sont installés et en cours d'exécution
2. Démarre tous les services avec Docker Compose
3. Vérifie que les services sont correctement lancés
4. Propose de générer des données de test
5. Affiche les informations d'accès (URLs, identifiants)

### 2. `stop_project.sh`

Ce script arrête tous les services du projet.

**Utilisation :**
```bash
./stop_project.sh
```

### 3. `show_logs.sh`

Ce script permet de consulter les logs des différents services.

**Utilisation :**
```bash
./show_logs.sh
```

Le script affiche un menu interactif permettant de choisir :
1. Afficher les logs de l'API
2. Afficher les logs du Frontend
3. Afficher les logs de tous les services
4. Quitter

## Accès aux services

Une fois les services démarrés avec `run_project.sh`, vous pouvez accéder à :

- **API FastAPI** : http://localhost:8000
  - Documentation Swagger : http://localhost:8000/docs
  - Documentation ReDoc : http://localhost:8000/redoc

- **Frontend Django** : http://localhost:8080
  - Identifiants par défaut : admin / admin123

## Résolution des problèmes courants

### Les services ne démarrent pas

Vérifiez que :
1. Docker Desktop est bien lancé
2. Les ports 8000 et 8080 ne sont pas déjà utilisés par d'autres applications
3. Vous avez les droits nécessaires pour exécuter Docker

Pour voir les logs détaillés en cas d'erreur :
```bash
docker compose logs
```

### Erreur "Permission denied" lors de l'exécution des scripts

Assurez-vous que les scripts sont exécutables :
```bash
chmod +x run_project.sh stop_project.sh show_logs.sh
``` 
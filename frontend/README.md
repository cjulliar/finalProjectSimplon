# Interface Utilisateur Django pour les Rapports Bancaires

Ce dossier contient l'interface utilisateur développée avec Django pour le Système d'Automatisation des Rapports Bancaires.

## Fonctionnalités

- Tableau de bord avec visualisations des données bancaires
- Consultation et filtrage des données bancaires
- Création et affichage des rapports d'analyse IA
- Authentification sécurisée (intégrée avec le système JWT de l'API)

## Structure du projet

- `frontend/` : Package principal Django
- `dashboard/` : Application pour le tableau de bord
- `bank_data/` : Application pour la gestion des données bancaires
- `ai_reports/` : Application pour la gestion des rapports d'IA
- `templates/` : Templates HTML partagés
- `static/` : Fichiers statiques (CSS, JS, images)

## Installation et démarrage (développement)

### Installation locale

1. Créer un environnement virtuel Python :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Configurer les variables d'environnement :
   ```bash
   export DEBUG=True
   export SECRET_KEY="django-insecure-key-for-development"
   export API_URL="http://localhost:8000"
   export API_SECRET_KEY="your-api-secret-key"
   ```

4. Lancer l'application :
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   python manage.py runserver 8080
   ```

5. Accéder à l'application : http://localhost:8080

### Avec Docker

```bash
docker-compose up -d frontend
```

Accéder à l'application : http://localhost:8080

## Authentification

L'interface utilise l'authentification de l'API. Pour vous connecter :

1. Utilisez les mêmes identifiants que ceux de l'API
2. L'interface obtient un token JWT et le stocke en session
3. Ce token est utilisé pour toutes les requêtes vers l'API

## Développement et tests

### Tests

Exécuter les tests :
```bash
python manage.py test
```

### Structure des templates

- Base template : `templates/base.html`
- Tableau de bord : `templates/dashboard/dashboard.html`
- Données bancaires : `templates/bank_data/list.html`, `templates/bank_data/detail.html`
- Rapports IA : `templates/ai_reports/list.html`, `templates/ai_reports/detail.html`, `templates/ai_reports/create.html`

### Communication avec l'API

La communication avec l'API est gérée par la classe `APIClient` dans `dashboard/services.py`. Cette classe encapsule toutes les requêtes vers l'API FastAPI. 
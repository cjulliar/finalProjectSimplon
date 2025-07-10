# Guide des Migrations de Base de Données

Ce projet utilise Alembic pour gérer les migrations de base de données. Ce document explique comment utiliser les scripts de migration.

## Prérequis

- Python 3.10 ou supérieur
- Alembic (`pip install alembic`)
- SQLAlchemy (`pip install sqlalchemy`)
- PostgreSQL (pour la production) ou SQLite (pour le développement)

## 🗄️ Architecture Hybride des Bases de Données

Ce projet utilise un **système de fallback automatique** :

- **🐘 PostgreSQL** : Base principale (production, performance)
- **🗄️ SQLite** : Fallback automatique (développement, résilience)

### Vérification de la base utilisée
```bash
# Vérifier quelle base de données est actuellement utilisée
python check_database_status.py

# Ou via l'API
curl http://localhost:8000/api/database-info
```

Les migrations fonctionnent automatiquement sur la base de données active (PostgreSQL ou SQLite selon la disponibilité).

## Scripts disponibles

### Initialisation de la base de données

Pour initialiser la base de données avec les migrations existantes :

```bash
python -m src.scripts.init_db
```

Pour initialiser la base de données et créer un utilisateur administrateur :

```bash
python -m src.scripts.init_db --create-admin --username admin --password votremotdepasse --email admin@example.com
```

### Création d'une nouvelle migration

Pour créer une nouvelle migration vide :

```bash
python -m src.scripts.create_migration "Description de la migration"
```

Pour générer automatiquement une migration à partir des modifications des modèles :

```bash
python -m src.scripts.create_migration "Description de la migration" --autogenerate
```

### Application des migrations

Pour appliquer toutes les migrations jusqu'à la plus récente :

```bash
python -m src.scripts.apply_migrations
```

Pour appliquer les migrations jusqu'à une révision spécifique :

```bash
python -m src.scripts.apply_migrations --revision abc123
```

Pour rétrograder à une révision précédente :

```bash
python -m src.scripts.apply_migrations --revision abc123 --downgrade
```

### Affichage de l'historique des migrations

Pour afficher l'historique des migrations :

```bash
python -m src.scripts.show_migrations
```

Pour afficher des informations détaillées sur les migrations :

```bash
python -m src.scripts.show_migrations --verbose
```

## Utilisation avec Docker

Le projet est configuré pour utiliser SQLite en développement local et PostgreSQL en production avec Docker.

Pour démarrer l'application avec Docker Compose :

```bash
./init_project.sh
```

## Structure des fichiers de migration

Les fichiers de migration sont stockés dans le répertoire `migrations/versions/`. Chaque fichier contient deux fonctions :

- `upgrade()` : Applique les modifications à la base de données
- `downgrade()` : Annule les modifications (pour revenir à l'état précédent)

## Bonnes pratiques

1. **Toujours créer une migration** pour les modifications de schéma de base de données
2. **Tester les migrations** avant de les déployer en production
3. **Ne jamais modifier** un fichier de migration existant qui a déjà été appliqué
4. **Versionner** les fichiers de migration dans le système de gestion de versions
5. **Documenter** les changements importants dans le message de la migration

## Résolution des problèmes courants

### Erreur "Target database is not up to date"

Si vous obtenez cette erreur lors de la création d'une migration avec `--autogenerate`, cela signifie que votre base de données n'est pas à jour avec les migrations existantes. Exécutez d'abord :

```bash
python -m src.scripts.apply_migrations
```

### Erreur "Can't locate revision"

Si vous obtenez cette erreur lors de l'application d'une migration, vérifiez que l'identifiant de révision est correct et que le fichier de migration existe dans le répertoire `migrations/versions/`. 
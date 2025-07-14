# Consolidation des Bases de Données

**Date de consolidation :** 2025-07-14 19:36:40

## Base de données unique

Le projet utilise maintenant une seule base de données SQLite :
- `bankreports.db` : Base consolidée principale

## Sauvegardes

Les anciennes bases ont été déplacées dans :
- `old_databases_backup_20250714_193639/` : Anciennes bases de données
- `users_backup_*.json` : Sauvegardes des utilisateurs Django

## Configuration

Django est configuré pour utiliser automatiquement la base consolidée.
Voir `frontend/frontend/settings.py` pour la configuration.

## Prévention des régressions

1. Toujours utiliser `bankreports.db` comme base unique
2. Sauvegarder les utilisateurs avant toute opération : `python backup_users.py backup`
3. Restaurer les utilisateurs si nécessaire : `python backup_users.py restore --file users_backup_*.json`

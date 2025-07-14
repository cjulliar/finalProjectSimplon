# BASE DE DONNÉES CONSOLIDÉE

## 📊 Informations
- **Fichier**: bankreports.db
- **Type**: SQLite
- **Taille**: 11 MB
- **Date de consolidation**: 2025-07-14 13:47:49

## 📋 Tables
- alembic_version
- analyses
- bank_data_enriched
- email_reports
- execution_logs
- scheduled_reports
- sqlite_sequence
- users
- visualizations

## 📊 Statistiques
- users: 76 enregistrements
- email_reports: 1 enregistrements
- bank_data_enriched: 4292 enregistrements
- analyses: 4478 enregistrements

## 🔧 Utilisation
- **Django**: Utilise cette base via la configuration dans frontend/settings.py
- **FastAPI**: Utilise cette base via la configuration dans src/db/database.py
- **Backup**: Utilise le script backup_database.sh

## 🚀 Déploiement
Cette base SQLite est prête pour le déploiement sur serveur.
- Copier le fichier bankreports.db sur le serveur
- Configurer les permissions appropriées
- Utiliser le script de backup pour la maintenance

## 📝 Notes
- Base unique pour tout le projet
- Compatible production
- Backup automatique recommandé

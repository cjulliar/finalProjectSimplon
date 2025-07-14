# 🏦 Projet Bancaire Intelligent - Guide de Production

## 📋 Vue d'ensemble

Ce projet est un système bancaire intelligent utilisant Django et FastAPI avec une base de données SQLite consolidée.

## 🗄️ Base de données

### Configuration actuelle
- **Base de production** : `bankreports.db` (11.9 MB)
- **Type** : SQLite
- **Utilisateurs** : 78 (dont 74 directeurs de banque)
- **Emails** : 75 rapports générés par IA
- **Données bancaires** : 4292 enregistrements

### Sauvegardes
- **Sauvegarde automatique** : `bankreports_production_backup_YYYYMMDD_HHMMSS.db`
- **Anciennes bases** : `old_databases_backup_YYYYMMDD_HHMMSS/`
- **Sauvegarde utilisateurs** : `users_backup_YYYYMMDD_HHMMSS.json`

## 👥 Utilisateurs

### Directeurs de banque
- **Format** : `directeurBanqueX` (où X = A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z, AA, AB, AC, etc.)
- **Mot de passe** : `directeur123`
- **Email** : `cyrjulliard@gmail.com` (pour tous les directeurs)

### Autres utilisateurs
- **admin** : Superutilisateur
- **testuser** : Utilisateur de test (mot de passe : `test123`)
- **manager1** : Manager
- **user1** : Utilisateur standard

## 🌐 Services

### Django (Frontend)
- **URL** : http://localhost:8080
- **Port** : 8080
- **Base de données** : SQLite (`bankreports.db`)

### FastAPI (Backend)
- **URL** : http://localhost:8001
- **Port** : 8001
- **Base de données** : SQLite (`bankreports.db`)

## 🔧 Scripts de maintenance

### Vérification de l'intégrité
```bash
python verify_project_integrity.py
```

### Sauvegarde de la base de production
```bash
python backup_production_db.py backup
```

### Liste des sauvegardes
```bash
python backup_production_db.py list
```

### Restauration d'une sauvegarde
```bash
python backup_production_db.py restore --file bankreports_production_backup_YYYYMMDD_HHMMSS.db
```

### Sauvegarde des utilisateurs
```bash
python backup_users.py backup
```

### Restauration des utilisateurs
```bash
python backup_users.py restore --file users_backup_YYYYMMDD_HHMMSS.json
```

### Vérification rapide de la base
```bash
python check_database_integrity.py
```

## 📧 Emails par banque

Chaque directeur de banque voit les emails de sa banque respective :
- `directeurBanqueA` → emails de la banque "A"
- `directeurBanqueB` → emails de la banque "B"
- etc.

## 🚀 Démarrage en production

1. **Démarrer Django** :
   ```bash
   cd frontend
   python manage.py runserver 0.0.0.0:8080
   ```

2. **Démarrer FastAPI** :
   ```bash
   python -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload
   ```

3. **Accéder à l'application** :
   - URL : http://localhost:8080
   - Identifiants : `directeurBanqueX` / `directeur123`

## 🔒 Sécurité

### Variables d'environnement
- `SECRET_KEY` : Clé secrète Django
- `DEBUG` : Mode debug (True/False)
- `ALLOWED_HOSTS` : Hôtes autorisés
- `API_URL` : URL de l'API FastAPI
- `API_SECRET_KEY` : Clé secrète API

### Bonnes pratiques
- Toujours sauvegarder avant toute modification
- Vérifier l'intégrité après les opérations
- Utiliser uniquement la base `bankreports.db`
- Ne pas créer de bases multiples

## 📊 Monitoring

### Vérifications automatiques
- Base de données unique
- Utilisateurs complets
- Services web accessibles
- Emails disponibles
- Configuration correcte

### Alertes
- Plusieurs bases détectées
- Utilisateurs manquants
- Services inaccessibles
- Emails manquants

## 🛠️ Dépannage

### Problème : Plusieurs bases de données
```bash
python cleanup_redundant_dbs.py
```

### Problème : Utilisateurs manquants
```bash
python create_directeurs.py
python backup_users.py restore --file users_backup_YYYYMMDD_HHMMSS.json
```

### Problème : Services inaccessibles
1. Vérifier que les ports 8080 et 8001 sont libres
2. Redémarrer les services
3. Vérifier les logs

### Problème : Emails non visibles
1. Vérifier le statut des emails (`generated`)
2. Vérifier la correspondance banque/utilisateur
3. Vérifier la base de données

## 📝 Logs

### Django
- Logs dans la console lors du démarrage
- Messages d'erreur dans la console

### FastAPI
- Logs dans la console lors du démarrage
- Messages d'erreur dans la console

## 🔄 Mise à jour

### Procédure de mise à jour
1. Sauvegarder la base : `python backup_production_db.py backup`
2. Sauvegarder les utilisateurs : `python backup_users.py backup`
3. Appliquer les modifications
4. Vérifier l'intégrité : `python verify_project_integrity.py`
5. Tester l'application

### Rollback
1. Restaurer la base : `python backup_production_db.py restore --file backup_file.db`
2. Restaurer les utilisateurs : `python backup_users.py restore --file users_backup.json`
3. Vérifier l'intégrité

## 📞 Support

En cas de problème :
1. Vérifier l'intégrité : `python verify_project_integrity.py`
2. Consulter les logs
3. Vérifier la base de données
4. Restaurer depuis une sauvegarde si nécessaire

---

**Dernière mise à jour** : 2025-07-14 19:45
**Version** : Production v1.0
**Base de données** : SQLite consolidée 
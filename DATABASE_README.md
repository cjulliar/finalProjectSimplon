# 🗄️ Guide Pratique - Gestion des Bases de Données

## 🚀 Démarrage Rapide

### Vérification du statut actuel
```bash
# Vérifier quelle base est utilisée
python check_database_status.py

# Via l'API
curl http://localhost:8000/api/database-info
```

### Configuration par défaut
- **Production/Docker** : PostgreSQL avec fallback SQLite
- **Développement local** : SQLite avec PostgreSQL optionnel
- **Tests** : SQLite isolé

## 🔧 Commandes Utiles

### Gestion des conteneurs
```bash
# Démarrer tout le projet
./run_project.sh

# Redémarrer seulement la base de données
docker restart finalprojectsimplon-db-1

# Redémarrer l'API (pour appliquer changements de code)
docker restart finalprojectsimplon-api-1

# Arrêter le projet
./stop_project.sh
```

### Test du système de fallback
```bash
# 1. Tester le fallback : arrêter PostgreSQL
docker stop finalprojectsimplon-db-1
docker restart finalprojectsimplon-api-1
python check_database_status.py  # → Doit afficher SQLite

# 2. Tester le retour : redémarrer PostgreSQL
docker start finalprojectsimplon-db-1
docker restart finalprojectsimplon-api-1
python check_database_status.py  # → Doit afficher PostgreSQL
```

### Accès direct aux bases

#### PostgreSQL
```bash
# Connexion via Docker
docker exec -it finalprojectsimplon-db-1 psql -U postgres -d bankreports

# Commandes utiles PostgreSQL
\dt              # Lister les tables
\d bank_data     # Décrire la table bank_data
SELECT COUNT(*) FROM bank_data;
```

#### SQLite
```bash
# Connexion locale
sqlite3 bankreports.db

# Commandes utiles SQLite
.tables          # Lister les tables
.schema bank_data # Décrire la table bank_data
SELECT COUNT(*) FROM bank_data;
```

## 📊 Surveillance et Debugging

### Logs importantes à surveiller
```bash
# Logs de l'API (connexions de base)
docker logs finalprojectsimplon-api-1 --tail=20

# Logs de PostgreSQL
docker logs finalprojectsimplon-db-1 --tail=20

# Logs du frontend
docker logs finalprojectsimplon-frontend-1 --tail=20
```

### Messages clés dans les logs
```
✅ Connexion PostgreSQL réussie: db
❌ Connexion PostgreSQL échouée: [erreur]
🔄 Basculement automatique vers SQLite
🗄️ Base de données: SQLite (./bankreports.db)
🐘 Base de données: PostgreSQL (db)
```

## 🔧 Configuration Avancée

### Variables d'environnement
```bash
# Dans docker-compose.yml ou .env
USE_POSTGRES=true           # Active le système hybride
POSTGRES_HOST=db            # Host PostgreSQL
POSTGRES_DB=bankreports     # Nom de la base
POSTGRES_USER=postgres      # Utilisateur
POSTGRES_PASSWORD=postgres  # Mot de passe
POSTGRES_PORT=5432          # Port
```

### Forcer une base spécifique

#### Forcer SQLite uniquement
```bash
# Temporairement
USE_POSTGRES=false docker-compose up

# Ou modifier docker-compose.yml
environment:
  - USE_POSTGRES=false
```

#### Forcer PostgreSQL uniquement (sans fallback)
```python
# Dans src/db/database.py, remplacer la logique par :
if all([POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD]):
    # PostgreSQL obligatoire
    SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
else:
    raise Exception("PostgreSQL requis mais configuration manquante")
```

## 🛠️ Maintenance

### Sauvegarde des données

#### PostgreSQL
```bash
# Sauvegarde complète
docker exec finalprojectsimplon-db-1 pg_dump -U postgres -d bankreports > backup_$(date +%Y%m%d).sql

# Restauration
cat backup_20240513.sql | docker exec -i finalprojectsimplon-db-1 psql -U postgres -d bankreports
```

#### SQLite
```bash
# Sauvegarde
cp bankreports.db backup_bankreports_$(date +%Y%m%d).db

# Restauration
cp backup_bankreports_20240513.db bankreports.db
```

### Migration entre bases
```bash
# Exporter de PostgreSQL vers SQLite
docker exec finalprojectsimplon-db-1 pg_dump -U postgres -d bankreports --data-only --inserts > data_export.sql

# Note: Nécessite adaptation manuelle des requêtes pour SQLite
```

### Nettoyage des données
```bash
# Vider une table (attention : irréversible)
docker exec -it finalprojectsimplon-db-1 psql -U postgres -d bankreports -c "TRUNCATE TABLE bank_data;"

# Ou via l'API
curl -X DELETE http://localhost:8000/api/bank-data -H "Authorization: Bearer YOUR_TOKEN"
```

## 🚨 Résolution de Problèmes

### Problème : API ne démarre pas
```bash
# 1. Vérifier les logs
docker logs finalprojectsimplon-api-1

# 2. Redémarrer avec logs en temps réel
docker restart finalprojectsimplon-api-1
docker logs -f finalprojectsimplon-api-1

# 3. Forcer SQLite si PostgreSQL problématique
docker stop finalprojectsimplon-db-1
docker restart finalprojectsimplon-api-1
```

### Problème : PostgreSQL ne démarre pas
```bash
# 1. Vérifier l'espace disque
df -h

# 2. Vérifier les logs PostgreSQL
docker logs finalprojectsimplon-db-1

# 3. Redémarrer complètement
docker-compose down
docker-compose up -d db
```

### Problème : Données incohérentes entre bases
```bash
# 1. Vérifier quelle base est utilisée
python check_database_status.py

# 2. Synchroniser les migrations
python -m src.scripts.apply_migrations

# 3. En cas de problème, recréer les tables
python -m src.scripts.init_db --recreate
```

## 📚 Bonnes Pratiques

### Développement
1. **Toujours vérifier** quelle base est utilisée avant les tests
2. **Tester le fallback** régulièrement
3. **Surveiller les logs** pour les erreurs de connexion
4. **Utiliser SQLite** pour les tests unitaires (rapidité)

### Production
1. **Monitorer PostgreSQL** activement
2. **Avoir des sauvegardes** régulières
3. **Tester la procédure de fallback** en préproduction
4. **Alertes** sur les basculements SQLite non planifiés

### Débogage
1. **Logs verbeux** en mode debug
2. **Tests de charge** sur les deux bases
3. **Métriques de performance** comparatives
4. **Documentation des incidents** de fallback

---

> 💡 **Astuce** : Le script `check_database_status.py` est votre meilleur ami pour comprendre l'état actuel du système de bases de données ! 
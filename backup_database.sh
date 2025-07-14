#!/bin/bash
# Script de backup automatique pour la base consolidée
# À exécuter quotidiennement avec cron

BACKUP_DIR="./backups"
DB_FILE="./bankreports.db"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/bankreports_backup_$DATE.db"

# Créer le dossier de backup s'il n'existe pas
mkdir -p "$BACKUP_DIR"

# Copier la base de données
cp "$DB_FILE" "$BACKUP_FILE"

# Garder seulement les 7 derniers backups
ls -t "$BACKUP_DIR"/bankreports_backup_*.db | tail -n +8 | xargs -r rm

echo "Backup créé: $BACKUP_FILE"

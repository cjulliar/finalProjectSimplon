#!/bin/bash
# Script pour initialiser l'application complète avec Docker Compose

set -e  # Arrêter le script en cas d'erreur

echo "=== Initialisation du projet ==="

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "Docker n'est pas installé. Veuillez l'installer avant de continuer."
    exit 1
fi

# Vérifier que Docker Compose est installé
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose n'est pas installé. Veuillez l'installer avant de continuer."
    exit 1
fi

# Installer les dépendances Python
echo "Installation des dépendances Python..."
pip install -r requirements.txt

# Initialiser la base de données avec Alembic
echo "Initialisation de la base de données avec Alembic..."
python -m src.scripts.init_db --create-admin

# Construire les images Docker
echo "Construction des images Docker..."
docker-compose build

# Lancer les conteneurs Docker
echo "Lancement des conteneurs Docker..."
docker-compose up -d

echo "=== Initialisation terminée ==="
echo "L'API est disponible à l'adresse : http://localhost:8000"
echo "Documentation de l'API : http://localhost:8000/docs"
echo "Frontend : http://localhost:8080"
echo "Prometheus : http://localhost:9090"
echo "Grafana : http://localhost:3000"
echo ""
echo "Pour arrêter l'application, exécutez : docker-compose down" 
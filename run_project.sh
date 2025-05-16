#!/bin/bash
# Script pour démarrer l'application complète avec Docker Compose

set -e  # Arrêter le script en cas d'erreur

echo "=== Démarrage du projet ==="

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "Docker n'est pas installé. Veuillez l'installer avant de continuer."
    exit 1
fi

# Déterminer la commande Docker Compose à utiliser
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo "Docker Compose n'est pas installé. Veuillez l'installer avant de continuer."
    exit 1
fi

echo "Utilisation de la commande : $DOCKER_COMPOSE"

# Vérifier si les conteneurs sont déjà en cours d'exécution
if $DOCKER_COMPOSE ps | grep -q "Up"; then
    echo "Certains conteneurs sont déjà en cours d'exécution."
    echo "Voulez-vous les redémarrer ? (o/n)"
    read -r response
    if [[ "$response" =~ ^([oO][uU][iI]|[oO])$ ]]; then
        echo "Arrêt des conteneurs existants..."
        $DOCKER_COMPOSE down
    else
        echo "Opération annulée."
        exit 0
    fi
fi

# Lancer les conteneurs Docker
echo "Lancement des conteneurs Docker..."
$DOCKER_COMPOSE up -d

# Vérifier que tous les conteneurs sont en cours d'exécution
echo "Vérification de l'état des conteneurs..."
if $DOCKER_COMPOSE ps | grep -q "Exit"; then
    echo "ATTENTION: Certains conteneurs ne sont pas en cours d'exécution."
    $DOCKER_COMPOSE ps
else
    echo "Tous les conteneurs sont en cours d'exécution."
fi

echo "=== Démarrage terminé ==="
echo "L'API est disponible à l'adresse : http://localhost:8000"
echo "Documentation de l'API : http://localhost:8000/docs"
echo "Frontend : http://localhost:8080"
echo "Prometheus : http://localhost:9090"
echo "Grafana : http://localhost:3000"
echo "  - Identifiant : admin"
echo "  - Mot de passe : admin"
echo ""
echo "Pour arrêter l'application, exécutez : $DOCKER_COMPOSE down" 
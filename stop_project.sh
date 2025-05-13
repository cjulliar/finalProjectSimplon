#!/bin/bash

# Script d'arrêt du projet d'Automatisation des Rapports Bancaires
# Ce script arrête tous les services Docker en cours d'exécution

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher un message d'information
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Fonction pour afficher un message de succès
success() {
    echo -e "${GREEN}[SUCCÈS]${NC} $1"
}

# Fonction pour afficher une erreur
error() {
    echo -e "${RED}[ERREUR]${NC} $1"
}

# Vérifier si docker-compose ou docker compose est disponible
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

# Afficher un message de confirmation
echo -e "${YELLOW}Arrêt des services du projet...${NC}"

# Arrêter les conteneurs
info "Arrêt des conteneurs Docker..."
$DOCKER_COMPOSE down

if [ $? -ne 0 ]; then
    error "Erreur lors de l'arrêt des conteneurs."
    exit 1
fi

success "Tous les services ont été arrêtés avec succès."
echo ""
info "Pour redémarrer le projet, exécutez : ./run_project.sh" 
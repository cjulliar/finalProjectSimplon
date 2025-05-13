#!/bin/bash

# Script d'affichage des logs du projet d'Automatisation des Rapports Bancaires
# Ce script permet de consulter les logs des différents services

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Vérifier si docker-compose ou docker compose est disponible
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

# Fonction pour afficher le menu
show_menu() {
    echo -e "${GREEN}=== Affichage des logs ===${NC}"
    echo "1) Logs de l'API"
    echo "2) Logs du Frontend"
    echo "3) Logs de tous les services"
    echo "4) Quitter"
    echo ""
}

# Fonction pour afficher les logs d'un service spécifique
show_service_logs() {
    local service=$1
    local lines=$2
    
    echo -e "${YELLOW}Affichage des logs du service ${service}. Appuyez sur Ctrl+C pour quitter.${NC}"
    echo ""
    
    if [ -z "$lines" ]; then
        $DOCKER_COMPOSE logs -f $service
    else
        $DOCKER_COMPOSE logs --tail=$lines -f $service
    fi
}

# Fonction principale
main() {
    # Vérifier que les services sont en cours d'exécution
    if ! $DOCKER_COMPOSE ps &> /dev/null; then
        echo -e "${RED}[ERREUR]${NC} Les services ne semblent pas être en cours d'exécution."
        echo -e "${YELLOW}Exécutez d'abord ./run_project.sh pour démarrer les services.${NC}"
        exit 1
    fi
    
    # Demander combien de lignes afficher
    echo -e "${BLUE}[INFO]${NC} Combien de lignes de logs souhaitez-vous afficher ?"
    echo "Laissez vide pour afficher tous les logs ou entrez un nombre (ex: 50) :"
    read -p "> " lines_count
    
    while true; do
        clear
        show_menu
        read -p "Choisissez une option (1-4): " choice
        
        case $choice in
            1)
                show_service_logs "api" "$lines_count"
                ;;
            2)
                show_service_logs "frontend" "$lines_count"
                ;;
            3)
                echo -e "${YELLOW}Affichage des logs de tous les services. Appuyez sur Ctrl+C pour quitter.${NC}"
                echo ""
                
                if [ -z "$lines_count" ]; then
                    $DOCKER_COMPOSE logs -f
                else
                    $DOCKER_COMPOSE logs --tail=$lines_count -f
                fi
                ;;
            4)
                echo -e "${GREEN}Au revoir !${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Option invalide. Veuillez réessayer.${NC}"
                sleep 2
                ;;
        esac
    done
}

# Exécuter la fonction principale
main 
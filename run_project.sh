#!/bin/bash

# Script de lancement du projet d'Automatisation des Rapports Bancaires
# Ce script lance l'API, le frontend et effectue des vérifications de base

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

# Fonction pour afficher un avertissement
warning() {
    echo -e "${YELLOW}[ATTENTION]${NC} $1"
}

# Fonction pour afficher une erreur
error() {
    echo -e "${RED}[ERREUR]${NC} $1"
}

# Fonction pour vérifier si Docker est installé et en cours d'exécution
check_docker() {
    info "Vérification de Docker..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker n'est pas installé. Veuillez installer Docker et réessayer."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker n'est pas en cours d'exécution. Veuillez démarrer Docker et réessayer."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose n'est pas installé. Veuillez installer Docker Compose et réessayer."
        exit 1
    fi
    
    success "Docker est correctement configuré."
}

# Fonction pour démarrer les services avec Docker Compose
start_services() {
    info "Démarrage des services avec Docker Compose..."
    
    # Vérifier si docker-compose ou docker compose est disponible
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        DOCKER_COMPOSE="docker compose"
    fi
    
    # Arrêter les conteneurs existants pour éviter les conflits
    $DOCKER_COMPOSE down
    
    # Démarrer les services
    $DOCKER_COMPOSE up -d
    
    if [ $? -ne 0 ]; then
        error "Échec du démarrage des services."
        exit 1
    fi
    
    success "Services démarrés avec succès."
}

# Fonction pour vérifier si les services sont en cours d'exécution
check_services() {
    info "Vérification des services..."
    
    # Attendre que les services soient prêts (augmenté à 10 secondes pour donner plus de temps au démarrage)
    info "Attente du démarrage des services (10 secondes)..."
    sleep 10
    
    # Vérifier si docker-compose ou docker compose est disponible
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        DOCKER_COMPOSE="docker compose"
    fi
    
    # Vérifier l'état des services
    $DOCKER_COMPOSE ps
    
    # Vérifier l'API
    info "Vérification de l'API..."
    if curl -s http://localhost:8000/health | grep -q "ok"; then
        success "L'API est opérationnelle."
    else
        warning "L'API ne répond pas correctement. Vérifiez les logs pour plus d'informations."
        info "Affichage des dernières lignes de logs de l'API..."
        $DOCKER_COMPOSE logs --tail=20 api
    fi
    
    # Vérifier le frontend
    info "Vérification du frontend Django..."
    if curl -s -I http://localhost:8080 | grep -q "302 Found"; then
        success "Le frontend Django est opérationnel (redirection vers la page de connexion)."
    else
        warning "Le frontend Django ne répond pas correctement. Vérifiez les logs pour plus d'informations."
        info "Affichage des dernières lignes de logs du frontend..."
        $DOCKER_COMPOSE logs --tail=20 frontend
    fi
}

# Fonction pour générer des données de test
generate_test_data() {
    info "Génération de données de test..."
    
    # Exécuter le script de génération de données de test dans le conteneur API
    docker compose exec api python -m src.scripts.generate_test_data --entries 150
    
    if [ $? -ne 0 ]; then
        warning "Échec de la génération des données de test."
    else
        success "Données de test générées avec succès."
    fi
}

# Fonction pour créer une analyse IA de test
create_test_analysis() {
    info "Création d'une analyse IA de test..."
    
    # Obtenir un token d'authentification
    TOKEN=$(curl -s -X POST "http://localhost:8000/api/token" -d "username=admin&password=admin123" -H "Content-Type: application/x-www-form-urlencoded" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    
    if [ -z "$TOKEN" ]; then
        warning "Impossible d'obtenir un token d'authentification. L'analyse IA ne sera pas créée."
        return
    fi
    
    # Créer une analyse IA
    RESPONSE=$(curl -s -X POST "http://localhost:8000/api/ai/analyze" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"start_date": null, "end_date": null, "include_visualizations": true}')
    
    if echo "$RESPONSE" | grep -q "report"; then
        success "Analyse IA créée avec succès."
    else
        warning "Échec de la création de l'analyse IA."
        echo "$RESPONSE"
    fi
}

# Fonction pour ouvrir le navigateur
open_browser() {
    info "Tentative d'ouverture du navigateur..."
    
    # Détection du système d'exploitation
    case "$(uname -s)" in
        Darwin)  # macOS
            open "http://localhost:8080"
            ;;
        Linux)
            if command -v xdg-open &> /dev/null; then
                xdg-open "http://localhost:8080"
            else
                warning "Impossible d'ouvrir automatiquement le navigateur. Veuillez ouvrir http://localhost:8080 manuellement."
            fi
            ;;
        CYGWIN*|MINGW*|MSYS*)  # Windows
            start "http://localhost:8080"
            ;;
        *)
            warning "Système d'exploitation non reconnu. Veuillez ouvrir http://localhost:8080 manuellement."
            ;;
    esac
}

# Fonction pour afficher les informations d'accès
show_access_info() {
    echo ""
    echo -e "${GREEN}=== Informations d'accès ===${NC}"
    echo "API: http://localhost:8000"
    echo "  - Documentation Swagger: http://localhost:8000/docs"
    echo "  - Documentation ReDoc: http://localhost:8000/redoc"
    echo ""
    echo "Frontend Django: http://localhost:8080"
    echo "  - Identifiants par défaut: admin / admin123"
    echo "  - Sections disponibles:"
    echo "    * Tableau de bord: http://localhost:8080/"
    echo "    * Données bancaires: http://localhost:8080/bank-data/"
    echo "    * Rapports IA: http://localhost:8080/ai-reports/"
    echo ""
    echo -e "${YELLOW}Pour voir les logs:${NC}"
    echo "  - API: docker compose logs -f api"
    echo "  - Frontend: docker compose logs -f frontend"
    echo "  - Ou utilisez le script: ./show_logs.sh"
    echo ""
    echo -e "${YELLOW}Pour arrêter les services:${NC}"
    echo "  - docker compose down"
    echo "  - Ou utilisez le script: ./stop_project.sh"
    echo ""
}

# Fonction principale
main() {
    echo -e "${GREEN}=== Démarrage du projet d'Automatisation des Rapports Bancaires ===${NC}"
    
    # Vérifier Docker
    check_docker
    
    # Démarrer les services
    start_services
    
    # Vérifier les services
    check_services
    
    # Demander si l'utilisateur souhaite générer des données de test
    echo ""
    read -p "Voulez-vous générer des données de test? (o/n): " generate_data
    if [[ $generate_data == "o" || $generate_data == "O" ]]; then
        generate_test_data
        
        # Demander si l'utilisateur souhaite créer une analyse IA de test
        echo ""
        read -p "Voulez-vous créer une analyse IA de test? (o/n): " create_analysis
        if [[ $create_analysis == "o" || $create_analysis == "O" ]]; then
            create_test_analysis
        fi
    fi
    
    # Demander si l'utilisateur souhaite ouvrir le navigateur
    echo ""
    read -p "Voulez-vous ouvrir le frontend Django dans votre navigateur? (o/n): " open_browser_choice
    if [[ $open_browser_choice == "o" || $open_browser_choice == "O" ]]; then
        open_browser
    fi
    
    # Afficher les informations d'accès
    show_access_info
}

# Exécuter la fonction principale
main 
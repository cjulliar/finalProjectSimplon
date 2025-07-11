#!/bin/bash

# Script d'installation et de lancement du projet bancaire intelligent
# Auteur: Cyril Julliard
# Date: $(date)

echo "🏦 INSTALLATION ET LANCEMENT DU PROJET BANCAIRE INTELLIGENT"
echo "=========================================================="

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier les prérequis
check_prerequisites() {
    print_status "Vérification des prérequis..."
    
    # Vérifier Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    
    # Vérifier pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    
    # Vérifier Docker (optionnel)
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        DOCKER_AVAILABLE=true
        print_success "Docker et Docker Compose sont disponibles"
    else
        DOCKER_AVAILABLE=false
        print_warning "Docker n'est pas disponible. Utilisation du mode local uniquement."
    fi
    
    print_success "Prérequis vérifiés"
}

# Installation des dépendances
install_dependencies() {
    print_status "Installation des dépendances..."
    
    # Créer l'environnement virtuel
    if [ ! -d "venv" ]; then
        print_status "Création de l'environnement virtuel..."
        python3 -m venv venv
    fi
    
    # Activer l'environnement virtuel
    source venv/bin/activate
    
    # Mettre à jour pip
    pip install --upgrade pip
    
    # Installer les dépendances principales
    print_status "Installation des dépendances Python..."
    pip install -r requirements.txt
    
    # Installer les dépendances du frontend
    print_status "Installation des dépendances Django..."
    pip install -r frontend/requirements.txt
    
    print_success "Dépendances installées"
}

# Configuration de la base de données
setup_database() {
    print_status "Configuration de la base de données..."
    
    # Copier la base de données SQLite si elle n'existe pas
    if [ ! -f "frontend/bankreports.db" ] && [ -f "bankreports.db" ]; then
        print_status "Copie de la base de données..."
        cp bankreports.db frontend/bankreports.db
    fi
    
    # Créer les migrations Django si nécessaire
    cd frontend
    python manage.py makemigrations --noinput
    python manage.py migrate --noinput
    cd ..
    
    print_success "Base de données configurée"
}

# Création des utilisateurs de test
create_test_users() {
    print_status "Création des utilisateurs de test..."
    
    # Vérifier si les scripts de création d'utilisateurs existent
    if [ -f "create_users.py" ]; then
        python create_users.py
    fi
    
    if [ -f "create_director_users.py" ]; then
        python create_director_users.py
    fi
    
    print_success "Utilisateurs de test créés"
}

# Lancement avec Docker
launch_with_docker() {
    print_status "Lancement avec Docker..."
    
    # Construire et démarrer les conteneurs
    docker-compose up -d --build
    
    # Attendre que les services soient prêts
    print_status "Attente du démarrage des services..."
    sleep 30
    
    print_success "Services Docker démarrés"
}

# Lancement en mode local
launch_local() {
    print_status "Lancement en mode local..."
    
    # Arrêter les processus existants
    pkill -f "python.*manage.py.*runserver.*8080" 2>/dev/null || true
    pkill -f "uvicorn.*main:app.*8000" 2>/dev/null || true
    pkill -f "uvicorn.*main:app.*8001" 2>/dev/null || true
    
    sleep 2
    
    # Démarrer l'API FastAPI
    print_status "Démarrage de l'API FastAPI..."
    cd src
    python -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload &
    API_PID=$!
    cd ..
    sleep 3
    
    # Démarrer le frontend Django
    print_status "Démarrage du frontend Django..."
    cd frontend
    python manage.py runserver 0.0.0.0:8080 &
    DJANGO_PID=$!
    cd ..
    sleep 3
    
    # Sauvegarder les PIDs
    echo $API_PID > .api_pid
    echo $DJANGO_PID > .django_pid
    
    print_success "Services locaux démarrés"
}

# Affichage des informations de connexion
show_connection_info() {
    echo ""
    echo "🎉 PROJET INSTALLÉ ET DÉMARRÉ AVEC SUCCÈS !"
    echo "============================================"
    echo ""
    
    if [ "$DOCKER_AVAILABLE" = true ] && [ "$1" = "docker" ]; then
        echo "🐳 Mode Docker :"
        echo "   • Frontend Django: http://localhost:8080"
        echo "   • API FastAPI: http://localhost:8000"
        echo "   • Documentation API: http://localhost:8000/docs"
        echo "   • Monitoring Prometheus: http://localhost:9090"
        echo "   • Dashboard Grafana: http://localhost:3000 (admin/admin)"
    else
        echo "💻 Mode Local :"
        echo "   • Frontend Django: http://localhost:8080"
        echo "   • API FastAPI: http://localhost:8001"
        echo "   • Documentation API: http://localhost:8001/docs"
    fi
    
    echo ""
    echo "🔐 Identifiants de test :"
    echo "   • Email: cyrjulliard@gmail.com"
    echo "   • Mot de passe: directeur123"
    echo "   • Exemples d'utilisateurs:"
    echo "     - directeurBanqueA"
    echo "     - directeurBanqueBG"
    echo "     - directeurBanqueC"
    echo ""
    echo "📊 Fonctionnalités disponibles :"
    echo "   • Dashboard personnalisé par agence"
    echo "   • 74 directeurs d'agence configurés"
    echo "   • Données bancaires enrichies"
    echo "   • Rapports automatiques"
    echo "   • Analyses IA"
    echo ""
    
    if [ "$DOCKER_AVAILABLE" = true ] && [ "$1" = "docker" ]; then
        echo "🛑 Pour arrêter le projet : docker-compose down"
    else
        echo "🛑 Pour arrêter le projet : ./stop_project.sh"
    fi
    
    echo "📝 Logs disponibles dans les fichiers .log"
    echo ""
}

# Fonction principale
main() {
    # Vérifier qu'on est dans le bon répertoire
    if [ ! -f "docker-compose.yml" ]; then
        print_error "Ce script doit être exécuté depuis la racine du projet"
        exit 1
    fi
    
    # Vérifier les prérequis
    check_prerequisites
    
    # Installation des dépendances
    install_dependencies
    
    # Configuration de la base de données
    setup_database
    
    # Création des utilisateurs de test
    create_test_users
    
    # Choix du mode de lancement
    if [ "$DOCKER_AVAILABLE" = true ]; then
        echo ""
        echo "Choisissez le mode de lancement :"
        echo "1) Docker (recommandé)"
        echo "2) Local"
        echo ""
        read -p "Votre choix (1 ou 2) : " choice
        
        case $choice in
            1)
                launch_with_docker
                show_connection_info "docker"
                ;;
            2)
                launch_local
                show_connection_info "local"
                ;;
            *)
                print_error "Choix invalide. Utilisation du mode local."
                launch_local
                show_connection_info "local"
                ;;
        esac
    else
        launch_local
        show_connection_info "local"
    fi
}

# Exécuter la fonction principale
main 
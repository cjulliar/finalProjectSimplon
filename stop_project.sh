#!/bin/bash

# Script d'arrêt du projet bancaire intelligent
# Auteur: Cyril Julliard
# Date: $(date)

echo "🛑 ARRÊT DU PROJET BANCAIRE INTELLIGENT"
echo "======================================"

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

# Vérifier si on est dans le bon répertoire
if [ ! -f "docker-compose.yml" ]; then
    print_error "Ce script doit être exécuté depuis la racine du projet"
    exit 1
fi

# Arrêter les processus par PID si les fichiers existent
print_status "Arrêt des processus par PID..."

if [ -f ".api_pid" ]; then
    API_PID=$(cat .api_pid)
    if kill -0 $API_PID 2>/dev/null; then
        print_status "Arrêt de l'API FastAPI (PID: $API_PID)..."
        kill $API_PID
        sleep 2
        if kill -0 $API_PID 2>/dev/null; then
            print_warning "Force kill de l'API FastAPI..."
            kill -9 $API_PID
        fi
        print_success "API FastAPI arrêtée"
    else
        print_warning "API FastAPI déjà arrêtée"
    fi
    rm -f .api_pid
else
    print_warning "Fichier PID API non trouvé"
fi

if [ -f ".django_pid" ]; then
    DJANGO_PID=$(cat .django_pid)
    if kill -0 $DJANGO_PID 2>/dev/null; then
        print_status "Arrêt du frontend Django (PID: $DJANGO_PID)..."
        kill $DJANGO_PID
        sleep 2
        if kill -0 $DJANGO_PID 2>/dev/null; then
            print_warning "Force kill du frontend Django..."
            kill -9 $DJANGO_PID
        fi
        print_success "Frontend Django arrêté"
    else
        print_warning "Frontend Django déjà arrêté"
    fi
    rm -f .django_pid
else
    print_warning "Fichier PID Django non trouvé"
fi

if [ -f ".api_alt_pid" ]; then
    API_ALT_PID=$(cat .api_alt_pid)
    if kill -0 $API_ALT_PID 2>/dev/null; then
        print_status "Arrêt de l'API alternative (PID: $API_ALT_PID)..."
        kill $API_ALT_PID
        sleep 2
        if kill -0 $API_ALT_PID 2>/dev/null; then
            print_warning "Force kill de l'API alternative..."
            kill -9 $API_ALT_PID
        fi
        print_success "API alternative arrêtée"
    else
        print_warning "API alternative déjà arrêtée"
    fi
    rm -f .api_alt_pid
else
    print_warning "Fichier PID API alternative non trouvé"
fi

# Arrêter tous les processus Python liés au projet
print_status "Arrêt des processus Python liés au projet..."

# Arrêter les serveurs Django
pkill -f "python.*manage.py.*runserver.*8080" 2>/dev/null || true
pkill -f "python.*manage.py.*runserver.*0.0.0.0:8080" 2>/dev/null || true

# Arrêter les serveurs uvicorn
pkill -f "uvicorn.*main:app.*8000" 2>/dev/null || true
pkill -f "uvicorn.*main:app.*8001" 2>/dev/null || true
pkill -f "uvicorn.*main:app.*0.0.0.0:8000" 2>/dev/null || true
pkill -f "uvicorn.*main:app.*0.0.0.0:8001" 2>/dev/null || true

# Arrêter les processus Celery si présents
pkill -f "celery.*worker" 2>/dev/null || true
pkill -f "celery.*beat" 2>/dev/null || true

# Vérifier que les ports sont libérés
print_status "Vérification de la libération des ports..."

check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        print_warning "Le port $port est encore utilisé"
        return 1
    else
        print_success "Port $port libéré"
        return 0
    fi
}

sleep 3

check_port 8080
check_port 8000
check_port 8001

# Nettoyer les fichiers temporaires
print_status "Nettoyage des fichiers temporaires..."
rm -f .api_pid .django_pid .api_alt_pid 2>/dev/null || true
rm -f *.log 2>/dev/null || true

# Arrêter Docker si utilisé
if command -v docker &> /dev/null; then
    print_status "Vérification des conteneurs Docker..."
    if docker ps --filter "name=finalprojectsimplon" --format "table {{.Names}}\t{{.Status}}" | grep -q "finalprojectsimplon"; then
        print_status "Arrêt des conteneurs Docker..."
        docker-compose down 2>/dev/null || true
        print_success "Conteneurs Docker arrêtés"
    else
        print_status "Aucun conteneur Docker actif"
    fi
fi

# Afficher le résumé
echo ""
echo "✅ PROJET ARRÊTÉ AVEC SUCCÈS !"
echo "=============================="
echo ""
echo "🛑 Services arrêtés :"
echo "   • Frontend Django (port 8080)"
echo "   • API FastAPI (port 8001)"
echo "   • API Alternative (port 8000)"
echo "   • Conteneurs Docker (si présents)"
echo ""
echo "🧹 Nettoyage effectué :"
echo "   • Fichiers PID supprimés"
echo "   • Logs temporaires nettoyés"
echo "   • Ports libérés"
echo ""
echo "🚀 Pour relancer le projet : ./start_project.sh"
echo ""

print_success "Arrêt terminé !" 
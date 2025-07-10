#!/bin/bash

# Script de lancement du projet bancaire intelligent
# Auteur: Cyril Julliard
# Date: $(date)

echo "🏦 LANCEMENT DU PROJET BANCAIRE INTELLIGENT"
echo "=========================================="

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

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    print_warning "Environnement virtuel non trouvé. Création..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Arrêter les processus existants sur les ports utilisés
print_status "Arrêt des processus existants..."
pkill -f "python.*manage.py.*runserver.*8080" 2>/dev/null || true
pkill -f "uvicorn.*main:app.*8000" 2>/dev/null || true
pkill -f "uvicorn.*main:app.*8001" 2>/dev/null || true

# Attendre que les ports soient libérés
sleep 2

# Vérifier les ports
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        print_error "Le port $port est déjà utilisé"
        return 1
    fi
    return 0
}

print_status "Vérification des ports..."
check_port 8080 || exit 1
check_port 8000 || exit 1
check_port 8001 || exit 1

# Démarrer les services

print_status "Démarrage des services..."

# 1. Démarrer l'API FastAPI (port 8001)
print_status "Démarrage de l'API FastAPI..."
cd src
python -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload &
API_PID=$!
cd ..
sleep 3

# Vérifier que l'API est démarrée
if curl -s http://localhost:8001/health >/dev/null 2>&1; then
    print_success "API FastAPI démarrée sur http://localhost:8001"
else
    print_warning "API FastAPI en cours de démarrage..."
fi

# 2. Démarrer le frontend Django (port 8080)
print_status "Démarrage du frontend Django..."
cd frontend
python manage.py runserver 0.0.0.0:8080 &
DJANGO_PID=$!
cd ..
sleep 3

# Vérifier que Django est démarré
if curl -s http://localhost:8080/login/ >/dev/null 2>&1; then
    print_success "Frontend Django démarré sur http://localhost:8080"
else
    print_warning "Frontend Django en cours de démarrage..."
fi

# 3. Démarrer l'API alternative (port 8000) si nécessaire
print_status "Démarrage de l'API alternative..."
cd src
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
API_ALT_PID=$!
cd ..
sleep 2

# Sauvegarder les PIDs
echo $API_PID > .api_pid
echo $DJANGO_PID > .django_pid
echo $API_ALT_PID > .api_alt_pid

# Afficher les informations de connexion
echo ""
echo "🎉 PROJET DÉMARRÉ AVEC SUCCÈS !"
echo "================================"
echo ""
echo "🌐 URLs d'accès :"
echo "   • Frontend Django: http://localhost:8080"
echo "   • API FastAPI: http://localhost:8001"
echo "   • API Alternative: http://localhost:8000"
echo "   • Documentation API: http://localhost:8001/docs"
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
echo "🛑 Pour arrêter le projet : ./stop_project.sh"
echo "📝 Logs disponibles dans les fichiers .log"
echo ""

# Attendre que tous les services soient prêts
print_status "Attente de la disponibilité des services..."
sleep 5

# Test final de connectivité
print_status "Test de connectivité..."
if curl -s http://localhost:8080/login/ >/dev/null 2>&1; then
    print_success "✅ Frontend accessible"
else
    print_warning "⚠️  Frontend en cours de démarrage"
fi

if curl -s http://localhost:8001/health >/dev/null 2>&1; then
    print_success "✅ API accessible"
else
    print_warning "⚠️  API en cours de démarrage"
fi

echo ""
print_success "Projet lancé avec succès !"
echo "Les services continuent de démarrer en arrière-plan."
echo "Vérifiez les URLs dans quelques secondes." 
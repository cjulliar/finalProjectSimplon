#!/bin/bash

# Script de lancement pour le développement local
# Auteur: Cyril Julliard

echo "💻 LANCEMENT EN MODE DÉVELOPPEMENT LOCAL"
echo "========================================"

# Couleurs pour les messages
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

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

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier qu'on est dans le bon répertoire
if [ ! -f "docker-compose.yml" ]; then
    print_error "Ce script doit être exécuté depuis la racine du projet"
    exit 1
fi

# Créer l'environnement virtuel si nécessaire
if [ ! -d "venv" ]; then
    print_status "Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances si nécessaire
if [ ! -f "venv/pyvenv.cfg" ]; then
    print_status "Installation des dépendances..."
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r frontend/requirements.txt
fi

# Arrêter les processus existants
print_status "Arrêt des processus existants..."
pkill -f "python.*manage.py.*runserver.*8080" 2>/dev/null || true
pkill -f "uvicorn.*main:app.*8001" 2>/dev/null || true

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
check_port 8001 || exit 1

# Configuration de la base de données
print_status "Configuration de la base de données..."
if [ ! -f "frontend/bankreports.db" ] && [ -f "bankreports.db" ]; then
    cp bankreports.db frontend/bankreports.db
fi

cd frontend
python manage.py makemigrations --noinput
python manage.py migrate --noinput
cd ..

# Créer les utilisateurs de test si nécessaire
if [ -f "create_users.py" ]; then
    print_status "Création des utilisateurs de test..."
    python create_users.py
fi

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

# Attendre que les services soient prêts
print_status "Attente de la disponibilité des services..."
sleep 5

# Test de connectivité
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
echo "🎉 PROJET DÉMARRÉ EN MODE DÉVELOPPEMENT !"
echo "=========================================="
echo ""
echo "🌐 URLs d'accès :"
echo "   • Frontend Django: http://localhost:8080"
echo "   • API FastAPI: http://localhost:8001"
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
echo "🔄 Mode développement avec rechargement automatique activé"
echo "" 
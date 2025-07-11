#!/bin/bash

# Script de lancement rapide avec Docker
# Auteur: Cyril Julliard

echo "🚀 LANCEMENT RAPIDE DU PROJET BANCAIRE INTELLIGENT"
echo "=================================================="

# Couleurs pour les messages
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
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

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Arrêter les conteneurs existants
print_status "Arrêt des conteneurs existants..."
docker-compose down 2>/dev/null || true

# Construire et démarrer
print_status "Construction et démarrage des conteneurs..."
docker-compose up -d --build

# Attendre que les services soient prêts
print_status "Attente du démarrage des services..."
sleep 30

# Vérifier que les services sont accessibles
print_status "Vérification des services..."

# Test de l'API
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    print_success "✅ API FastAPI accessible"
else
    print_warning "⚠️  API en cours de démarrage..."
fi

# Test du frontend
if curl -s http://localhost:8080/login/ >/dev/null 2>&1; then
    print_success "✅ Frontend Django accessible"
else
    print_warning "⚠️  Frontend en cours de démarrage..."
fi

echo ""
echo "🎉 PROJET DÉMARRÉ AVEC SUCCÈS !"
echo "================================"
echo ""
echo "🌐 URLs d'accès :"
echo "   • Frontend Django: http://localhost:8080"
echo "   • API FastAPI: http://localhost:8000"
echo "   • Documentation API: http://localhost:8000/docs"
echo "   • Monitoring Prometheus: http://localhost:9090"
echo "   • Dashboard Grafana: http://localhost:3000 (admin/admin)"
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
echo "🛑 Pour arrêter le projet : docker-compose down"
echo "📊 Pour voir les logs : docker-compose logs -f"
echo "🔄 Pour redémarrer : docker-compose restart"
echo "" 
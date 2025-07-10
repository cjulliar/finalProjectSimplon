#!/bin/bash
# Script pour lancer l'environnement Docker complet avec PostgreSQL

echo "🐳 DÉMARRAGE ENVIRONNEMENT DOCKER COMPLET"
echo "========================================"

# Fonction pour nettoyer à la sortie
cleanup() {
    echo ""
    echo "🛑 Arrêt des conteneurs Docker..."
    docker-compose down
    echo "✅ Conteneurs arrêtés"
    exit 0
}

# Capturer Ctrl+C
trap cleanup SIGINT SIGTERM

# Vérifier Docker Desktop
echo "🔍 Vérification Docker Desktop..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker Desktop n'est pas démarré"
    echo "💡 Démarrage automatique de Docker Desktop..."
    open -a Docker
    echo "⏳ Attente démarrage Docker (45 secondes)..."
    sleep 45
    
    # Vérification après attente
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker Desktop toujours non accessible"
        echo "🔧 Veuillez démarrer Docker Desktop manuellement et relancer ce script"
        exit 1
    fi
fi
echo "✅ Docker Desktop actif"

# Nettoyer les anciens conteneurs
echo "🧹 Nettoyage des anciens conteneurs..."
docker-compose down --volumes --remove-orphans

# Construire et lancer les services
echo "🏗️  Construction et démarrage des services..."
docker-compose up --build -d

# Attendre que PostgreSQL soit prêt
echo "⏳ Attente PostgreSQL (30 secondes)..."
sleep 30

# Vérifier les services
echo ""
echo "🔍 VÉRIFICATION DES SERVICES"
echo "=============================="

# Test PostgreSQL
if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ PostgreSQL: Opérationnel (port 5432)"
else
    echo "⚠️  PostgreSQL: En cours de démarrage..."
fi

# Test Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: Opérationnel (port 6379)"
else
    echo "⚠️  Redis: En cours de démarrage..."
fi

# Test API
sleep 10
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API FastAPI: http://localhost:8000 (Opérationnelle)"
    echo "📚 Documentation: http://localhost:8000/docs"
else
    echo "⚠️  API FastAPI: En cours de démarrage..."
fi

# Test Frontend
if curl -s http://localhost:8080/ > /dev/null; then
    echo "✅ Frontend Django: http://localhost:8080 (Opérationnel)"
    echo "⚙️  Dashboard Celery: http://localhost:8080/celery/"
else
    echo "⚠️  Frontend Django: En cours de démarrage..."
fi

# Test Celery
if curl -s http://localhost:8000/api/celery/status > /dev/null; then
    echo "✅ Celery: Opérationnel avec Redis"
else
    echo "⚠️  Celery: En cours de démarrage..."
fi

# Monitoring services
echo "📊 Grafana: http://localhost:3000 (admin/admin)"
echo "🔍 Prometheus: http://localhost:9090"

echo ""
echo "🎯 ENVIRONNEMENT DOCKER PRÊT !"
echo "=============================="
echo "🌐 Frontend: http://localhost:8080"
echo "📊 API: http://localhost:8000"
echo "📚 Documentation: http://localhost:8000/docs"
echo "⚙️  Dashboard Celery: http://localhost:8080/celery/"
echo "🗄️  PostgreSQL: localhost:5432 (postgres/postgres/bankreports)"
echo "🚀 Redis: localhost:6379"
echo "📊 Grafana: http://localhost:3000 (admin/admin)"
echo "🔍 Prometheus: http://localhost:9090"
echo ""
echo "🔑 IDENTIFIANTS DE CONNEXION:"
echo "👤 Username: admin"
echo "🔒 Password: hBtH_apEj3dP_baa"
echo "📧 Email: admin@example.com"
echo ""
echo "💡 Appuyez sur Ctrl+C pour arrêter tous les services"
echo "📋 Logs en temps réel: docker-compose logs -f"
echo ""

# Garder le script en vie et afficher les logs
docker-compose logs -f 
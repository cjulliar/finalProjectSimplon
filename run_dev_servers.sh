#!/bin/bash
# Script pour lancer les serveurs de développement avec gestion Docker automatique

echo "🚀 DÉMARRAGE DU SYSTÈME DE RAPPORTS BANCAIRES"
echo "=============================================="

# Fonction pour nettoyer les processus à la sortie
cleanup() {
    echo ""
    echo "🛑 Arrêt des serveurs..."
    kill $API_PID $DJANGO_PID 2>/dev/null
    wait $API_PID $DJANGO_PID 2>/dev/null
    echo "✅ Serveurs arrêtés"
    exit 0
}

# Capturer Ctrl+C
trap cleanup SIGINT SIGTERM

# Vérifier l'environnement virtuel
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Environnement virtuel non activé. Activation..."
    source venv/bin/activate
fi

# === NOUVELLE GESTION DOCKER/POSTGRESQL ===
echo "🔍 Détection de l'environnement..."

# Fonction pour tester la connexion PostgreSQL
test_postgres_connection() {
    python3 -c "
import psycopg2
import sys
try:
    conn = psycopg2.connect(
        host='localhost',
        database='bankreports', 
        user='postgres',
        password='postgres',
        connect_timeout=3
    )
    conn.close()
    sys.exit(0)
except:
    sys.exit(1)
" 2>/dev/null
}

# Détecter et configurer PostgreSQL
POSTGRES_AVAILABLE=false

if test_postgres_connection; then
    echo "✅ PostgreSQL détecté et accessible"
    POSTGRES_AVAILABLE=true
else
    echo "❌ PostgreSQL non accessible"
    
    # Vérifier Docker Desktop
    if docker info > /dev/null 2>&1; then
        echo "✅ Docker Desktop actif"
        echo "🐳 Démarrage de PostgreSQL via Docker..."
        
        # Lancer uniquement les services de base (db + redis)
        docker-compose up -d db redis
        
        echo "⏳ Attente PostgreSQL (30 secondes)..."
        sleep 30
        
        # Test après démarrage Docker
        if test_postgres_connection; then
            echo "✅ PostgreSQL démarré avec succès via Docker"
            POSTGRES_AVAILABLE=true
        else
            echo "⚠️  PostgreSQL toujours inaccessible"
        fi
    else
        echo "❌ Docker Desktop non accessible"
        echo "💡 Démarrage automatique de Docker Desktop..."
        open -a Docker
        echo "⏳ Attente Docker Desktop (45 secondes)..."
        sleep 45
        
        if docker info > /dev/null 2>&1; then
            echo "✅ Docker Desktop démarré"
            echo "🐳 Démarrage PostgreSQL..."
            docker-compose up -d db redis
            sleep 30
            
            if test_postgres_connection; then
                echo "✅ PostgreSQL accessible après démarrage Docker"
                POSTGRES_AVAILABLE=true
            else
                echo "⚠️  PostgreSQL toujours non accessible"
            fi
        else
            echo "⚠️  Docker Desktop toujours non accessible"
            echo "🔄 Utilisation de SQLite en fallback"
        fi
    fi
fi

# Configuration des variables d'environnement AVANT le lancement
if $POSTGRES_AVAILABLE; then
    echo "🗄️  Mode: PostgreSQL + Redis (Production)"
    export USE_POSTGRES=true
    export POSTGRES_HOST=localhost
    export POSTGRES_DB=bankreports
    export POSTGRES_USER=postgres
    export POSTGRES_PASSWORD=postgres
    export POSTGRES_PORT=5432
    export REDIS_URL=redis://localhost:6379/0
    DB_MODE="PostgreSQL"
    CREDENTIALS="admin/hBtH_apEj3dP_baa"
else
    echo "🗄️  Mode: SQLite (Développement)"
    export USE_POSTGRES=false
    DB_MODE="SQLite"
    CREDENTIALS="admin/admin123"
fi

echo "📊 Lancement de l'API FastAPI (port 8001)..."
cd src
python -m uvicorn api.main:app --reload --port 8001 &
API_PID=$!
cd ..

echo "🌐 Lancement du Frontend Django (port 8080)..."
cd frontend

# Configuration automatique des migrations et utilisateurs
echo "🔧 Configuration de la base de données Django..."
python manage.py makemigrations --noinput > /dev/null 2>&1
python manage.py migrate --noinput > /dev/null 2>&1

python manage.py runserver 8080 &
DJANGO_PID=$!
cd ..

# Configuration des utilisateurs admin après démarrage
echo "👤 Configuration des utilisateurs admin..."
sleep 3
python setup_admin_users.py > /dev/null 2>&1 || echo "⚠️  Configuration utilisateur à finaliser manuellement"

# Attendre que les serveurs démarrent
echo "⏳ Démarrage des serveurs..."
sleep 8

# Tester les services avec retry
echo ""
echo "🔍 VÉRIFICATION DES SERVICES"
echo "=============================="

# Test API avec retry
API_OK=false
for i in {1..3}; do
    if curl -s http://localhost:8001/health > /dev/null; then
        echo "✅ API FastAPI: http://localhost:8001 (Opérationnelle)"
        echo "📚 Documentation: http://localhost:8001/docs"
        API_OK=true
        break
    else
        echo "⏳ API FastAPI: Tentative $i/3..."
        sleep 2
    fi
done

if ! $API_OK; then
    echo "❌ API FastAPI: Erreur de connexion"
fi

# Test Django avec retry
DJANGO_OK=false
for i in {1..5}; do
    # Test simple sur la page d'accueil
    if curl -s -m 5 http://localhost:8080/ > /dev/null 2>&1; then
        echo "✅ Frontend Django: http://localhost:8080 (Opérationnel)"
        echo "⚙️  Dashboard Celery: http://localhost:8080/celery/"
        DJANGO_OK=true
        break
    else
        echo "⏳ Frontend Django: Tentative $i/5..."
        sleep 3
    fi
done

if ! $DJANGO_OK; then
    echo "⚠️  Frontend Django: Démarrage en cours (peut nécessiter plus de temps)"
fi

# Test Celery
if curl -s http://localhost:8001/api/celery/status > /dev/null; then
    echo "✅ API Celery: http://localhost:8001/api/celery/status (Disponible)"
else
    echo "⚠️  API Celery: Mode dégradé (Redis non disponible)"
fi

# Test Base de données
if $POSTGRES_AVAILABLE; then
    if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        echo "✅ PostgreSQL: Opérationnel (port 5432)"
        echo "🔑 DB Access: postgres/postgres@bankreports"
    else
        echo "⚠️  PostgreSQL: En cours de stabilisation..."
    fi
else
    echo "⚠️  Base de données: SQLite (mode fallback)"
fi

echo ""
echo "🎯 SYSTÈME PRÊT !"
echo "=================="
echo "🌐 Frontend: http://localhost:8080"
echo "📊 API: http://localhost:8001"
echo "📚 Documentation: http://localhost:8001/docs"
echo "⚙️  Dashboard Celery: http://localhost:8080/celery/"
echo "🗄️  Base de données: $DB_MODE"

if $POSTGRES_AVAILABLE; then
    echo "🚀 Redis: localhost:6379"
    echo "🗄️  PostgreSQL: localhost:5432 (postgres/postgres/bankreports)"
fi

echo ""
echo "🔑 IDENTIFIANTS DE CONNEXION:"
echo "👤 Username: admin"
echo "🔒 Password: $CREDENTIALS"
echo "📧 Email: admin@example.com"
echo ""
echo "💡 Appuyez sur Ctrl+C pour arrêter les serveurs"
echo "⚠️  Note: Si Django semble lent, attendez 30-60 secondes supplémentaires"
echo ""

# Garder le script en vie
wait $API_PID $DJANGO_PID 
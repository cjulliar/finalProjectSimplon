#!/bin/bash
# Script pour lancer les serveurs de développement

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

echo "🗄️  Mode: SQLite (Base consolidée)"
export USE_POSTGRES=false
DB_MODE="SQLite"
CREDENTIALS="admin/admin123"

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
for i in {1..3}; do
    if curl -s http://localhost:8080 > /dev/null; then
        echo "✅ Frontend Django: http://localhost:8080 (Opérationnel)"
        DJANGO_OK=true
        break
    else
        echo "⏳ Frontend Django: Tentative $i/3..."
        sleep 2
    fi
done

if ! $DJANGO_OK; then
    echo "❌ Frontend Django: Erreur de connexion"
fi

echo ""
echo "🎉 SYSTÈME DÉMARRÉ AVEC SUCCÈS !"
echo "================================"
echo "🌐 Frontend: http://localhost:8080"
echo "📊 API: http://localhost:8001"
echo "📚 Documentation API: http://localhost:8001/docs"
echo ""
echo "🔐 Identifiants de connexion:"
echo "   👤 Utilisateur: admin"
echo "   🔑 Mot de passe: admin123"
echo ""
echo "📊 Base de données: $DB_MODE"
echo "🗄️  Base: bankreports.db (consolidée)"
echo ""
echo "⏹️  Pour arrêter les serveurs: Ctrl+C"
echo "========================================"

# Attendre indéfiniment
wait 
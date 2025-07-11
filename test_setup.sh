#!/bin/bash

echo "🧪 TEST RAPIDE DE L'INSTALLATION"
echo "================================"

# Test Python
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 installé"
else
    echo "❌ Python 3 manquant"
fi

# Test pip
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 installé"
else
    echo "❌ pip3 manquant"
fi

# Test Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker installé"
else
    echo "⚠️  Docker non installé (mode local uniquement)"
fi

# Test Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose installé"
else
    echo "⚠️  Docker Compose non installé"
fi

echo ""
echo "🎯 Pour lancer le projet :"
echo "   • Installation complète : ./install_and_run.sh"
echo "   • Lancement rapide Docker : ./quick_start.sh"
echo "   • Développement local : ./dev_start.sh"
echo ""

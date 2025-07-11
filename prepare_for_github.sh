#!/bin/bash

# Script de préparation pour GitHub
# Auteur: Cyril Julliard

echo "🔧 PRÉPARATION DU PROJET POUR GITHUB"
echo "===================================="

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

# Rendre tous les scripts exécutables
print_status "Rendre les scripts exécutables..."
chmod +x install_and_run.sh
chmod +x quick_start.sh
chmod +x dev_start.sh
chmod +x start_project.sh
chmod +x stop_project.sh
chmod +x run_project.sh
chmod +x run_dev_servers.sh
chmod +x run_docker_env.sh
chmod +x generate_prompts.sh

print_success "Scripts rendus exécutables"

# Vérifier que les fichiers sensibles ne sont pas commités
print_status "Vérification des fichiers sensibles..."

SENSITIVE_FILES=(
    ".env"
    "smtp_config.env"
    "admin_credentials.txt"
    "credentials/"
    "*.db"
    "*.sqlite"
    "*.sqlite3"
)

for file in "${SENSITIVE_FILES[@]}"; do
    if git ls-files | grep -q "$file"; then
        print_warning "Fichier sensible détecté dans Git: $file"
        echo "   Considérez le supprimer avec: git rm --cached $file"
    fi
done

# Vérifier la taille des fichiers
print_status "Vérification de la taille des fichiers..."

LARGE_FILES=$(find . -type f -size +50M 2>/dev/null | head -10)
if [ ! -z "$LARGE_FILES" ]; then
    print_warning "Fichiers volumineux détectés:"
    echo "$LARGE_FILES"
    echo "   Considérez les ajouter au .gitignore ou utiliser Git LFS"
fi

# Créer un fichier de version
print_status "Création du fichier de version..."
echo "Version: 1.0.0" > VERSION
echo "Date: $(date)" >> VERSION
echo "Auteur: Cyril Julliard" >> VERSION

print_success "Fichier de version créé"

# Vérifier la structure du projet
print_status "Vérification de la structure du projet..."

REQUIRED_FILES=(
    "README.md"
    "requirements.txt"
    "docker-compose.yml"
    "install_and_run.sh"
    "quick_start.sh"
    "dev_start.sh"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "✅ $file présent"
    else
        print_warning "⚠️  $file manquant"
    fi
done

# Créer un fichier de test rapide
print_status "Création d'un script de test rapide..."
cat > test_setup.sh << 'EOF'
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
EOF

chmod +x test_setup.sh
print_success "Script de test créé"

echo ""
echo "🎉 PROJET PRÊT POUR GITHUB !"
echo "============================"
echo ""
echo "📋 Prochaines étapes :"
echo "   1. Vérifiez que tous les fichiers sensibles sont dans .gitignore"
echo "   2. Testez l'installation : ./test_setup.sh"
echo "   3. Committez les changements : git add . && git commit -m 'Prepare for GitHub'"
echo "   4. Poussez vers GitHub : git push origin main"
echo ""
echo "🚀 Une fois sur GitHub, les utilisateurs pourront :"
echo "   • Cloner le projet"
echo "   • Exécuter ./install_and_run.sh pour une installation complète"
echo "   • Ou ./quick_start.sh pour un lancement rapide"
echo "" 
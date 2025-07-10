#!/bin/bash

# 📊 Script de génération des diagrammes d'architecture

echo "📊 === GÉNÉRATION DES DIAGRAMMES ==="
echo

# Fonction pour vérifier si mermaid-cli est installé
check_mermaid() {
    if command -v mmdc &> /dev/null; then
        echo "✅ Mermaid CLI trouvé"
        return 0
    else
        echo "❌ Mermaid CLI non trouvé"
        return 1
    fi
}

# Fonction pour installer mermaid-cli
install_mermaid() {
    echo "📦 Installation de Mermaid CLI..."
    if command -v npm &> /dev/null; then
        npm install -g @mermaid-js/mermaid-cli
        echo "✅ Mermaid CLI installé"
    else
        echo "❌ NPM non trouvé. Veuillez installer Node.js d'abord"
        echo "   Ou utilisez l'éditeur en ligne : https://mermaid.live/"
        return 1
    fi
}

# Fonction pour générer les images avec mermaid-cli
generate_with_cli() {
    echo "🎨 Génération des images avec Mermaid CLI..."
    
    if [ -f "docs/database_architecture_diagram.mmd" ]; then
        mmdc -i docs/database_architecture_diagram.mmd -o docs/database_architecture.png -t dark -b transparent
        echo "✅ docs/database_architecture.png créé"
    fi
    
    if [ -f "docs/database_overview_diagram.mmd" ]; then
        mmdc -i docs/database_overview_diagram.mmd -o docs/database_overview.png -t dark -b transparent
        echo "✅ docs/database_overview.png créé"
    fi
}

# Fonction pour générer avec Docker
generate_with_docker() {
    echo "🐳 Génération des images avec Docker..."
    
    if [ -f "docs/database_architecture_diagram.mmd" ]; then
        docker run --rm -v $(pwd):/data minlag/mermaid-cli -i /data/docs/database_architecture_diagram.mmd -o /data/docs/database_architecture.png -t dark -b transparent
        echo "✅ docs/database_architecture.png créé (Docker)"
    fi
    
    if [ -f "docs/database_overview_diagram.mmd" ]; then
        docker run --rm -v $(pwd):/data minlag/mermaid-cli -i /data/docs/database_overview_diagram.mmd -o /data/docs/database_overview.png -t dark -b transparent
        echo "✅ docs/database_overview.png créé (Docker)"
    fi
}

# Fonction pour afficher les instructions manuelles
show_manual_instructions() {
    echo "📋 Instructions pour génération manuelle :"
    echo "1. Aller sur https://mermaid.live/"
    echo "2. Copier le contenu de docs/database_architecture_diagram.mmd"
    echo "3. Coller dans l'éditeur"
    echo "4. Cliquer sur 'Actions' > 'Download PNG'"
    echo "5. Sauvegarder sous docs/database_architecture.png"
    echo
    echo "Répéter pour docs/database_overview_diagram.mmd"
}

# Menu principal
case "$1" in
    "cli")
        if check_mermaid; then
            generate_with_cli
        else
            echo "❓ Voulez-vous installer Mermaid CLI ? (y/n)"
            read -r response
            if [[ "$response" == "y" || "$response" == "Y" ]]; then
                install_mermaid && generate_with_cli
            else
                show_manual_instructions
            fi
        fi
        ;;
    "docker")
        if command -v docker &> /dev/null; then
            generate_with_docker
        else
            echo "❌ Docker non trouvé"
            show_manual_instructions
        fi
        ;;
    "manual"|"help"|"")
        show_manual_instructions
        ;;
    *)
        echo "Usage: $0 {cli|docker|manual}"
        echo
        echo "Méthodes de génération :"
        echo "  cli     - Utiliser Mermaid CLI (installation automatique si nécessaire)"
        echo "  docker  - Utiliser Docker avec Mermaid"
        echo "  manual  - Instructions pour génération manuelle"
        echo
        exit 1
        ;;
esac

echo
echo "📁 Fichiers de diagrammes disponibles :"
ls -la docs/*diagram*.mmd 2>/dev/null || echo "Aucun fichier .mmd trouvé"

echo
echo "🖼️ Images générées :"
ls -la docs/*.png 2>/dev/null || echo "Aucune image PNG trouvée" 
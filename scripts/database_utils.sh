#!/bin/bash

# 🗄️ Utilitaires de gestion des bases de données

echo "🗄️ === UTILITAIRES BASES DE DONNÉES ==="
echo

# Fonction pour afficher le statut
show_status() {
    echo "📊 Statut actuel des bases de données:"
    python check_database_status.py
    echo
}

# Fonction pour tester le fallback
test_fallback() {
    echo "🔧 Test du système de fallback..."
    echo "1. Arrêt de PostgreSQL:"
    docker stop finalprojectsimplon-db-1
    
    echo "2. Redémarrage de l'API:"
    docker restart finalprojectsimplon-api-1
    
    echo "3. Attente stabilisation..."
    sleep 5
    
    echo "4. Vérification du fallback:"
    python check_database_status.py
    echo
}

# Fonction pour restaurer PostgreSQL
restore_postgres() {
    echo "🔄 Restauration de PostgreSQL..."
    echo "1. Redémarrage de PostgreSQL:"
    docker start finalprojectsimplon-db-1
    
    echo "2. Redémarrage de l'API:"
    docker restart finalprojectsimplon-api-1
    
    echo "3. Attente stabilisation..."
    sleep 8
    
    echo "4. Vérification du retour à PostgreSQL:"
    python check_database_status.py
    echo
}

# Fonction pour afficher les logs
show_logs() {
    echo "📋 Logs récents de l'API:"
    docker logs finalprojectsimplon-api-1 --tail=10
    echo
}

# Menu principal
case "$1" in
    "status")
        show_status
        ;;
    "test-fallback")
        test_fallback
        ;;
    "restore")
        restore_postgres
        ;;
    "logs")
        show_logs
        ;;
    "full-test")
        echo "🧪 Test complet du système de fallback..."
        show_status
        test_fallback
        echo "⏳ Attente 5 secondes..."
        sleep 5
        restore_postgres
        ;;
    *)
        echo "Usage: $0 {status|test-fallback|restore|logs|full-test}"
        echo
        echo "Commandes disponibles:"
        echo "  status       - Afficher le statut des bases"
        echo "  test-fallback - Tester le basculement vers SQLite"
        echo "  restore      - Restaurer PostgreSQL"
        echo "  logs         - Afficher les logs récents"
        echo "  full-test    - Test complet (fallback + restauration)"
        echo
        exit 1
        ;;
esac 
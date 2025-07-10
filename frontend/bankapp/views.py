from django.shortcuts import render
from django.http import JsonResponse

def index(request):
    """Page d'accueil du système de rapports bancaires."""
    context = {
        'page_title': 'Accueil',
    }
    return render(request, 'bankapp/base.html', context)

def celery_dashboard(request):
    """Dashboard de gestion des tâches Celery."""
    
    # Vérifier la disponibilité de l'API Celery
    api_available = True
    api_status = "Vérification en cours..."
    
    try:
        import requests
        response = requests.get('http://localhost:8001/api/celery/status', timeout=5)
        if response.status_code == 200:
            api_status = "API Celery disponible"
        else:
            api_available = False
            api_status = f"API inaccessible (code: {response.status_code})"
    except Exception as e:
        api_available = False
        api_status = f"Erreur de connexion: {str(e)}"
    
    context = {
        'api_available': api_available,
        'api_status': api_status,
        'api_base_url': 'http://localhost:8001/api/celery'
    }
    
    return render(request, 'bankapp/celery_dashboard.html', context) 
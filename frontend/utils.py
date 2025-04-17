"""
Utilitaires partagés pour l'interface frontend.
"""

import logging
import requests
from functools import wraps
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

def get_authenticated_session(request):
    """
    Renvoie une session requests préparée avec le jeton d'authentification.
    
    Args:
        request: La requête Django qui contient le jeton dans la session
        
    Returns:
        session: Session requests avec l'en-tête d'authentification
    """
    session = requests.Session()
    token = request.session.get('api_token')
    
    if token:
        session.headers.update({'Authorization': f'Bearer {token}'})
    
    return session

def api_call(method, url, **kwargs):
    """
    Effectue un appel à l'API avec gestion des erreurs.
    
    Args:
        method: Méthode HTTP (get, post, put, delete)
        url: URL relative de l'API (sans le préfixe API_URL)
        **kwargs: Arguments supplémentaires pour la requête
        
    Returns:
        data: Données JSON de la réponse ou None en cas d'erreur
        status_code: Code HTTP de la réponse ou None en cas d'erreur
    """
    try:
        full_url = f"{settings.API_URL}{url}"
        response = getattr(requests, method.lower())(full_url, **kwargs)
        
        # Tenter de renvoyer les données JSON
        try:
            data = response.json()
        except ValueError:
            data = None
            
        return data, response.status_code
    except requests.RequestException as e:
        logger.error(f"Erreur lors de l'appel API {method} {url}: {str(e)}")
        return None, None

def require_api_token(view_func):
    """
    Décorateur qui vérifie que le jeton API est présent dans la session.
    Redirige vers la page de connexion si le jeton est absent.
    
    Args:
        view_func: La vue à décorer
        
    Returns:
        wrapped_view: Vue décorée avec vérification du jeton
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Vérifier si le jeton est présent
        if not request.session.get('api_token'):
            messages.error(request, "Votre session a expiré. Veuillez vous reconnecter.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapped_view 
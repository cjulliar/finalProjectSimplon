import requests
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
from .services import get_api_client

logger = logging.getLogger(__name__)

@login_required
def dashboard_view(request):
    """
    Vue principale du tableau de bord.
    Affiche un résumé des données bancaires et des rapports IA.
    """
    # Initialiser le client API
    api_client = get_api_client(request)
    
    # Vérifier si le token est présent
    if not request.session.get('api_token'):
        messages.warning(
            request, 
            "Vous n'êtes pas authentifié auprès de l'API. Certaines fonctionnalités ne seront pas disponibles. "
            "Veuillez vous déconnecter et vous reconnecter."
        )
        return render(request, 'dashboard/dashboard.html', {'auth_error': True})
    
    # Préparer le contexte par défaut
    context = {
        'stats_by_agency': [],
        'stats_by_date': [],
        'latest_analyses': [],
        'total_transactions': 0,
        'total_amount': 0,
    }
    
    try:
        # Récupérer les statistiques par agence
        stats_by_agency = api_client.get_stats_by_agency()
        context['stats_by_agency'] = stats_by_agency
        
        # Récupérer les statistiques par date
        stats_by_date = api_client.get_stats_by_date(days=30)
        context['stats_by_date'] = stats_by_date
        
        # Récupérer les dernières analyses IA
        latest_analyses = api_client.get_latest_analyses(limit=5)
        context['latest_analyses'] = latest_analyses
        
        # Calculer les totaux
        if stats_by_agency:
            context['total_transactions'] = sum(agency.get('nombre_transactions', 0) for agency in stats_by_agency)
            context['total_amount'] = sum(agency.get('montant', 0) for agency in stats_by_agency)
        
        return render(request, 'dashboard/dashboard.html', context)
        
    except requests.exceptions.HTTPError as e:
        # Gestion spécifique des erreurs HTTP
        status_code = e.response.status_code if hasattr(e, 'response') else None
        
        if status_code == 401:
            # Erreur d'authentification
            logger.error(f"Erreur d'authentification API: {str(e)}")
            messages.error(
                request, 
                "Votre session API a expiré. Veuillez vous déconnecter et vous reconnecter pour rafraîchir votre authentification."
            )
            # Supprimer le token invalide
            if 'api_token' in request.session:
                del request.session['api_token']
                
            context['auth_error'] = True
        else:
            # Autres erreurs HTTP
            logger.error(f"Erreur HTTP lors de l'accès à l'API: {str(e)}")
            context['error'] = f"Erreur {status_code}: {str(e)}"
            context['api_error'] = True
            
        return render(request, 'dashboard/dashboard.html', context)
            
    except Exception as e:
        # Erreurs génériques
        logger.error(f"Erreur lors de l'accès au tableau de bord: {str(e)}")
        context['error'] = str(e)
        context['api_error'] = True
        return render(request, 'dashboard/dashboard.html', context) 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from dashboard.services import get_api_client


@login_required
def bank_data_list(request):
    """
    Liste des données bancaires avec possibilité de filtrage.
    """
    api_client = get_api_client(request)
    
    # Récupérer les paramètres de filtre
    agence = request.GET.get('agence', '')
    date_debut_str = request.GET.get('date_debut', '')
    date_fin_str = request.GET.get('date_fin', '')
    page = request.GET.get('page', 1)
    
    # Convertir les dates si elles sont spécifiées
    date_debut = None
    date_fin = None
    
    if date_debut_str:
        try:
            date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    if date_fin_str:
        try:
            date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    try:
        # Récupérer les données avec filtres
        bank_data = api_client.get_bank_data(
            skip=0, 
            limit=1000,  # Nous filtrerons côté client pour la pagination
            agence=agence if agence else None,
            date_debut=date_debut,
            date_fin=date_fin
        )
        
        # Récupérer les statistiques par agence pour le filtre
        stats_by_agency = api_client.get_stats_by_agency()
        agencies = [agency['agence'] for agency in stats_by_agency]
        
        # Paginer les résultats
        paginator = Paginator(bank_data, 20)  # 20 entrées par page
        page_obj = paginator.get_page(page)
        
        context = {
            'page_obj': page_obj,
            'agencies': agencies,
            'current_agence': agence,
            'date_debut': date_debut_str,
            'date_fin': date_fin_str,
            'total_results': len(bank_data)
        }
        
        return render(request, 'bank_data/list.html', context)
        
    except Exception as e:
        context = {
            'error': str(e),
            'api_error': True
        }
        return render(request, 'bank_data/list.html', context)


@login_required
def bank_data_detail(request, bank_data_id):
    """
    Détail d'une entrée de données bancaires.
    """
    api_client = get_api_client(request)
    
    try:
        # Récupérer les détails d'une entrée spécifique
        bank_data = api_client.get_bank_data_by_id(bank_data_id)
        
        # Calculer quelques statistiques pour comparer
        stats_by_agency = api_client.get_stats_by_agency()
        agency_stats = next((s for s in stats_by_agency if s['agence'] == bank_data['agence']), None)
        
        context = {
            'bank_data': bank_data,
            'agency_stats': agency_stats
        }
        
        return render(request, 'bank_data/detail.html', context)
        
    except Exception as e:
        context = {
            'error': str(e),
            'api_error': True
        }
        return render(request, 'bank_data/detail.html', context) 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime, timedelta
from dashboard.services import get_api_client


@login_required
def report_list(request):
    """
    Liste des rapports IA générés.
    """
    api_client = get_api_client(request)
    
    try:
        # Récupérer tous les rapports
        reports = api_client.get_latest_analyses(limit=100)
        
        context = {
            'reports': reports
        }
        
        return render(request, 'ai_reports/list.html', context)
        
    except Exception as e:
        context = {
            'error': str(e),
            'api_error': True
        }
        return render(request, 'ai_reports/list.html', context)


@login_required
def report_create(request):
    """
    Création d'un nouveau rapport IA.
    """
    api_client = get_api_client(request)
    
    # Récupérer les statistiques par agence pour le formulaire
    try:
        stats_by_agency = api_client.get_stats_by_agency()
        agencies = [agency['agence'] for agency in stats_by_agency]
    except Exception:
        agencies = []
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        agence = request.POST.get('agence', '')
        date_debut_str = request.POST.get('date_debut', '')
        date_fin_str = request.POST.get('date_fin', '')
        include_visualizations = request.POST.get('include_visualizations') == 'on'
        
        # Convertir les dates
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
            # Créer la requête d'analyse
            analysis_request = {
                'start_date': date_debut.isoformat() if date_debut else None,
                'end_date': date_fin.isoformat() if date_fin else None,
                'agence': agence if agence else None,
                'include_visualizations': include_visualizations
            }
            
            # Envoyer la requête à l'API
            response = api_client.create_analysis(analysis_request)
            
            messages.success(request, "Analyse IA créée avec succès.")
            return redirect('ai_reports:detail', report_id=response['id'])
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la création de l'analyse : {str(e)}")
    
    context = {
        'agencies': agencies,
        'default_date_debut': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'default_date_fin': datetime.now().strftime('%Y-%m-%d')
    }
    
    return render(request, 'ai_reports/create.html', context)


@login_required
def report_detail(request, report_id):
    """
    Détail d'un rapport IA.
    """
    api_client = get_api_client(request)
    
    try:
        # Récupérer les détails du rapport
        report = api_client.get_analysis(report_id)
        
        context = {
            'report': report
        }
        
        return render(request, 'ai_reports/detail.html', context)
        
    except Exception as e:
        context = {
            'error': str(e),
            'api_error': True,
            'report_id': report_id
        }
        return render(request, 'ai_reports/detail.html', context) 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from dashboard.services import get_api_client


@login_required
def report_list(request):
    """
    Liste des rapports IA générés.
    """
    api_client = get_api_client(request)
    
    try:
        # Récupérer tous les rapports
        analyses = api_client.get_latest_analyses(limit=10)
        
        return render(request, 'ai_reports/list.html', {
            'analyses': analyses.get('analyses', []),
            'count': analyses.get('count', 0)
        })
        
    except Exception as e:
        return render(request, 'ai_reports/list.html', {
            'error': str(e),
            'analyses': [],
            'count': 0
        })


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
            
            if 'id' in response:
                return redirect('ai_reports:detail', report_id=response['id'])
            else:
                return render(request, 'ai_reports/create.html', {
                    'error': 'Erreur lors de la création du rapport',
                    'form_data': analysis_request
                })
            
        except Exception as e:
            return render(request, 'ai_reports/create.html', {
                'error': str(e),
                'form_data': {
                    'agence': agence,
                    'start_date': date_debut_str,
                    'end_date': date_fin_str,
                    'include_visualizations': include_visualizations
                }
            })
    
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
        
        return render(request, 'ai_reports/detail.html', {
            'report': report
        })
        
    except Exception as e:
        return render(request, 'ai_reports/detail.html', {
            'error': str(e)
        })


@login_required
def bank_charts(request):
    """
    Graphiques d'évolution pour une banque spécifique.
    """
    # Connexion à la base de données SQLite
    db_path = os.path.join(settings.BASE_DIR, '..', 'bankreports.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Liste des banques disponibles
    cursor.execute("SELECT DISTINCT agence FROM bank_data_enriched ORDER BY agence")
    banks = [row['agence'] for row in cursor.fetchall()]
    
    if not banks:
        # Fallback sur les banques par défaut si aucune n'est trouvée
        banks = ["Banque A", "Banque B", "Banque C", "Banque D"]
    
    # Banque sélectionnée (par défaut: première banque de la liste)
    default_bank = banks[0] if banks else "Banque A"
    selected_bank = request.GET.get('bank', default_bank)
    
    # Récupérer les données pour la banque sélectionnée
    cursor.execute("""
        SELECT semaine_id, MOY_GLOBAL, OCC_PART, OCC_PRO, RANG_GLOBAL
        FROM bank_data_enriched
        WHERE agence = ?
        ORDER BY semaine_id DESC
        LIMIT 20
    """, (selected_bank,))
    
    data = cursor.fetchall()
    
    # Préparer les données pour les graphiques
    charts = {
        'labels': [],
        'moy_global': [],
        'occ_part': [],
        'occ_pro': [],
        'rang_global': []
    }
    
    for row in data:
        charts['labels'].append(row['semaine_id'])
        charts['moy_global'].append(row['MOY_GLOBAL'] or 0)
        charts['occ_part'].append(row['OCC_PART'] or 0)
        charts['occ_pro'].append(row['OCC_PRO'] or 0)
        charts['rang_global'].append(row['RANG_GLOBAL'] or 0)
    
    conn.close()
    
    return render(request, 'ai_reports/bank_charts.html', {
        'banks': banks,
        'selected_bank': selected_bank,
        'charts': charts
    }) 
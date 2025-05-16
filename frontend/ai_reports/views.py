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
def email_reports(request):
    """
    Afficher les rapports par email pour une banque spécifique.
    Cette vue permet de voir les emails de rapports pour chaque banque
    avec un sélecteur de banque en haut à gauche.
    """
    # Connexion à la base de données SQLite
    db_path = os.path.join(settings.BASE_DIR, '..', 'bankreports.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Liste des banques disponibles
    cursor.execute("SELECT DISTINCT bank_name FROM email_reports ORDER BY bank_name")
    banks = [row['bank_name'] for row in cursor.fetchall()]
    
    if not banks:
        # Fallback sur les banques par défaut si aucune n'est trouvée
        banks = ["Banque A", "Banque B", "Banque C", "Banque D"]
    
    # Banque sélectionnée (par défaut: première banque de la liste)
    default_bank = banks[0] if banks else "Banque A"
    selected_bank = request.GET.get('bank', default_bank)
    
    # Récupérer les rapports pour la banque sélectionnée
    cursor.execute("""
        SELECT id, subject, content, sent_at, recipients, status
        FROM email_reports
        WHERE bank_name = ?
        ORDER BY sent_at DESC
    """, (selected_bank,))
    
    reports = []
    for row in cursor.fetchall():
        # Convertir les données JSON
        try:
            recipients = json.loads(row['recipients'])
        except:
            recipients = []
            
        # Convertir la date
        try:
            sent_at = datetime.fromisoformat(row['sent_at']).strftime("%d/%m/%Y %H:%M")
        except:
            sent_at = row['sent_at']
            
        reports.append({
            'id': row['id'],
            'subject': row['subject'],
            'content': row['content'],
            'sent_at': sent_at,
            'recipients': recipients,
            'status': row['status']
        })
    
    conn.close()
    
    return render(request, 'ai_reports/email_reports.html', {
        'banks': banks,
        'selected_bank': selected_bank,
        'reports': reports
    })


@login_required
def bank_charts(request):
    """
    Afficher les courbes d'évolution pour une banque spécifique.
    Cette vue permet de voir les graphiques d'évolution des chiffres clés
    avec un sélecteur de banque en haut à gauche.
    """
    # Connexion à la base de données SQLite
    db_path = os.path.join(settings.BASE_DIR, '..', 'bankreports.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Liste des banques disponibles
    cursor.execute("SELECT DISTINCT bank_name FROM email_reports ORDER BY bank_name")
    banks = [row['bank_name'] for row in cursor.fetchall()]
    
    if not banks:
        # Fallback sur les banques par défaut si aucune n'est trouvée
        banks = ["Banque A", "Banque B", "Banque C", "Banque D"]
    
    # Banque sélectionnée (par défaut: première banque de la liste)
    default_bank = banks[0] if banks else "Banque A"
    selected_bank = request.GET.get('bank', default_bank)
    
    # Récupérer les visualisations pour la banque sélectionnée
    output_dir = Path("output")
    charts = []
    
    if output_dir.exists():
        # Récupérer les dernières visualisations pour la banque sélectionnée
        # Format des fichiers: evolution_montants_Banque A_20250514_151324.png
        
        # Trouver tous les timestamps uniques pour cette banque
        timestamps = set()
        for file in output_dir.glob(f"*_{selected_bank}_*.png"):
            parts = file.stem.split('_')
            if len(parts) >= 4:
                timestamps.add(parts[-2] + '_' + parts[-1])
        
        # Pour chaque timestamp, récupérer toutes les visualisations
        for timestamp in sorted(timestamps, reverse=True):
            timestamp_charts = []
            
            # Chercher les visualisations pour ce timestamp
            for file in output_dir.glob(f"*_{selected_bank}_{timestamp}.png"):
                chart_type = file.stem.split('_')[0]
                if chart_type == "evolution":
                    chart_type = file.stem.split('_')[0] + '_' + file.stem.split('_')[1]
                
                timestamp_charts.append({
                    'file': str(file),
                    'type': chart_type,
                    'url': f"/static/output/{file.name}"
                })
            
            if timestamp_charts:
                try:
                    date = datetime.strptime(timestamp.split('_')[0], "%Y%m%d").strftime("%d/%m/%Y")
                except ValueError:
                    date = timestamp
                
                charts.append({
                    'date': date,
                    'timestamp': timestamp,
                    'charts': timestamp_charts
                })
        
        # Limiter à 5 ensembles de visualisations
        charts = charts[:5]
    
    conn.close()
    
    return render(request, 'ai_reports/bank_charts.html', {
        'banks': banks,
        'selected_bank': selected_bank,
        'charts': charts
    }) 
import requests
import logging
import sqlite3
import os
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
from .services import get_api_client

logger = logging.getLogger(__name__)

# Chemin de la base de données SQLite
DB_PATH = os.environ.get('BANKREPORTS_DB_PATH', '/app/bankreports.db')

def get_user_agence(username):
    """Extrait le nom de l'agence à partir du nom d'utilisateur"""
    if username.startswith('directeurBanque'):
        # Enlever 'directeurBanque' et retourner le reste
        agence = username.replace('directeurBanque', '')
        return f"Banque {agence}"
    # Pour les utilisateurs de test, retourner "A" pour correspondre aux bank_name dans la base
    return "A"  # Fallback par défaut

def get_agence_data(agence_name):
    """Récupère les données de l'agence depuis la base SQLite"""
    try:
        logger.info(f"Tentative de connexion à la base SQLite: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Récupérer les données de l'agence
        cursor.execute('''
            SELECT * FROM bank_data_enriched 
            WHERE agence = ? 
            ORDER BY date_semaine DESC
        ''', (agence_name,))
        
        columns = [description[0] for description in cursor.description]
        data = []
        for row in cursor.fetchall():
            data.append(dict(zip(columns, row)))
        
        logger.info(f"Données récupérées pour {agence_name}: {len(data)} enregistrements")
        conn.close()
        return data
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données: {e}")
        logger.error(f"Chemin de la base: {DB_PATH}")
        return []

def home_view(request):
    """
    Vue publique de la page d'accueil.
    Accessible sans authentification.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:dernier_rapport')
    
    context = {
        'system_status': 'operational',
        'api_url': settings.API_URL,
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def dashboard_view(request):
    """
    Vue principale du tableau de bord.
    Redirige vers le dernier rapport.
    """
    return redirect('dashboard:dernier_rapport')

@login_required
def dernier_rapport_view(request):
    """
    Vue du dernier rapport envoyé - Affiche les emails générés par IA.
    """
    agence_name = get_user_agence(request.user.username)
    
    # Connexion à la base de données SQLite pour récupérer les emails IA
    import os
    import sqlite3
    import json
    from datetime import datetime
    from django.conf import settings
    
    db_path = os.path.join(settings.BASE_DIR, '..', 'bankreports.db')
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Utiliser directement le nom d'agence (sans préfixe "Banque ")
        email_agence_name = agence_name.replace('Banque ', '')
        
        # Récupérer les emails pour cette agence
        cursor.execute("""
            SELECT id, subject, content, sent_at, recipients, status
            FROM email_reports
            WHERE bank_name = ? AND status = 'generated'
            ORDER BY sent_at DESC
            LIMIT 1
        """, (email_agence_name,))
        
        email_data = cursor.fetchone()
        
        if email_data:
            # Convertir les données JSON
            try:
                recipients = json.loads(email_data['recipients'])
            except:
                recipients = []
                
            # Convertir la date
            try:
                sent_at = datetime.fromisoformat(email_data['sent_at']).strftime("%d/%m/%Y %H:%M")
            except:
                sent_at = email_data['sent_at']
            
            dernier_rapport = {
                'date_semaine': sent_at,
                'numero_semaine': '2025_28',
                'annee': '2025',
                'contenu': email_data['content'],
                'subject': email_data['subject'],
                'recipients': recipients,
                'status': email_data['status'],
                'is_ai_generated': True,
                'statistiques': {
                    'montant_global': 'N/A',
                    'rang_global': 'N/A',
                    'clients_particuliers': 'N/A',
                    'clients_professionnels': 'N/A',
                }
            }
        else:
            # Fallback si aucun email trouvé
            dernier_rapport = {
                'date_semaine': 'Aucune donnée',
                'contenu': f'Aucun email IA généré disponible pour {agence_name}.',
                'subject': 'Aucun rapport IA',
                'is_ai_generated': False,
                'statistiques': {}
            }
        
        conn.close()
        
    except Exception as e:
        # En cas d'erreur, afficher un message d'erreur
        dernier_rapport = {
            'date_semaine': 'Erreur',
            'contenu': f'Erreur lors de la récupération des données : {str(e)}',
            'subject': 'Erreur de connexion',
            'is_ai_generated': False,
            'statistiques': {}
        }
    
    context = {
        'agence_name': agence_name,
        'dernier_rapport': dernier_rapport
    }
    
    return render(request, 'dashboard/dernier_rapport.html', context)

@login_required
def historique_rapports_view(request):
    """
    Vue de l'historique des rapports - Affiche l'historique des emails générés par IA.
    """
    agence_name = get_user_agence(request.user.username)
    
    # Connexion à la base de données SQLite pour récupérer les emails IA
    import os
    import sqlite3
    import json
    from datetime import datetime
    from django.conf import settings
    
    db_path = os.path.join(settings.BASE_DIR, '..', 'bankreports.db')
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Utiliser directement le nom d'agence (sans préfixe "Banque ")
        email_agence_name = agence_name.replace('Banque ', '')
        
        # Récupérer tous les emails pour cette agence
        cursor.execute("""
            SELECT id, subject, content, sent_at, recipients, status
            FROM email_reports
            WHERE bank_name = ? AND status = 'generated'
            ORDER BY sent_at DESC
        """, (email_agence_name,))
        
        emails_data = cursor.fetchall()
        
        # Récupérer l'email sélectionné
        selected_email_id = request.GET.get('email_id')
        selected_email = None
        
        if selected_email_id:
            cursor.execute("""
                SELECT id, subject, content, sent_at, recipients, status
                FROM email_reports
                WHERE id = ? AND bank_name = ?
            """, (selected_email_id, email_agence_name))
            selected_email = cursor.fetchone()
        
        # Préparer la liste des emails
        emails_list = []
        for email in emails_data:
            try:
                sent_at = datetime.fromisoformat(email['sent_at']).strftime("%d/%m/%Y %H:%M")
            except:
                sent_at = email['sent_at']
                
            emails_list.append({
                'id': email['id'],
                'subject': email['subject'],
                'sent_at': sent_at,
                'status': email['status']
            })
        
        # Préparer l'email sélectionné pour l'affichage
        rapport = None
        if selected_email:
            try:
                recipients = json.loads(selected_email['recipients'])
            except:
                recipients = []
                
            try:
                sent_at = datetime.fromisoformat(selected_email['sent_at']).strftime("%d/%m/%Y %H:%M")
            except:
                sent_at = selected_email['sent_at']
            
            rapport = {
                'id': selected_email['id'],
                'subject': selected_email['subject'],
                'content': selected_email['content'],
                'sent_at': sent_at,
                'recipients': recipients,
                'status': selected_email['status'],
                'is_ai_generated': True
            }
        
        conn.close()
        
    except Exception as e:
        emails_list = []
        rapport = None
        print(f"Erreur lors de la récupération des emails : {str(e)}")
    
    context = {
        'agence_name': agence_name,
        'emails_list': emails_list,
        'selected_email_id': selected_email_id,
        'rapport': rapport
    }
    
    return render(request, 'dashboard/historique_rapports.html', context)

@login_required
def statistiques_view(request):
    """
    Vue des statistiques - Affiche les statistiques des données enrichies.
    """
    agence_name = get_user_agence(request.user.username)
    
    # Connexion à la base de données SQLite pour récupérer les données enrichies
    import os
    import sqlite3
    from datetime import datetime
    from django.conf import settings
    
    db_path = os.path.join(settings.BASE_DIR, '..', 'bankreports.db')
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Récupérer les données enrichies pour cette agence
        cursor.execute("""
            SELECT * FROM bank_data_enriched
            WHERE agence = ?
            ORDER BY semaine_id DESC
            LIMIT 20
        """, (agence_name,))
        
        agence_data = cursor.fetchall()
        
        if agence_data:
            # Préparer les données pour les graphiques
            dates = []
            montants_globaux = []
            clients_particuliers = []
            clients_professionnels = []
            rangs_globaux = []
            conso_dec = []
            bilan_net = []
            vers_ep_fi = []
            
            for data in agence_data:
                dates.append(data['semaine_id'])
                montants_globaux.append(data['MOY_GLOBAL'] or 0)
                clients_particuliers.append(data['OCC_PART'] or 0)
                clients_professionnels.append(data['OCC_PRO'] or 0)
                rangs_globaux.append(data['RANG_GLOBAL'] or 0)
                conso_dec.append(data['CONSO_DEC'] or 0)
                bilan_net.append(data['BILAN_NET'] or 0)
                vers_ep_fi.append(data['VERS_EP_FI'] or 0)
            
            # Calculer les statistiques globales
            total_montant = sum(montants_globaux)
            moyenne_montant = total_montant / len(montants_globaux) if montants_globaux else 0
            meilleur_rang = min(rangs_globaux) if rangs_globaux else 0
            
            # Statistiques des indicateurs clés
            total_conso_dec = sum(conso_dec)
            total_bilan_net = sum(bilan_net)
            total_vers_ep_fi = sum(vers_ep_fi)
            
            context = {
                'agence_name': agence_name,
                'dates': dates,
                'montants_globaux': montants_globaux,
                'clients_particuliers': clients_particuliers,
                'clients_professionnels': clients_professionnels,
                'rangs_globaux': rangs_globaux,
                'conso_dec': conso_dec,
                'bilan_net': bilan_net,
                'vers_ep_fi': vers_ep_fi,
                'statistiques_globales': {
                    'total_montant': total_montant,
                    'moyenne_montant': moyenne_montant,
                    'meilleur_rang': meilleur_rang,
                    'nombre_semaines': len(agence_data),
                    'total_conso_dec': total_conso_dec,
                    'total_bilan_net': total_bilan_net,
                    'total_vers_ep_fi': total_vers_ep_fi
                },
                'has_data': True
            }
        else:
            context = {
                'agence_name': agence_name,
                'dates': [],
                'montants_globaux': [],
                'clients_particuliers': [],
                'clients_professionnels': [],
                'rangs_globaux': [],
                'conso_dec': [],
                'bilan_net': [],
                'vers_ep_fi': [],
                'statistiques_globales': {
                    'total_montant': 0,
                    'moyenne_montant': 0,
                    'meilleur_rang': 0,
                    'nombre_semaines': 0,
                    'total_conso_dec': 0,
                    'total_bilan_net': 0,
                    'total_vers_ep_fi': 0
                },
                'has_data': False
            }
        
        conn.close()
        
    except Exception as e:
        context = {
            'agence_name': agence_name,
            'dates': [],
            'montants_globaux': [],
            'clients_particuliers': [],
            'clients_professionnels': [],
            'rangs_globaux': [],
            'conso_dec': [],
            'bilan_net': [],
            'vers_ep_fi': [],
            'statistiques_globales': {
                'total_montant': 0,
                'moyenne_montant': 0,
                'meilleur_rang': 0,
                'nombre_semaines': 0,
                'total_conso_dec': 0,
                'total_bilan_net': 0,
                'total_vers_ep_fi': 0
            },
            'has_data': False,
            'error': str(e)
        }
        print(f"Erreur lors de la récupération des données enrichies : {str(e)}")
    
    return render(request, 'dashboard/statistiques.html', context) 
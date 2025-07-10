#!/usr/bin/env python3
"""
Générateur de rapport bancaire avec vraies données de la Banque A.
"""
import sqlite3
import sys
import os
import statistics
from pathlib import Path
from datetime import datetime, timedelta

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent))

# Charger la configuration SMTP
with open('smtp_config.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

from src.ia.email_service import EmailService

def get_bank_data(bank_name="Banque A", weeks=4):
    """Récupérer les données réelles de la banque sur plusieurs semaines."""
    conn = sqlite3.connect('bankreports.db')
    cursor = conn.cursor()
    
    # Récupérer les données des X dernières semaines
    query = """
    SELECT date, montant, nombre_transactions, 
           strftime('%Y-W%W', date) as semaine
    FROM bank_data 
    WHERE agence = ? 
    ORDER BY date DESC 
    LIMIT ?
    """
    
    cursor.execute(query, (bank_name, weeks * 7))  # Approximation
    data = cursor.fetchall()
    
    if not data:
        print(f"❌ Aucune donnée trouvée pour {bank_name}")
        return None
    
    # Organiser par semaine
    weeks_data = {}
    for date, montant, transactions, semaine in data:
        if semaine not in weeks_data:
            weeks_data[semaine] = []
        weeks_data[semaine].append({
            'date': date,
            'montant': montant,
            'transactions': transactions
        })
    
    conn.close()
    return weeks_data

def analyze_weekly_data(weeks_data):
    """Analyser les données hebdomadaires."""
    analysis = {}
    
    for semaine, data in weeks_data.items():
        total_montant = sum(d['montant'] for d in data)
        total_transactions = sum(d['transactions'] for d in data)
        nb_jours = len(data)
        
        analysis[semaine] = {
            'periode': f"{data[0]['date']} à {data[-1]['date']}" if data else "N/A",
            'nb_jours': nb_jours,
            'montant_total': total_montant,
            'transactions_total': total_transactions,
            'montant_moyen_jour': total_montant / nb_jours if nb_jours > 0 else 0,
            'transactions_moyenne_jour': total_transactions / nb_jours if nb_jours > 0 else 0,
            'montant_moyen_transaction': total_montant / total_transactions if total_transactions > 0 else 0
        }
    
    return analysis

def calculate_trends(analysis):
    """Calculer les tendances d'évolution."""
    weeks = sorted(analysis.keys())
    if len(weeks) < 2:
        return {}
    
    current_week = weeks[-1]
    previous_week = weeks[-2]
    
    current = analysis[current_week]
    previous = analysis[previous_week]
    
    evolution_montant = ((current['montant_total'] - previous['montant_total']) / previous['montant_total'] * 100) if previous['montant_total'] > 0 else 0
    evolution_transactions = ((current['transactions_total'] - previous['transactions_total']) / previous['transactions_total'] * 100) if previous['transactions_total'] > 0 else 0
    
    # Tendance générale sur toutes les semaines
    montants_totaux = [analysis[w]['montant_total'] for w in weeks]
    if len(montants_totaux) > 1:
        # Régression linéaire simple
        n = len(montants_totaux)
        x_values = list(range(n))
        sum_x = sum(x_values)
        sum_y = sum(montants_totaux)
        sum_xy = sum(x * y for x, y in zip(x_values, montants_totaux))
        sum_x2 = sum(x * x for x in x_values)
        
        if n * sum_x2 - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            avg_montant = statistics.mean(montants_totaux)
            trend_percentage = (slope / avg_montant * 100) if avg_montant > 0 else 0
        else:
            trend_percentage = 0
    else:
        trend_percentage = 0
    
    return {
        'current_week': current_week,
        'previous_week': previous_week,
        'evolution_montant': evolution_montant,
        'evolution_transactions': evolution_transactions,
        'trend_percentage': trend_percentage,
        'total_weeks': len(weeks)
    }

def generate_html_report(bank_name, analysis, trends):
    """Générer un rapport HTML professionnel avec les vraies données."""
    
    weeks = sorted(analysis.keys())
    current_week = weeks[-1] if weeks else "N/A"
    current_data = analysis.get(current_week, {})
    
    # Déterminer la tendance
    if trends.get('trend_percentage', 0) > 5:
        trend_icon = "📈"
        trend_text = "Progression forte"
        trend_color = "#28a745"
    elif trends.get('trend_percentage', 0) > 0:
        trend_icon = "📊"
        trend_text = "Progression modérée"
        trend_color = "#17a2b8"
    elif trends.get('trend_percentage', 0) > -5:
        trend_icon = "📊"
        trend_text = "Stabilité"
        trend_color = "#ffc107"
    else:
        trend_icon = "📉"
        trend_text = "Déclin"
        trend_color = "#dc3545"
    
    # Données de performance
    montant_total = current_data.get('montant_total', 0)
    transactions_total = current_data.get('transactions_total', 0)
    evolution_montant = trends.get('evolution_montant', 0)
    
    html_report = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 0; 
                background-color: #f8f9fa;
            }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; }}
            .header {{ 
                background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%); 
                color: white; 
                padding: 30px; 
                text-align: center; 
            }}
            .header h1 {{ margin: 0; font-size: 2.2em; }}
            .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 1.1em; }}
            
            .content {{ padding: 30px; }}
            
            .summary-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 20px; 
                margin: 20px 0; 
            }}
            .summary-card {{ 
                background: #f8f9fa; 
                padding: 20px; 
                border-radius: 10px; 
                border-left: 5px solid #2E86AB;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .summary-card h3 {{ margin: 0 0 10px 0; color: #2E86AB; }}
            .summary-card .value {{ font-size: 1.8em; font-weight: bold; color: #333; }}
            .summary-card .label {{ font-size: 0.9em; color: #666; margin-top: 5px; }}
            
            .trend-indicator {{ 
                display: inline-flex; 
                align-items: center; 
                padding: 8px 15px; 
                background: {trend_color}; 
                color: white; 
                border-radius: 20px; 
                font-weight: bold;
                margin: 10px 0;
            }}
            
            .data-table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin: 20px 0;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .data-table th {{ 
                background: #2E86AB; 
                color: white; 
                padding: 15px; 
                text-align: left; 
            }}
            .data-table td {{ 
                padding: 12px 15px; 
                border-bottom: 1px solid #eee; 
            }}
            .data-table tr:nth-child(even) {{ background: #f8f9fa; }}
            
            .section {{ margin: 30px 0; }}
            .section h2 {{ 
                color: #2E86AB; 
                border-bottom: 2px solid #2E86AB; 
                padding-bottom: 10px;
            }}
            
            .recommendations {{ 
                background: #e8f4f8; 
                padding: 20px; 
                border-radius: 10px; 
                border-left: 5px solid #17a2b8;
            }}
            .recommendations ul {{ margin: 10px 0; }}
            .recommendations li {{ margin: 8px 0; }}
            
            .footer {{ 
                background: #f1f3f4; 
                padding: 20px; 
                text-align: center; 
                border-top: 1px solid #e9ecef;
            }}
            .footer p {{ margin: 5px 0; color: #6c757d; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏦 Rapport d'Analyse - {bank_name}</h1>
                <p>📅 Période analysée: {trends.get('total_weeks', 0)} semaines • Semaine actuelle: {current_week}</p>
                <div class="trend-indicator">
                    {trend_icon} {trend_text} ({trends.get('trend_percentage', 0):.1f}%)
                </div>
            </div>

            <div class="content">
                <div class="section">
                    <h2>📊 Indicateurs Clés de Performance</h2>
                    <div class="summary-grid">
                        <div class="summary-card">
                            <h3>💰 Chiffre d'Affaires</h3>
                            <div class="value">{montant_total:,.0f} €</div>
                            <div class="label">Semaine {current_week}</div>
                        </div>
                        <div class="summary-card">
                            <h3>🔄 Transactions</h3>
                            <div class="value">{transactions_total:,}</div>
                            <div class="label">Nombre total</div>
                        </div>
                        <div class="summary-card">
                            <h3>📈 Évolution</h3>
                            <div class="value" style="color: {'#28a745' if evolution_montant > 0 else '#dc3545' if evolution_montant < 0 else '#ffc107'}">
                                {'+' if evolution_montant > 0 else ''}{evolution_montant:.1f}%
                            </div>
                            <div class="label">vs semaine précédente</div>
                        </div>
                        <div class="summary-card">
                            <h3>💳 Ticket Moyen</h3>
                            <div class="value">{current_data.get('montant_moyen_transaction', 0):.0f} €</div>
                            <div class="label">Par transaction</div>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>📈 Historique Hebdomadaire</h2>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Semaine</th>
                                <th>Période</th>
                                <th>Chiffre d'Affaires</th>
                                <th>Transactions</th>
                                <th>Ticket Moyen</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    # Ajouter les données hebdomadaires
    for week in sorted(weeks, reverse=True):
        data = analysis[week]
        html_report += f"""
                            <tr>
                                <td><strong>{week}</strong></td>
                                <td>{data['periode']}</td>
                                <td>{data['montant_total']:,.0f} €</td>
                                <td>{data['transactions_total']:,}</td>
                                <td>{data['montant_moyen_transaction']:.0f} €</td>
                            </tr>
        """
    
    # Points clés et recommandations
    points_cles = []
    recommendations = []
    
    if evolution_montant > 10:
        points_cles.append("✅ Croissance exceptionnelle du chiffre d'affaires")
        recommendations.append("Analyser les facteurs de succès pour les reproduire")
    elif evolution_montant > 5:
        points_cles.append("✅ Progression solide des performances")
        recommendations.append("Maintenir la stratégie commerciale actuelle")
    elif evolution_montant > 0:
        points_cles.append("📊 Croissance modérée")
        recommendations.append("Identifier les leviers d'accélération")
    else:
        points_cles.append("⚠️ Baisse d'activité détectée")
        recommendations.append("Analyser les causes de la baisse et ajuster la stratégie")
    
    if current_data.get('montant_moyen_transaction', 0) > 300:
        points_cles.append("💰 Ticket moyen élevé - Clientèle premium")
        recommendations.append("Développer l'offre haut de gamme")
    elif current_data.get('montant_moyen_transaction', 0) < 150:
        points_cles.append("📱 Ticket moyen accessible - Démocratisation")
        recommendations.append("Optimiser le volume de transactions")
    
    if trends.get('total_weeks', 0) >= 4:
        points_cles.append(f"📊 Analyse sur {trends['total_weeks']} semaines - Données fiables")
        recommendations.append("Planifier les objectifs pour les semaines à venir")
    
    html_report += f"""
                        </tbody>
                    </table>
                </div>

                <div class="section">
                    <h2>🎯 Points Clés</h2>
                    <ul>
    """
    
    for point in points_cles:
        html_report += f"                        <li>{point}</li>\n"
    
    html_report += f"""
                    </ul>
                </div>

                <div class="section">
                    <div class="recommendations">
                        <h2>💡 Recommandations Stratégiques</h2>
                        <ul>
    """
    
    for rec in recommendations:
        html_report += f"                            <li>{rec}</li>\n"
    
    html_report += f"""
                        </ul>
                    </div>
                </div>
            </div>

            <div class="footer">
                <p><strong>🤖 Rapport généré automatiquement par l'Agent IA Bancaire</strong></p>
                <p>📅 Date de génération: {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
                <p>🔄 Prochaine analyse prévue: {(datetime.now() + timedelta(days=7)).strftime('%d/%m/%Y')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_report

def main():
    """Fonction principale."""
    print("📊 GÉNÉRATION DE RAPPORT AVEC VRAIES DONNÉES")
    print("=" * 50)
    
    bank_name = "Banque A"
    weeks = 6  # Analyser 6 semaines
    
    print(f"🏦 Analyse de: {bank_name}")
    print(f"📅 Période: {weeks} dernières semaines")
    
    # Récupérer les données
    print("\n🔍 Récupération des données...")
    weeks_data = get_bank_data(bank_name, weeks)
    
    if not weeks_data:
        print("❌ Aucune donnée disponible")
        return
    
    print(f"✅ Données récupérées pour {len(weeks_data)} semaines")
    
    # Analyser les données
    print("📊 Analyse des tendances...")
    analysis = analyze_weekly_data(weeks_data)
    trends = calculate_trends(analysis)
    
    # Générer le rapport HTML
    print("📝 Génération du rapport HTML...")
    html_report = generate_html_report(bank_name, analysis, trends)
    
    # Envoyer par email
    print("📧 Envoi par email...")
    email_service = EmailService()
    
    result = email_service.send_report_email(
        report=html_report,
        recipients=["cyrjulliard@gmail.com"],
        subject=f"📊 Rapport {bank_name} - Analyse {len(weeks_data)} semaines"
    )
    
    if result.get('sent'):
        print("✅ Rapport envoyé avec succès !")
        print("📧 Vérifiez votre boîte email")
        
        # Afficher un résumé
        current_week = sorted(analysis.keys())[-1]
        current_data = analysis[current_week]
        print(f"\n📈 RÉSUMÉ EXÉCUTIF:")
        print(f"   💰 CA semaine {current_week}: {current_data['montant_total']:,.0f} €")
        print(f"   🔄 Transactions: {current_data['transactions_total']:,}")
        print(f"   💳 Ticket moyen: {current_data['montant_moyen_transaction']:.0f} €")
        print(f"   📈 Évolution: {trends.get('evolution_montant', 0):+.1f}%")
    else:
        print(f"❌ Échec de l'envoi: {result.get('message')}")

if __name__ == "__main__":
    main() 
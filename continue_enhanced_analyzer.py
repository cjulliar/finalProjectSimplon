#!/usr/bin/env python3
"""
🔄 CONTINUATION ANALYSEUR SÉQUENTIEL ENRICHI
============================================

Script de continuation pour finir le traitement séquentiel enrichi
avec correction de l'erreur de division par zéro.
"""

import sqlite3
import pandas as pd
import json
import uuid
from datetime import datetime
from pathlib import Path
import statistics

class ContinueEnhancedAnalyzer:
    def __init__(self):
        self.db_path = "bankreports.db"
        self.weeks_for_moving_average = 4
        
    def get_database_connection(self):
        return sqlite3.connect(self.db_path)
    
    def get_remaining_weeks(self):
        """Trouve les semaines qui n'ont pas encore été traitées"""
        conn = self.get_database_connection()
        
        # Semaines disponibles
        available_weeks = pd.read_sql("""
            SELECT DISTINCT strftime('%Y-W%W', date) as semaine 
            FROM bank_data 
            WHERE strftime('%Y-W%W', date) >= '2024-W01'
            GROUP BY strftime('%Y-W%W', date)
            HAVING COUNT(DISTINCT agence) = 74
            ORDER BY semaine
        """, conn)['semaine'].tolist()
        
        # Semaines déjà traitées
        processed_weeks = pd.read_sql("""
            SELECT DISTINCT JSON_EXTRACT(analysis_metadata, '$.semaine_analysee') as semaine
            FROM analyses 
            WHERE analysis_metadata LIKE '%enhanced_sequential%'
        """, conn)['semaine'].tolist()
        
        conn.close()
        
        # Semaines restantes
        remaining = [w for w in available_weeks if w not in processed_weeks]
        
        return available_weeks, remaining
    
    def get_week_statistics(self, agence, semaine):
        conn = self.get_database_connection()
        
        try:
            query = """
            SELECT agence, date, montant, nombre_transactions, created_at
            FROM bank_data 
            WHERE agence = ? AND strftime('%Y-W%W', date) = ?
            ORDER BY date
            """
            
            cursor = conn.cursor()
            cursor.execute(query, (agence, semaine))
            data = cursor.fetchall()
            
            if not data:
                return None
                
            total_montant = sum(row[2] for row in data)
            total_transactions = sum(row[3] for row in data)
            nombre_jours = len(data)
            montant_moyen_jour = total_montant / nombre_jours if nombre_jours > 0 else 0
            transactions_moyenne_jour = total_transactions / nombre_jours if nombre_jours > 0 else 0
            
            montants = [row[2] for row in data]
            pic_montant = max(montants) if montants else 0
            creux_montant = min(montants) if montants else 0
            
            return {
                'agence': agence,
                'semaine': semaine,
                'periode': f"{data[0][1]} à {data[-1][1]}" if data else "N/A",
                'nombre_jours_activite': nombre_jours,
                'montant_total': total_montant,
                'nombre_transactions_total': total_transactions,
                'montant_moyen_jour': montant_moyen_jour,
                'transactions_moyenne_jour': transactions_moyenne_jour,
                'pic_montant': pic_montant,
                'creux_montant': creux_montant
            }
            
        finally:
            conn.close()
    
    def get_moving_average_context(self, agence, current_week, weeks_list):
        current_index = weeks_list.index(current_week)
        start_index = max(0, current_index - self.weeks_for_moving_average + 1)
        context_weeks = weeks_list[start_index:current_index + 1]
        
        context_stats = []
        for week in context_weeks:
            stats = self.get_week_statistics(agence, week)
            if stats:
                context_stats.append(stats)
        
        if not context_stats:
            return None
        
        avg_montant = statistics.mean([s['montant_total'] for s in context_stats])
        avg_transactions = statistics.mean([s['nombre_transactions_total'] for s in context_stats])
        
        # Calcul de tendance
        n = len(context_stats)
        montants = [s['montant_total'] for s in context_stats]
        
        if n > 1:
            x_values = list(range(n))
            sum_x = sum(x_values)
            sum_y = sum(montants)
            sum_xy = sum(x * y for x, y in zip(x_values, montants))
            sum_x2 = sum(x * x for x in x_values)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            trend_percentage = (slope / avg_montant * 100) if avg_montant > 0 else 0
        else:
            trend_percentage = 0
        
        if trend_percentage > 10:
            trend_indicator = "Progression forte"
        elif trend_percentage > 3:
            trend_indicator = "Progression modérée"
        elif trend_percentage > -3:
            trend_indicator = "Stabilité"
        elif trend_percentage > -10:
            trend_indicator = "Déclin modéré"
        else:
            trend_indicator = "Déclin préoccupant"
        
        return {
            'weeks_analyzed': len(context_stats),
            'period_covered': f"{context_weeks[0]} à {context_weeks[-1]}",
            'avg_montant': avg_montant,
            'avg_transactions': avg_transactions,
            'trend_percentage': trend_percentage,
            'trend_indicator': trend_indicator
        }
    
    def get_previous_analysis(self, agence, previous_week):
        conn = self.get_database_connection()
        
        try:
            query = """
            SELECT report, analysis_metadata, created_at
            FROM analyses 
            WHERE analysis_metadata LIKE ? AND analysis_metadata LIKE ?
            ORDER BY created_at DESC
            LIMIT 1
            """
            
            cursor = conn.cursor()
            cursor.execute(query, (f'%{agence}%', f'%{previous_week}%'))
            result = cursor.fetchone()
            
            if result:
                report, metadata_str, created_at = result
                try:
                    metadata = json.loads(metadata_str)
                    return {
                        'rapport': report,
                        'metadata': metadata,
                        'date_creation': created_at
                    }
                except:
                    return None
            
            return None
            
        finally:
            conn.close()
    
    def calculate_evolution(self, current_stats, previous_stats):
        if not previous_stats:
            return {
                'evolution_montant': 0,
                'evolution_transactions': 0,
                'tendance': 'Pas de données de comparaison',
                'performance': 'N/A'
            }
        
        evolution_montant = ((current_stats['montant_total'] - previous_stats['montant_total']) / previous_stats['montant_total'] * 100) if previous_stats['montant_total'] > 0 else 0
        evolution_transactions = ((current_stats['nombre_transactions_total'] - previous_stats['nombre_transactions_total']) / previous_stats['nombre_transactions_total'] * 100) if previous_stats['nombre_transactions_total'] > 0 else 0
        
        if evolution_montant > 15:
            tendance = "Forte progression"
        elif evolution_montant > 5:
            tendance = "Progression modérée"
        elif evolution_montant > -5:
            tendance = "Stabilité relative"
        elif evolution_montant > -15:
            tendance = "Déclin modéré"
        else:
            tendance = "Forte baisse"
        
        if evolution_montant > 10 and evolution_transactions > 10:
            performance = "Excellente amélioration"
        elif evolution_montant > 0 and evolution_transactions > 0:
            performance = "Amélioration positive"
        elif evolution_montant > -10 and evolution_transactions > -10:
            performance = "Performance stable"
        else:
            performance = "Dégradation préoccupante"
        
        return {
            'evolution_montant': evolution_montant,
            'evolution_transactions': evolution_transactions,
            'tendance': tendance,
            'performance': performance
        }
    
    def generate_corrected_analysis(self, agence, current_stats, previous_stats, moving_avg_context, evolution, current_week, previous_week):
        """Génère l'analyse avec correction du ticket moyen"""
        
        montant_formatted = f"{current_stats['montant_total']:,.2f} €"
        
        # Correction pour éviter division par zéro
        ticket_moyen = (current_stats['montant_total'] / current_stats['nombre_transactions_total']) if current_stats['nombre_transactions_total'] > 0 else 0.00
        
        # Analyse de l'évolution
        if evolution['evolution_montant'] > 10:
            evolution_text = f"une forte progression de {evolution['evolution_montant']:+.1f}%"
            recommandation = "Capitaliser sur cette dynamique positive."
        elif evolution['evolution_montant'] > 0:
            evolution_text = f"une progression de {evolution['evolution_montant']:+.1f}%"
            recommandation = "Consolider cette amélioration."
        elif evolution['evolution_montant'] > -10:
            evolution_text = f"une légère baisse de {evolution['evolution_montant']:+.1f}%"
            recommandation = "Analyser les causes et ajuster la stratégie."
        else:
            evolution_text = f"une baisse significative de {evolution['evolution_montant']:+.1f}%"
            recommandation = "Plan d'action d'urgence nécessaire."
        
        # Contexte tendanciel
        if moving_avg_context:
            position_vs_moyenne = ((current_stats['montant_total'] - moving_avg_context['avg_montant']) / moving_avg_context['avg_montant'] * 100)
            if position_vs_moyenne > 10:
                contexte_text = f"se positionne {position_vs_moyenne:+.1f}% au-dessus de sa moyenne mobile"
            elif position_vs_moyenne > -10:
                contexte_text = f"reste proche de sa moyenne mobile ({position_vs_moyenne:+.1f}%)"
            else:
                contexte_text = f"se situe {position_vs_moyenne:+.1f}% sous sa moyenne mobile"
        else:
            contexte_text = "manque de données pour le contexte tendanciel"
        
        analysis = f"""RAPPORT D'ANALYSE SÉQUENTIELLE ENRICHIE - AGENCE {agence}
Période : {current_stats['periode']} (Semaine {current_week})
Référence : Semaine {previous_week}
Contexte : {moving_avg_context['period_covered'] if moving_avg_context else 'N/A'}
Destinataire : Direction Générale

RÉSUMÉ EXÉCUTIF - ÉVOLUTION {previous_week}→{current_week}
L'agence {agence} affiche {evolution_text} de son volume d'activité avec {montant_formatted} en semaine {current_week}. Cette évolution traduit {evolution['performance'].lower()} dans un contexte où l'agence {contexte_text}.

PERFORMANCE SEMAINE {current_week}
Volume total réalisé : {montant_formatted} sur {current_stats['nombre_jours_activite']} jours
Transactions traitées : {current_stats['nombre_transactions_total']} opérations
Performance quotidienne : {current_stats['montant_moyen_jour']:,.2f} € en moyenne
Fréquence transactionnelle : {current_stats['transactions_moyenne_jour']:.1f} transactions/jour
Ticket moyen : {ticket_moyen:,.2f} €

ANALYSE COMPARATIVE IMMÉDIATE (vs {previous_week})
Le volume d'activité évolue de {evolution['evolution_montant']:+.1f}% par rapport à la semaine précédente.
L'activité transactionnelle progresse de {evolution['evolution_transactions']:+.1f}%.
Cette évolution classe la performance comme "{evolution['performance'].lower()}".

CONTEXTUALISATION TENDANCIELLE
Sur les {moving_avg_context['weeks_analyzed'] if moving_avg_context else 'N/A'} dernières semaines, l'agence présente une tendance "{moving_avg_context['trend_indicator'] if moving_avg_context else 'indéterminée'}". La performance actuelle {contexte_text}.

NOUVELLES RECOMMANDATIONS ADAPTÉES
{recommandation} L'analyse enrichie recommande de prendre en compte la tendance globale "{moving_avg_context['trend_indicator'] if moving_avg_context else 'à déterminer'}" pour ajuster la stratégie.

CONCLUSION ET OBJECTIFS SEMAINE SUIVANTE
L'agence {agence} doit {"maintenir cette dynamique" if evolution['evolution_montant'] > 5 else "améliorer ses performances" if evolution['evolution_montant'] > -5 else "redresser ses résultats"} pour la semaine suivante."""

        return analysis
    
    def save_enhanced_analysis(self, agence, analysis, current_stats, evolution, moving_avg_context, current_week, previous_week):
        conn = self.get_database_connection()
        
        try:
            analysis_id = str(uuid.uuid4())
            user_id = 1
            created_at = datetime.now()
            
            query_parameters = {
                'agence_id': agence,
                'semaine': current_week,
                'semaine_reference': previous_week,
                'type_rapport': 'enhanced_sequential_analysis',
                'source': 'ai_agent_sequential_enriched'
            }
            
            analysis_metadata = {
                'type': 'ai_generated_enhanced_sequential',
                'agence': agence,
                'semaine_analysee': current_week,
                'semaine_reference': previous_week,
                'approach': 'sequential_enriched_option_b',
                'generation_method': 'direct_ai_agent_enhanced_corrected',
                'montant_total': current_stats['montant_total'],
                'evolution_montant': evolution['evolution_montant'],
                'evolution_transactions': evolution['evolution_transactions'],
                'performance': evolution['performance'],
                'tendance_immediate': evolution['tendance'],
                'moving_avg_weeks': moving_avg_context['weeks_analyzed'] if moving_avg_context else 0,
                'trend_indicator': moving_avg_context['trend_indicator'] if moving_avg_context else 'N/A',
                'trend_percentage': moving_avg_context['trend_percentage'] if moving_avg_context else 0,
                'word_count': len(analysis.split()),
                'generated_at': datetime.now().isoformat(),
                'is_enhanced_sequential': True
            }
            
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analyses (id, user_id, created_at, query_parameters, report, analysis_metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                analysis_id,
                user_id,
                created_at,
                json.dumps(query_parameters),
                analysis,
                json.dumps(analysis_metadata)
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Erreur sauvegarde pour {agence}: {e}")
            return False
        finally:
            conn.close()
    
    def continue_processing(self):
        """Continue le traitement des semaines restantes"""
        print("🔄 CONTINUATION ANALYSEUR SÉQUENTIEL ENRICHI")
        print("=" * 60)
        
        all_weeks, remaining_weeks = self.get_remaining_weeks()
        
        if not remaining_weeks:
            print("✅ Toutes les semaines ont déjà été traitées !")
            return
        
        print(f"📅 Semaines restantes à traiter: {len(remaining_weeks)}")
        print(f"🎯 Depuis: {remaining_weeks[0]} jusqu'à: {remaining_weeks[-1]}")
        
        base_dir = Path("enhanced_sequential_analysis")
        analyses_dir = base_dir / "generated_analyses"
        analyses_dir.mkdir(parents=True, exist_ok=True)
        
        total_processed = 0
        total_saved = 0
        
        for current_week in remaining_weeks:
            previous_week = all_weeks[all_weeks.index(current_week) - 1]
            
            print(f"\n📍 TRAITEMENT SEMAINE {current_week}")
            print(f"   Référence: {previous_week}")
            
            # Récupérer les agences
            conn = self.get_database_connection()
            agencies_df = pd.read_sql(
                "SELECT DISTINCT agence FROM bank_data WHERE strftime('%Y-W%W', date) = ? ORDER BY agence", 
                conn, params=[current_week]
            )
            conn.close()
            
            agencies = agencies_df['agence'].tolist()
            week_processed = 0
            week_saved = 0
            
            for agence in agencies:
                current_stats = self.get_week_statistics(agence, current_week)
                
                if current_stats:
                    previous_stats = self.get_week_statistics(agence, previous_week)
                    moving_avg_context = self.get_moving_average_context(agence, current_week, all_weeks)
                    previous_analysis = self.get_previous_analysis(agence, previous_week)
                    evolution = self.calculate_evolution(current_stats, previous_stats)
                    
                    # Générer analyse corrigée
                    analysis = self.generate_corrected_analysis(
                        agence, current_stats, previous_stats, moving_avg_context, 
                        evolution, current_week, previous_week
                    )
                    
                    # Sauvegarder analyse
                    safe_name = "".join(c for c in agence if c.isalnum() or c in (' ', '-', '_')).strip()
                    safe_week = current_week.replace('-', '_')
                    analysis_file = analyses_dir / f"{safe_week}_analysis_{safe_name}.txt"
                    
                    with open(analysis_file, 'w', encoding='utf-8') as f:
                        f.write(analysis)
                    
                    # Sauvegarder en BDD
                    if self.save_enhanced_analysis(agence, analysis, current_stats, evolution, moving_avg_context, current_week, previous_week):
                        week_saved += 1
                    
                    week_processed += 1
            
            total_processed += week_processed
            total_saved += week_saved
            
            print(f"   ✅ {week_processed} agences traitées, {week_saved} sauvegardées en BDD")
        
        print(f"\n🎯 RÉSUMÉ CONTINUATION:")
        print(f"═══════════════════════════════════════")
        print(f"✅ Semaines complétées: {len(remaining_weeks)}")
        print(f"📊 Total analyses générées: {total_processed}")
        print(f"💾 Total sauvegardées en BDD: {total_saved}")


def main():
    analyzer = ContinueEnhancedAnalyzer()
    analyzer.continue_processing()


if __name__ == "__main__":
    main()
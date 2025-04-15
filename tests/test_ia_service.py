#!/usr/bin/env python3
"""
Tests pour le service d'IA.
"""
import os
import sys
import unittest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importer le service d'IA
from src.ia.ai_service import AIAnalysisService


class TestAIAnalysisService(unittest.TestCase):
    """Tests pour le service d'analyse IA."""
    
    def setUp(self):
        """Préparation des tests."""
        # Forcer l'utilisation du mode fallback pour éviter les appels API réels
        self.service = AIAnalysisService(use_alternative_api=True)
        
        # Générer des données de test
        self.test_data = self._generate_test_data()
    
    def _generate_test_data(self):
        """Générer un DataFrame de test."""
        # Créer 3 agences avec 10 jours de données chacune
        agences = ["Agence A", "Agence B", "Agence C"]
        dates = [(datetime.now() - timedelta(days=i)).date() for i in range(10)]
        
        data = []
        for agence in agences:
            for date in dates:
                # Générer des valeurs aléatoires mais reproductibles
                np.random.seed(int(date.strftime("%Y%m%d")) + hash(agence) % 10000)
                montant = np.random.uniform(1000, 10000)
                transactions = np.random.randint(10, 100)
                
                data.append({
                    "agence": agence,
                    "date": date,
                    "montant": montant,
                    "nombre_transactions": transactions
                })
        
        return pd.DataFrame(data)
    
    def test_prepare_prompt(self):
        """Tester la génération du prompt."""
        prompt = self.service._prepare_prompt(self.test_data)
        
        # Vérifier que le prompt contient les éléments essentiels
        self.assertIn("STATISTIQUES GLOBALES", prompt)
        self.assertIn("STATISTIQUES PAR AGENCE", prompt)
        self.assertIn("Agence A", prompt)
        self.assertIn("Agence B", prompt)
        self.assertIn("Agence C", prompt)
        self.assertIn("Montant total:", prompt)
        self.assertIn("Transactions totales:", prompt)
        self.assertIn("INSTRUCTIONS", prompt)
    
    def test_generate_fallback_report(self):
        """Tester la génération d'un rapport de secours."""
        prompt = self.service._prepare_prompt(self.test_data)
        report = self.service._generate_fallback_report(prompt)
        
        # Vérifier que le rapport contient les sections attendues
        self.assertIn("# Rapport d'Analyse Bancaire Hebdomadaire", report)
        self.assertIn("## Introduction", report)
        self.assertIn("## Analyse des Performances par Agence", report)
        self.assertIn("## Recommandations Stratégiques", report)
        self.assertIn("## Conclusion", report)
    
    def test_generate_visualizations(self):
        """Tester la génération des visualisations."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Définir le dossier de sortie temporaire
            original_dir = os.getcwd()
            os.chdir(tmp_dir)
            
            try:
                # Générer les visualisations
                visualizations = self.service._generate_visualizations(self.test_data)
                
                # Vérifier que les visualisations ont été générées
                self.assertEqual(len(visualizations), 3)
                
                # Vérifier les types de visualisations
                viz_types = [viz["type"] for viz in visualizations]
                self.assertIn("bar_chart", viz_types)
                self.assertIn("line_chart", viz_types)
                
                # Vérifier que les fichiers existent
                for viz in visualizations:
                    self.assertTrue(os.path.exists(viz["path"]))
            finally:
                # Restaurer le répertoire de travail
                os.chdir(original_dir)
    
    def test_analyze_bank_data(self):
        """Tester l'analyse complète des données bancaires."""
        result = self.service.analyze_bank_data(self.test_data)
        
        # Vérifier que la réponse contient les éléments attendus
        self.assertIn("report", result)
        self.assertIn("visualizations", result)
        self.assertIn("metadata", result)
        
        # Vérifier les métadonnées
        metadata = result["metadata"]
        self.assertEqual(metadata["data_points"], len(self.test_data))
        self.assertEqual(len(metadata["agencies"]), 3)
        
        # Vérifier les visualisations
        self.assertEqual(len(result["visualizations"]), 3)
        
        # Vérifier que le rapport n'est pas vide
        self.assertTrue(len(result["report"]) > 100)
    
    def test_analyze_bank_data_from_list(self):
        """Tester l'analyse avec une liste de dictionnaires au lieu d'un DataFrame."""
        data_list = self.test_data.to_dict('records')
        result = self.service.analyze_bank_data(data_list)
        
        # Vérifier que la réponse contient les éléments attendus
        self.assertIn("report", result)
        self.assertIn("visualizations", result)
        self.assertIn("metadata", result)
        
        # Vérifier les métadonnées
        metadata = result["metadata"]
        self.assertEqual(metadata["data_points"], len(data_list))
    
    def test_missing_columns(self):
        """Tester la gestion des colonnes manquantes."""
        # Créer un DataFrame sans les colonnes requises
        bad_data = pd.DataFrame({
            "agence": ["Agence A"],
            "date": [datetime.now().date()],
            # Manque "montant" et "nombre_transactions"
        })
        
        # Vérifier que l'exception est levée
        with self.assertRaises(ValueError):
            self.service.analyze_bank_data(bad_data)
    
    def test_empty_data(self):
        """Tester la gestion des données vides."""
        # Créer un DataFrame vide mais avec les bonnes colonnes
        empty_data = pd.DataFrame(columns=["agence", "date", "montant", "nombre_transactions"])
        
        # Vérifier que l'analyse fonctionne mais produit un résultat par défaut
        result = self.service.analyze_bank_data(empty_data)
        self.assertIn("report", result)
        self.assertEqual(result["metadata"]["data_points"], 0)


if __name__ == "__main__":
    unittest.main() 
#!/usr/bin/env python3
"""
Script de test pour vérifier que les templatetags sont bien reconnus
"""

import os
import sys
import django

# Configuration Django
sys.path.append('frontend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')
django.setup()

def test_templatetags():
    """Test que les templatetags sont bien reconnus"""
    
    print("🔧 TEST DES TEMPLATETAGS")
    print("=" * 50)
    
    try:
        # Test du filtre email_filters
        from dashboard.templatetags.email_filters import format_email_content
        print("✅ email_filters.format_email_content importé avec succès")
        
        # Test du filtre math_filters
        from dashboard.templatetags.math_filters import format_number, format_currency
        print("✅ math_filters.format_number et format_currency importés avec succès")
        
        # Test de fonctionnement
        test_content = "Bonjour\n\nTest de contenu\n\nAvec des retours à la ligne"
        formatted = format_email_content(test_content)
        print(f"✅ format_email_content fonctionne: {len(formatted)} caractères générés")
        
        test_number = 1234567.89
        formatted_number = format_number(test_number)
        print(f"✅ format_number fonctionne: {test_number} -> {formatted_number}")
        
        formatted_currency = format_currency(test_number)
        print(f"✅ format_currency fonctionne: {test_number} -> {formatted_currency}")
        
        print("\n🎉 TOUS LES TEMPLATETAGS FONCTIONNENT CORRECTEMENT!")
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur de test: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_templatetags()
    if success:
        print("\n✅ Les templatetags sont prêts à être utilisés dans les templates!")
        print("🌐 Vous pouvez maintenant accéder au site sur http://localhost:8080")
    else:
        print("\n❌ Il y a un problème avec les templatetags") 
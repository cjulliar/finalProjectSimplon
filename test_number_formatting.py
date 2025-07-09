#!/usr/bin/env python3
"""
Script de test pour vérifier le formatage des nombres
"""

import os
import sys
import django

# Configuration Django
sys.path.append('frontend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')
django.setup()

from templatetags.math_filters import format_number, format_currency, format_percentage

def test_number_formatting():
    """Test le formatage des nombres"""
    
    print("🔢 TEST DU FORMATAGE DES NOMBRES")
    print("=" * 50)
    
    # Tests de formatage
    test_cases = [
        (1883565.27, "1 883 565,27"),
        (1234567.89, "1 234 567,89"),
        (1000000, "1 000 000,00"),
        (1234.56, "1 234,56"),
        (0.1234, "0,12"),
        (None, "0"),
        ("invalid", "invalid"),
    ]
    
    print("📊 Tests format_number:")
    for input_val, expected in test_cases:
        result = format_number(input_val)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {input_val} -> {result} (attendu: {expected})")
    
    print("\n💰 Tests format_currency:")
    currency_tests = [
        (1883565.27, "1 883 565,27 €"),
        (1234.56, "1 234,56 €"),
    ]
    
    for input_val, expected in currency_tests:
        result = format_currency(input_val)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {input_val} -> {result} (attendu: {expected})")
    
    print("\n📈 Tests format_percentage:")
    percentage_tests = [
        (0.1567, "15,67%"),
        (0.5, "50,00%"),
        (1.0, "100,00%"),
    ]
    
    for input_val, expected in percentage_tests:
        result = format_percentage(input_val)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {input_val} -> {result} (attendu: {expected})")
    
    print("\n✅ Tests terminés!")

if __name__ == "__main__":
    test_number_formatting() 
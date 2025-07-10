#!/usr/bin/env python3
"""
Script de test pour vérifier le formatage des emails
"""

import os
import sys
import django
import sqlite3

# Configuration Django
sys.path.append('frontend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')
django.setup()

from templatetags.email_filters import format_email_content

def test_email_formatting():
    """Test le formatage d'un email"""
    
    # Connexion à la base de données
    conn = sqlite3.connect('bankreports.db')
    cursor = conn.cursor()
    
    # Récupérer un email de test
    cursor.execute("""
        SELECT content FROM email_reports 
        WHERE bank_name = 'Banque_A' 
        ORDER BY sent_at DESC 
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    if not result:
        print("❌ Aucun email trouvé pour Banque_A")
        return
    
    content = result[0]
    print("📧 EMAIL BRUT:")
    print("=" * 50)
    print(content[:500] + "...")
    print("\n" + "=" * 50)
    
    # Tester le formatage
    print("\n🎨 EMAIL FORMATÉ:")
    print("=" * 50)
    formatted = format_email_content(content)
    print(formatted[:1000] + "...")
    
    # Sauvegarder le résultat dans un fichier pour inspection
    with open('test_email_formatted.html', 'w', encoding='utf-8') as f:
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test Email Formaté</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Test de Formatage Email</h1>
        <h2>Contenu brut:</h2>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px;">{content[:500]}...</pre>
        
        <h2>Contenu formaté:</h2>
        {formatted}
    </div>
</body>
</html>
        """)
    
    print(f"\n✅ Résultat sauvegardé dans 'test_email_formatted.html'")
    print(f"🌐 Ouvrez ce fichier dans votre navigateur pour voir le résultat")
    
    conn.close()

if __name__ == "__main__":
    test_email_formatting() 
from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter(name='format_email_content')
def format_email_content(content):
    """
    Convertit le contenu d'email brut en HTML formaté
    """
    if not content:
        return ""
    
    # Convertir les retours à la ligne en <br> et <p>
    lines = content.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Détecter les titres principaux (lignes en majuscules)
        if re.match(r'^[A-Z\s\-_]+$', line) and len(line) > 3 and len(line) < 50:
            formatted_lines.append(f'<h3 style="color: #2c3e50; margin: 25px 0 15px 0; border-bottom: 3px solid #3498db; padding-bottom: 8px; font-size: 1.4em;">{line}</h3>')
        # Détecter les sous-titres (commençant par des emojis)
        elif re.match(r'^[📊📈👥💼🎯🏆]', line):
            formatted_lines.append(f'<h4 style="color: #34495e; margin: 20px 0 10px 0; font-weight: 600; font-size: 1.2em;">{line}</h4>')
        # Détecter les titres de sections (commençant par "Analyse", "Synthèse", etc.)
        elif re.match(r'^(Analyse|Synthèse|Particuliers|Professionnels|Recommandations)', line, re.IGNORECASE):
            formatted_lines.append(f'<h4 style="color: #2c3e50; margin: 20px 0 10px 0; background-color: #ecf0f1; padding: 8px 12px; border-radius: 5px; font-weight: 600;">{line}</h4>')
        # Détecter les listes (commençant par des chiffres ou des tirets)
        elif re.match(r'^\d+\.', line) or line.startswith('-') or line.startswith('•'):
            formatted_lines.append(f'<li style="margin: 8px 0; padding-left: 5px;">{line}</li>')
        # Détecter les montants (lignes contenant €)
        elif '€' in line and re.search(r'\d+', line):
            formatted_lines.append(f'<p style="margin: 12px 0; line-height: 1.6; font-weight: 500; color: #27ae60; background-color: #f8f9fa; padding: 8px 12px; border-radius: 4px; border-left: 4px solid #27ae60;">{line}</p>')
        # Détecter les paragraphes normaux
        else:
            formatted_lines.append(f'<p style="margin: 12px 0; line-height: 1.6;">{line}</p>')
    
    # Grouper les éléments de liste
    html_content = ""
    in_list = False
    
    for line in formatted_lines:
        if '<li>' in line:
            if not in_list:
                html_content += '<ul style="margin: 15px 0; padding-left: 25px; list-style-type: disc;">'
                in_list = True
            html_content += line
        else:
            if in_list:
                html_content += '</ul>'
                in_list = False
            html_content += line
    
    if in_list:
        html_content += '</ul>'
    
    # Ajouter des styles CSS pour améliorer la présentation
    styled_content = f'''
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 100%;">
        {html_content}
    </div>
    '''
    
    return mark_safe(styled_content)

@register.filter(name='extract_metadata')
def extract_metadata(content):
    """
    Extrait les métadonnées du contenu email
    """
    if not content:
        return {}
    
    # Chercher les métadonnées dans les commentaires HTML
    metadata_match = re.search(r'<!-- METADATA: ({.*?}) -->', content, re.DOTALL)
    if metadata_match:
        try:
            import json
            metadata_str = metadata_match.group(1)
            return json.loads(metadata_str)
        except:
            pass
    
    return {} 
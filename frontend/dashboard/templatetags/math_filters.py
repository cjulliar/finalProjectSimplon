from django import template
import locale

register = template.Library()

@register.filter(name='format_number')
def format_number(value):
    """
    Formate un nombre avec des espaces pour les milliers
    Exemple: 1883565.27 -> 1 883 565,27
    """
    if value is None:
        return "0"
    
    try:
        # Convertir en float
        float_value = float(value)
        
        # Formatage manuel - toujours afficher 2 décimales
        parts = f"{float_value:.2f}".split('.')
        integer_part = f"{int(parts[0]):,}".replace(',', ' ')
        return f"{integer_part},{parts[1]}"
            
    except (ValueError, TypeError):
        return str(value)

@register.filter(name='format_currency')
def format_currency(value):
    """
    Formate un montant en euros avec symbole
    Exemple: 1883565.27 -> 1 883 565,27 €
    """
    formatted = format_number(value)
    return f"{formatted} €"

@register.filter(name='format_percentage')
def format_percentage(value):
    """
    Formate un pourcentage
    Exemple: 0.1567 -> 15,67%
    """
    if value is None:
        return "0%"
    
    try:
        percentage = float(value) * 100
        return f"{percentage:.2f}%".replace('.', ',')
    except (ValueError, TypeError):
        return f"{value}%" 
from django import template
import sys


register = template.Library()


@register.filter(name='incremento_iva')
def incremento_iva(value):
    """Incrementa el valor en un 19%."""
    try:
        original_value = value
        value = value * 1.19
        print(f"Aplicando incremento_iva: {original_value} -> {value}", file=sys.stderr)
        return value
    except (ValueError, TypeError) as e:
        print(f"Error aplicando incremento_iva a {value}: {e}", file=sys.stderr)
        return value
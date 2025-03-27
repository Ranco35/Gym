from django import template

register = template.Library()

@register.filter
def sum_weights(sets):
    """Calcula la suma total de pesos en las series."""
    return sum(set.weight for set in sets)

@register.filter
def subtract(value, arg):
    """Resta el argumento del valor."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def abs_value(value):
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0

@register.filter
def get_item(dictionary, key):
    """
    Obtiene un elemento de un diccionario usando una clave.
    Uso en template: {{ dictionary|get_item:key }}
    """
    try:
        return dictionary.get(key, 0)
    except (AttributeError, TypeError):
        return 0 
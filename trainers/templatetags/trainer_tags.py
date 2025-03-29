from django import template
from django.db.models import Count

register = template.Library()

@register.filter
def get_item(list_or_dict, i):
    """
    Obtiene un elemento de una lista por su índice, restando 1 para que sea basado en 1 en lugar de 0.
    Ejemplo: {{ my_list|get_item:1 }} devolverá el primer elemento de la lista.
    
    También funciona con diccionarios: {{ my_dict|get_item:'key' }}
    """
    try:
        # Si se trata de un índice numérico, restar 1 para hacerlo basado en 1
        if isinstance(i, int) or i.isdigit():
            i = int(i) - 1
            
        return list_or_dict[i]
    except (IndexError, KeyError, TypeError):
        return None 

@register.filter
def completed_sets_count(queryset, set_id):
    """Contar cuántas series se han completado para un ejercicio específico"""
    return queryset.filter(set_id=set_id).count()

@register.filter
def filter_count(qs):
    """Contar elementos en un queryset filtrado"""
    return qs.count() if qs else 0

@register.filter
def multiply(value, arg):
    """Multiplicar un valor por un factor"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """Dividir un valor por otro"""
    try:
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, TypeError):
        return 0 
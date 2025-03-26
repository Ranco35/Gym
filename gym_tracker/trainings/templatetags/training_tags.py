from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Filtro para obtener un elemento de un diccionario por su clave.
    Uso en template: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key, []) 
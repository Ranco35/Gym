from django import template

register = template.Library()

@register.filter(name='filter_active')
def filter_active(sessions):
    """
    Filtra las sesiones activas (no finalizadas).
    
    Args:
        sessions: QuerySet o lista de sesiones
        
    Returns:
        Lista de sesiones activas (ended_at es None)
    """
    if not sessions:
        return []
    return [session for session in sessions if session.ended_at is None] 
from django import template

register = template.Library()

@register.filter
def filter_difficulty(exercises, difficulty):
    """
    Filtra los ejercicios por nivel de dificultad
    """
    if not exercises:
        return []
    return [exercise for exercise in exercises if exercise.difficulty == difficulty] 
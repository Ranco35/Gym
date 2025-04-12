from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from ..models import Training, Set
from ..forms import SetForm
from gym_tracker.exercises.models import Exercise

@login_required
@require_POST
def delete_set(request, set_id):
    """
    Elimina un set de un entrenamiento.
    """
    set_obj = get_object_or_404(Set, pk=set_id)
    
    # Verificar que el usuario es el propietario
    if set_obj.training.user != request.user:
        return JsonResponse({'error': 'No tienes permiso para eliminar este set'}, status=403)
    
    # Guardar referencias para redirigir después de eliminar
    training_id = set_obj.training.id
    
    # Eliminar set
    set_obj.delete()
    
    # Si la solicitud es AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'set_id': set_id
        })
    
    # Si no, redirigir a la vista de sesión
    return redirect('trainings:training-session', training_id=training_id)

@login_required
def edit_set(request, set_id):
    """
    Edita un set de un entrenamiento.
    """
    set_obj = get_object_or_404(Set, pk=set_id)
    
    # Verificar que el usuario es el propietario
    if set_obj.training.user != request.user:
        return JsonResponse({'error': 'No tienes permiso para editar este set'}, status=403)
    
    if request.method == 'POST':
        # Obtener datos del formulario
        reps = request.POST.get('reps', set_obj.reps)
        weight = request.POST.get('weight', set_obj.weight)
        notes = request.POST.get('notes', set_obj.notes)
        
        # Actualizar el set
        set_obj.reps = reps
        set_obj.weight = weight
        set_obj.notes = notes
        set_obj.save()
        
        # Si la solicitud es AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'set_id': set_obj.id,
                'exercise_name': set_obj.exercise.name,
                'set_number': set_obj.set_number,
                'reps': reps,
                'weight': weight,
                'notes': notes
            })
        
        # Si no, redirigir a la vista de sesión
        return redirect('trainings:training-session', training_id=set_obj.training.id)
    
    # Si no es un método POST, mostrar formulario
    form = SetForm(instance=set_obj)
    
    return render(request, 'trainings/edit_set.html', {
        'form': form,
        'set': set_obj,
        'training': set_obj.training
    }) 
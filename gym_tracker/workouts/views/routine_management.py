from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from ..models import WeeklyRoutine, RoutineDay
from trainers.models import TrainerTraining

# Función de verificación para comprobar si un usuario es administrador o superusuario
def is_admin_or_superuser(user):
    return user.is_authenticated and (user.role == 'ADMIN' or user.is_superuser)

@login_required
def edit_routine(request, pk):
    """
    Vista para editar una rutina existente.
    """
    routine = get_object_or_404(WeeklyRoutine, pk=pk, user=request.user)
    days_of_week = WeeklyRoutine.DAYS_OF_WEEK
    
    if request.method == 'POST':
        # Obtener datos del formulario
        routine_name = request.POST.get('routine_name', 'Mi Rutina Semanal')
        routine_description = request.POST.get('routine_description', '')
        selected_days = request.POST.getlist('days')
        
        # Actualizar la rutina existente
        routine.name = routine_name
        routine.description = routine_description
        routine.save()
        
        # Obtener los días actuales y crear un diccionario para facilitar la búsqueda
        current_days = {day.day_of_week: day for day in routine.days.all()}
        
        # Crear nuevos días si no existen
        for day_name in selected_days:
            if day_name not in current_days:
                # Crear un nuevo día
                RoutineDay.objects.create(
                    routine=routine,
                    day_of_week=day_name,
                    focus="Por definir"
                )
        
        # Añadir un mensaje de éxito
        messages.success(request, "Rutina actualizada correctamente.")
        
        # Redirigir a la vista de detalle
        return redirect('workouts:routine-detail', pk=routine.id)
    
    # Obtener los días seleccionados actualmente
    selected_days = [day.day_of_week for day in routine.days.all()]
    
    return render(request, 'workouts/routine_edit.html', {
        'routine': routine,
        'days_of_week': days_of_week,
        'selected_days': selected_days
    })

@login_required
def delete_routine(request, pk):
    """
    Elimina una rutina completa.
    Solo administradores o superusuarios pueden eliminar rutinas.
    """
    # Verificar si el usuario es administrador o superusuario
    if not is_admin_or_superuser(request.user):
        messages.error(request, "No tienes permisos para eliminar rutinas. Esta acción solo está permitida para administradores.")
        return redirect('workouts:routine-list')
    
    routine = get_object_or_404(WeeklyRoutine, pk=pk)
    
    if request.method == 'POST':
        # Guardar el nombre para mostrar en mensaje de confirmación
        routine_name = routine.name
        # Eliminar la rutina
        routine.delete()
        messages.success(request, f"La rutina '{routine_name}' ha sido eliminada.")
        return redirect('workouts:routine-list')
    
    # Si no es un método POST, mostrar página de confirmación
    return render(request, 'workouts/routine_confirm_delete.html', {
        'routine': routine
    })

@login_required
def view_assigned_routine(request, pk):
    """
    Vista de acceso directo para ver la rutina asignada.
    """
    try:
        # Intentar obtener la rutina con el ID proporcionado
        routine = TrainerTraining.objects.get(id=pk)
    except TrainerTraining.DoesNotExist:
        messages.error(request, f"No se encontró la rutina con ID {pk}.")
        return redirect('workouts:routine-list')
    
    trainer_info = {
        'name': routine.created_by.get_full_name() or routine.created_by.username,
        'date_assigned': routine.created_at
    }
    
    return render(request, 'workouts/routine_detail.html', {
        'routine': routine,
        'is_assigned_routine': True,
        'trainer_info': trainer_info
    }) 
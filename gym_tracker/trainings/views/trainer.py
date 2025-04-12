from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from trainers.models import LiveTrainingSession, TrainerStudent, TrainerTraining, TrainerTrainingDay, TrainerSet

@login_required
def assigned_training_detail(request, training_id):
    """
    Muestra los detalles de un entrenamiento asignado por un entrenador.
    """
    training = get_object_or_404(TrainerTraining, pk=training_id, user=request.user)
    
    # Obtener los días de entrenamiento
    days = training.days.all().order_by('day_of_week')
    
    # Obtener información del entrenador
    trainer_info = {
        'name': training.created_by.get_full_name() or training.created_by.username,
        'date_assigned': training.created_at
    }
    
    return render(request, 'trainings/assigned_training_detail.html', {
        'training': training,
        'days': days,
        'trainer_info': trainer_info
    })

@login_required
def create_training_session(request):
    """
    Crea una nueva sesión de entrenamiento en vivo.
    """
    if request.method == 'POST':
        # Obtener datos del formulario
        trainer_id = request.POST.get('trainer_id')
        date = request.POST.get('date')
        time = request.POST.get('time')
        duration = request.POST.get('duration', 60)  # Duración en minutos, por defecto 60
        
        # Crear la sesión de entrenamiento
        session = LiveTrainingSession.objects.create(
            trainer_id=trainer_id,
            user=request.user,
            date=date,
            time=time,
            duration=duration
        )
        
        messages.success(request, "Sesión de entrenamiento creada correctamente.")
        return redirect('trainings:training-list')
    
    # Obtener los entrenadores disponibles
    trainers = TrainerStudent.objects.filter(student=request.user).select_related('trainer')
    
    return render(request, 'trainings/create_training_session.html', {
        'trainers': trainers
    })

@login_required
def edit_user_training(request, pk):
    """
    Edita un entrenamiento asignado por un entrenador.
    """
    training = get_object_or_404(TrainerTraining, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Obtener datos del formulario
        name = request.POST.get('name', training.name)
        notes = request.POST.get('notes', training.notes)
        
        # Actualizar el entrenamiento
        training.name = name
        training.notes = notes
        training.save()
        
        messages.success(request, "Entrenamiento actualizado correctamente.")
        return redirect('trainings:assigned-training-detail', training_id=training.id)
    
    return render(request, 'trainings/edit_user_training.html', {
        'training': training
    }) 
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

from ..models import UserProfile

@login_required
def profile_edit(request):
    """
    Edita el perfil del usuario.
    """
    # Obtener o crear el perfil del usuario
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Obtener datos del formulario
        height = request.POST.get('height', '')
        weight = request.POST.get('weight', '')
        birth_date = request.POST.get('birth_date', '')
        gender = request.POST.get('gender', '')
        goal = request.POST.get('goal', '')
        
        # Actualizar el perfil
        if height:
            profile.height = height
        if weight:
            profile.weight = weight
        if birth_date:
            profile.birth_date = birth_date
        if gender:
            profile.gender = gender
        if goal:
            profile.goal = goal
        
        # Procesar imagen de perfil si se proporciona
        if 'profile_image' in request.FILES:
            profile_image = request.FILES['profile_image']
            
            # Procesar la imagen con Pillow
            img = Image.open(profile_image)
            
            # Redimensionar si es necesario
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
            
            # Guardar la imagen procesada
            buffer = BytesIO()
            img.save(buffer, format='JPEG')
            profile.profile_image.save(
                f'profile_{request.user.id}.jpg',
                ContentFile(buffer.getvalue()),
                save=False
            )
        
        profile.save()
        messages.success(request, "Perfil actualizado correctamente.")
        return redirect('trainings:dashboard')
    
    return render(request, 'trainings/profile_edit.html', {
        'profile': profile
    }) 
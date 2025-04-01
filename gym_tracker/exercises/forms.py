from django import forms
from .models import Exercise, ExerciseCategory
from django.core.exceptions import ValidationError

class ExerciseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExerciseCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la categoría'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción breve de la categoría'}),
        }
        labels = {
            'name': 'Nombre',
            'description': 'Descripción',
        }
        help_texts = {
            'name': 'Nombre único para la categoría de ejercicios',
            'description': 'Descripción opcional de la categoría',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        # Verificar si el nombre ya existe (para crear) o si ha cambiado (para actualizar)
        if self.instance.pk:
            # Estamos actualizando
            if ExerciseCategory.objects.exclude(pk=self.instance.pk).filter(name__iexact=name).exists():
                raise forms.ValidationError("Ya existe una categoría con este nombre.")
        else:
            # Estamos creando
            if ExerciseCategory.objects.filter(name__iexact=name).exists():
                raise forms.ValidationError("Ya existe una categoría con este nombre.")
        
        return name 

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = [
            'name', 
            'slug',
            'description',
            'muscle_group',
            'primary_muscles',
            'secondary_muscles', 
            'tips', 
            'equipment', 
            'difficulty', 
            'video_url',
            'image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'muscle_group': forms.Select(attrs={'class': 'form-select'}),
            'primary_muscles': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Pectorales, Deltoides anterior'
            }),
            'secondary_muscles': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Tríceps, Deltoides medio'
            }),
            'tips': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Consejos adicionales para mejorar la ejecución del ejercicio'
            }),
            'equipment': forms.TextInput(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.youtube.com/watch?v=...'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return image
            
        # Si es una instancia existente, retornarla sin validación
        if hasattr(image, 'instance'):
            return image
            
        # Para nuevas imágenes
        if image:
            # Verificar el tamaño (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('La imagen no debe exceder 5MB.')
                
            # Verificar la extensión
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            import os
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError('Por favor sube una imagen válida. Los formatos permitidos son: ' + ', '.join(valid_extensions))
                
        return image 
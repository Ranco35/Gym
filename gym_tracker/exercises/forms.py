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
            'name', 'description', 'category', 'difficulty',
            'primary_muscles', 'secondary_muscles', 'equipment',
            'instructions', 'tips', 'image', 'youtube_link'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'instructions': forms.Textarea(attrs={'rows': 4}),
            'tips': forms.Textarea(attrs={'rows': 3}),
            'youtube_link': forms.URLInput(attrs={'placeholder': 'https://www.youtube.com/watch?v=...'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Verificar el tamaño del archivo (máximo 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('El tamaño máximo permitido es 5MB')
            
            # Verificar el formato
            allowed_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image.content_type not in allowed_formats:
                raise ValidationError('Solo se permiten archivos JPG, PNG, GIF o WEBP')
        
        return image 
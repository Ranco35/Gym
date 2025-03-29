from django import forms
from .models import Exercise, ExerciseCategory

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
from django import forms
from .models import Exercise

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'description', 'instructions', 'tips', 'category', 'equipment', 'difficulty', 'youtube_link', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe paso a paso cómo realizar el ejercicio correctamente'
            }),
            'tips': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Consejos adicionales para mejorar la ejecución del ejercicio'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'equipment': forms.Select(attrs={'class': 'form-select'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'youtube_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.youtube.com/watch?v=...'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        } 
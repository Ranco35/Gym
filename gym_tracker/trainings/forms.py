from django import forms
from .models import Training, Set

class TrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        fields = ['exercise', 'date', 'total_sets', 'reps', 'weight', 'rest_time', 'intensity', 'notes', 'completed']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'intensity': forms.Select(choices=[
                ('Bajo', 'Bajo'),
                ('Moderado', 'Moderado'),
                ('Alto', 'Alto'),
                ('Máximo', 'Máximo')
            ])
        }

class SetForm(forms.ModelForm):
    class Meta:
        model = Set
        fields = ['weight', 'reps', 'completed']
        widgets = {
            'weight': forms.NumberInput(attrs={'step': '0.5', 'min': '0'}),
            'reps': forms.NumberInput(attrs={'min': '0'})
        } 
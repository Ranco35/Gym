# Generated by Django 5.0.2 on 2025-03-29 15:29

import django.db.models.deletion
import gym_tracker.exercises.models
from django.db import migrations, models


def create_categories_from_exercises(apps, schema_editor):
    """
    Crear categorías a partir de las categorías existentes en los ejercicios.
    """
    Exercise = apps.get_model('exercises', 'Exercise')
    ExerciseCategory = apps.get_model('exercises', 'ExerciseCategory')
    
    # Obtener todas las categorías únicas de los ejercicios existentes
    existing_categories = set(Exercise.objects.values_list('category', flat=True).distinct())
    
    # Crear las categorías en la base de datos
    for category_name in existing_categories:
        if category_name:  # Evitar categorías vacías o nulas
            ExerciseCategory.objects.get_or_create(name=category_name)
    
    # Asegurarse de que existe la categoría por defecto 'Otros'
    ExerciseCategory.objects.get_or_create(name='Otros')


class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0004_alter_exercise_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExerciseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Categoría de Ejercicio',
                'verbose_name_plural': 'Categorías de Ejercicios',
                'ordering': ['name'],
            },
        ),
        # Ejecutar la función para crear las categorías iniciales
        migrations.RunPython(create_categories_from_exercises),
    ]

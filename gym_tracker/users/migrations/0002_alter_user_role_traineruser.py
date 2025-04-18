# Generated by Django 5.0.4 on 2025-03-25 16:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('USER', 'Usuario'), ('TRAINER', 'Entrenador'), ('ADMIN', 'Administrador General')], default='USER', max_length=10),
        ),
        migrations.CreateModel(
            name='TrainerUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateField(auto_now_add=True)),
                ('activo', models.BooleanField(default=True)),
                ('notas', models.TextField(blank=True)),
                ('trainer', models.ForeignKey(limit_choices_to={'role': 'TRAINER'}, on_delete=django.db.models.deletion.CASCADE, related_name='trainer_users', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(limit_choices_to={'role': 'USER'}, on_delete=django.db.models.deletion.CASCADE, related_name='user_trainers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Relación Entrenador-Usuario',
                'verbose_name_plural': 'Relaciones Entrenador-Usuario',
                'unique_together': {('trainer', 'user')},
            },
        ),
    ]

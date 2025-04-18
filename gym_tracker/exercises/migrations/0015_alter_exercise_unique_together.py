# Generated by Django 5.0.2 on 2025-04-08 00:49

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0014_make_slug_non_nullable'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='exercise',
            unique_together={('name', 'created_by')},
        ),
    ]

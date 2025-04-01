from django.db import migrations
from django.utils.text import slugify

def populate_slugs(apps, schema_editor):
    Exercise = apps.get_model('exercises', 'Exercise')
    for exercise in Exercise.objects.all():
        if not exercise.slug:
            base_slug = slugify(exercise.name)
            slug = base_slug
            counter = 1
            
            # Verificar si el slug ya existe
            while Exercise.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            exercise.slug = slug
            exercise.save()

class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0012_alter_exercise_options_remove_exercise_category_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_slugs),
    ] 
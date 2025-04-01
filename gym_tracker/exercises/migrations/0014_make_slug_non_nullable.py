from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0013_populate_slug_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercise',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, unique=True),
        ),
    ] 
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0015_alter_exercise_unique_together'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL para eliminar la columna
            "ALTER TABLE exercises_exercise DROP COLUMN category_id;",
            # SQL para revertir (si es necesario)
            "ALTER TABLE exercises_exercise ADD COLUMN category_id integer;"
        ),
    ] 
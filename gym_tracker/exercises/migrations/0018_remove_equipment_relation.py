from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0017_remove_category_id_constraint'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL para permitir valores nulos en equipment_id
            "ALTER TABLE exercises_exercise ALTER COLUMN equipment_id DROP NOT NULL;",
            # SQL para revertir (si es necesario)
            "ALTER TABLE exercises_exercise ALTER COLUMN equipment_id SET NOT NULL;"
        ),
        migrations.RunSQL(
            # SQL para eliminar la columna equipment_id
            "ALTER TABLE exercises_exercise DROP COLUMN equipment_id;",
            # SQL para revertir (si es necesario)
            "ALTER TABLE exercises_exercise ADD COLUMN equipment_id integer;"
        ),
    ] 
# Generated by Django 4.1.5 on 2023-01-16 11:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('visita', '0003_alter_resultados_id_intervencion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultados',
            name='id_visita',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='visita.visita'),
        ),
    ]

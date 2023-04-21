# Generated by Django 4.1.5 on 2023-01-24 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cita', '0004_remove_cita_es_paciente'),
    ]

    operations = [
        migrations.AddField(
            model_name='cita',
            name='duracion',
            field=models.IntegerField(choices=[(15, 15), (30, 30), (45, 45), (60, 60), (75, 75), (90, 90), (105, 105), (120, 120), (135, 135), (150, 150), (165, 165), (180, 180)], default=15),
        ),
    ]
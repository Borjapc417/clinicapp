# Generated by Django 4.1.5 on 2023-01-15 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paciente', '0012_paciente_codigo_postal'),
    ]

    operations = [
        migrations.AddField(
            model_name='paciente',
            name='localidad',
            field=models.TextField(default=''),
        ),
    ]

# Generated by Django 4.1.5 on 2023-05-29 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paciente', '0020_alter_historicalpaciente_direccion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpaciente',
            name='codigo_postal',
            field=models.CharField(max_length=5),
        ),
        migrations.AlterField(
            model_name='historicalpaciente',
            name='sexo',
            field=models.CharField(choices=[('masculino', 'masculino'), ('femenino', 'femenino'), ('ninguno', 'ninguno')], default='masculino', max_length=20),
        ),
        migrations.AlterField(
            model_name='paciente',
            name='codigo_postal',
            field=models.CharField(max_length=5),
        ),
        migrations.AlterField(
            model_name='paciente',
            name='sexo',
            field=models.CharField(choices=[('masculino', 'masculino'), ('femenino', 'femenino'), ('ninguno', 'ninguno')], default='masculino', max_length=20),
        ),
    ]
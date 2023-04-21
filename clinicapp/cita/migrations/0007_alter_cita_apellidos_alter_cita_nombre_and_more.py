# Generated by Django 4.1.5 on 2023-02-10 10:19

from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cita', '0006_remove_cita_duracion_cita_fecha_terminacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cita',
            name='apellidos',
            field=django_cryptography.fields.encrypt(models.TextField()),
        ),
        migrations.AlterField(
            model_name='cita',
            name='nombre',
            field=django_cryptography.fields.encrypt(models.TextField()),
        ),
        migrations.AlterField(
            model_name='cita',
            name='telefono',
            field=django_cryptography.fields.encrypt(models.CharField(max_length=12)),
        ),
    ]
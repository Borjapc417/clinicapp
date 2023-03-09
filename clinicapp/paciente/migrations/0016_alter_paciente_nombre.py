# Generated by Django 4.1.5 on 2023-02-09 11:38

from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ('paciente', '0015_paciente_foto_consentimiento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paciente',
            name='nombre',
            field=django_cryptography.fields.encrypt(models.CharField(max_length=50)),
        ),
    ]

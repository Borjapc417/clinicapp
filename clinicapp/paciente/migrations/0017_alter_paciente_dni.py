# Generated by Django 4.1.5 on 2023-02-09 11:41

from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ('paciente', '0016_alter_paciente_nombre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paciente',
            name='dni',
            field=django_cryptography.fields.encrypt(models.CharField(max_length=9, unique=True)),
        ),
    ]

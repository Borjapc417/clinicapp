# Generated by Django 4.1.5 on 2023-01-14 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paciente', '0003_rename_contexto_antecedente_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paciente',
            name='quiere_informacion',
            field=models.BooleanField(default=False),
        ),
    ]
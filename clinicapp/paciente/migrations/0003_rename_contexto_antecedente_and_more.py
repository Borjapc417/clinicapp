# Generated by Django 4.1.5 on 2023-01-14 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paciente', '0002_alter_alergia_nombre_alter_contexto_nombre_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Contexto',
            new_name='Antecedente',
        ),
        migrations.RenameField(
            model_name='paciente',
            old_name='contextos',
            new_name='antecedentes',
        ),
        migrations.AddField(
            model_name='paciente',
            name='quiere_informacion',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='paciente',
            name='vino_de',
            field=models.TextField(default='Web'),
        ),
    ]

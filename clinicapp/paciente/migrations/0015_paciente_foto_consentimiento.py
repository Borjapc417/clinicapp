# Generated by Django 4.1.5 on 2023-01-24 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paciente', '0014_alter_paciente_codigo_postal'),
    ]

    operations = [
        migrations.AddField(
            model_name='paciente',
            name='foto_consentimiento',
            field=models.ImageField(default='/media/imagenes/casa_herborista.jpg', upload_to='imagenes', verbose_name='fotoConsentimiento'),
        ),
    ]
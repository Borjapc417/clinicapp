from django.db import models
from paciente.models import Paciente

class Visita(models.Model):
    fecha = models.DateTimeField()

    MOTIVO = (
        ('informacion', 'informacion'),
        ('medicina familiar', 'medicina familiar'),
        ('consulta', 'consulta'),
        ('revision', 'revision'),

    )
    motivo = models.CharField(
        max_length=20,
        choices=MOTIVO,
        default='informacion',
    )
    
    observaciones_auxiliar = models.TextField()
    observaciones_doctor = models.TextField()
    id_paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)


class Intervencion(models.Model):
    nombre = models.TextField()

    TIPO = (
        ('cirugia', 'cirugia'),
        ('pequeña cirugia', 'pequeña cirugia'),
        ('trat facial', 'trat facial'),
        ('trat corporal', 'trat corporal'),

    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO,
        default='informacion',
    )

class Resultados(models.Model):
    id_visita = models.ForeignKey(Visita, on_delete=models.CASCADE, null = True, blank = True)
    id_intervencion = models.ForeignKey(Intervencion, on_delete=models.CASCADE, null = True, blank = True)
    foto_antes =  models.ImageField(upload_to= 'imagenes', verbose_name='fotoAntes')
    foto_despues = models.ImageField(upload_to= 'imagenes', verbose_name='fotoDespues')
    foto_consentimiento = models.ImageField(upload_to= 'imagenes', verbose_name='fotoConsentimiento')
    foto_etiqueta = models.ImageField(upload_to= 'imagenes', verbose_name='fotoEtiqueta')
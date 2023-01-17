from django.db import models
from paciente.models import Paciente

class Visita(models.Model):
    fecha = models.DateTimeField()

    MOTIVO = (
        ('INFORMACION', 'INFORMACION'),
        ('MEDICINA FAMILIAR', 'MEDICINA FAMILIAR'),
        ('CONSULTA', 'CONSULTA'),
        ('REVISION', 'REVISION'),

    )
    motivo = models.CharField(
        max_length=20,
        choices=MOTIVO,
        default='INFORMACION',
    )
    
    observaciones_auxiliar = models.TextField()
    observaciones_doctor = models.TextField()
    id_paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)


class Intervencion(models.Model):
    nombre = models.TextField(unique = True, null = False, blank = False)

    TIPO = (
        ('CIRUGIA', 'CIRUGIA'),
        ('PEQUEÑA CIRUGIA', 'PEQUEÑA CIRUGIA'),
        ('TRAT FACIAL', 'TRAT FACIAL'),
        ('TRAT CORPORAL', 'TRAT CORPORAL'),

    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO,
        default='PEQUEÑA CIRUGIA',
    )

class Resultados(models.Model):
    id_visita = models.OneToOneField(Visita, on_delete=models.CASCADE, null = False, blank = False)
    id_intervencion = models.ForeignKey(Intervencion, on_delete=models.CASCADE, null = False, blank = False)
    foto_antes =  models.ImageField(upload_to= 'imagenes', verbose_name='fotoAntes')
    foto_despues = models.ImageField(upload_to= 'imagenes', verbose_name='fotoDespues')
    foto_consentimiento = models.ImageField(upload_to= 'imagenes', verbose_name='fotoConsentimiento')
    foto_etiqueta = models.ImageField(upload_to= 'imagenes', verbose_name='fotoEtiqueta')
from django.db import models
from paciente.models import Paciente

class Cita(models.Model):
    fecha_creacion = models.DateTimeField()
    fecha_programada = models.DateTimeField()

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
    
    nombre = models.TextField()
    apellidos = models.TextField()
    telefono = models.CharField(max_length=12)
    es_paciente = models.BooleanField()
    id_paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, blank=True, null=True)

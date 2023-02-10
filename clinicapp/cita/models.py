from django.db import models
from paciente.models import Paciente
from django_cryptography.fields import encrypt

class Cita(models.Model):
    fecha_creacion = models.DateTimeField()

    fecha_programada = models.DateTimeField()
    fecha_terminacion = models.DateTimeField()

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
    
    nombre = encrypt(models.TextField())
    apellidos = encrypt(models.TextField())
    telefono = encrypt(models.CharField(max_length=12))
    id_paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return ''+self.nombre + ', ' + self.apellidos + ' con fecha ' + self.fecha_programada.strftime('%d-%m-%y  %H:%M')+ "-" + self.fecha_terminacion.strftime('%H:%M') + " para " + self.motivo
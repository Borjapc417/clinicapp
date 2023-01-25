from django.db import models
from paciente.models import Paciente

class Cita(models.Model):
    fecha_creacion = models.DateTimeField()

    duraciones = ((15, 15),
                (30, 30),
                (45, 45),
                (60, 60),
                (75, 75),
                (90, 90),
                (105, 105),
                (120, 120),
                (135, 135),
                (150, 150),
                (165, 165),
                (180, 180),
    )

    duracion = models.IntegerField(
        choices=duraciones,
        default=15,
    )
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
    id_paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return ''+self.nombre + ', ' + self.apellidos + ' con fecha ' + self.fecha_programada.strftime('%d-%m-%y  %H:%M')
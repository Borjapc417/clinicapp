from django.db import models
from paciente.models import Paciente
from django_cryptography.fields import encrypt
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import pytz
import re

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

    def clean(self):
        super().clean()
        self.val_duracion()
        self.val_fecha_programada()
        self.val_motivo()
        self.val_telefono()

    def val_fecha_programada(self):
        if(datetime.now(tz=pytz.timezone('Europe/Madrid')) > self.fecha_programada):
            raise ValidationError('La fecha programada debe ser posterior al momento actual')
        

    def val_telefono(self):
        tel_val = re.search("^(?:\+\d{11}|\d{9})$", self.telefono)
        if(tel_val == None):
            raise ValidationError('El telefono no sigue un formato valido. Por ejemplo: 666777888')

    def val_motivo(self):
        motivos = ['INFORMACION', 'MEDICINA FAMILIAR', 'CONSULTA', 'REVISION']
        if self.motivo not in motivos:
            raise ValidationError('El motivo de la cita debe ser uno de los disponibles')

    def val_duracion(self):
        duraciones = [
            15,
            30,
            45,
            60, 
            75, 
            90, 
            105,
            120,
            135,
            150,
            165,
            180,
        ]
        duracion =  (self.fecha_terminacion - self.fecha_programada).total_seconds() / 60
        print(duracion)
        if not duracion in duraciones:
            raise ValidationError('La duracion no es valida')

from django.db import models
from django_cryptography.fields import encrypt
from simple_history.models import HistoricalRecords
import re
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import pytz

class Alergia(models.Model):
    nombre = models.TextField(unique = True)

    def __str__(self):
        return  self.nombre

class Antecedente(models.Model):
    nombre = models.TextField(unique = True)

    def __str__(self):
        return  self.nombre

class Farmaco(models.Model):
    nombre = models.TextField(unique = True)

    def __str__(self):
        return  self.nombre

class Paciente(models.Model):
    dni = encrypt(models.CharField(max_length=9, unique=True, blank=False))
    nombre = encrypt(models.CharField(max_length=50))
    apellidos = encrypt(models.TextField())
    direccion = encrypt(models.TextField())
    fecha_nacimiento = models.DateField()
    telefono = encrypt(models.CharField(max_length = 12))
    email = encrypt(models.EmailField(unique=True, blank=False))
    codigo_postal = models.IntegerField(default=0)
    localidad = models.TextField(default="")


    SEXO = (
        ('masculino', 'masculino'),
        ('femenino', 'femenino'),

    )
    sexo = models.CharField(
        max_length=20,
        choices=SEXO,
        default='masculino',
    )

    COMUNIDADES_AUTONOMAS = (
    ('ANDALUCÍA', 'ANDALUCÍA'),
    ('ARAGÓN', 'ARAGÓN'),
    ('PRINCIPADO DE ASTURIAS', 'PRINCIPADO DE ASTURIAS'),
    ('ISLAS BALEARES', 'ISLAS BALEARES'),
    ('CANARIAS', 'CANARIAS'),
    ('CANTABRIA', 'CANTABRIA'),
    ('CASTILLA-LA MANCHA', 'CASTILLA-LA MANCHA'),
    ('CASTILLA Y LEÓN', 'CASTILLA Y LEÓN'),
    ('CATALUÑA', 'CATALUÑA'),
    ('COMUNIDAD VALENCIANA', 'COMUNIDAD VALENCIANA'),
    ('EXTREMADURA', 'EXTREMADURA'),
    ('GALICIA', 'GALICIA'),
    ('COMUNIDAD DE MADRID', 'COMUNIDAD DE MADRID'),
    ('REGIÓN DE MURCIA', 'REGIÓN DE MURCIA'),
    ('NAVARRA', 'NAVARRA'),
    ('PAÍS VASCO', 'PAÍS VASCO'),
    ('LA RIOJA', 'LA RIOJA'),
    ('CEUTA', 'CEUTA'),
    ('MELILLA', 'MELILLA'),
    )

    comunidad = models.CharField(
        max_length=30,
        choices=COMUNIDADES_AUTONOMAS,
    )

    pais = models.TextField()
    quiere_informacion = models.BooleanField(default = False)
    vino_de = models.TextField(default = "Web")
    alergias = models.ManyToManyField(Alergia)
    antecedentes = models.ManyToManyField(Antecedente)
    prescripciones = models.ManyToManyField(Farmaco, through='Prescripcion')
    foto_consentimiento = models.ImageField(upload_to= 'imagenes', verbose_name='fotoConsentimiento', null=False, default='/media/imagenes/casa_herborista.jpg')
    historia = HistoricalRecords()

    def clean(self):
        super().clean()
        self.validar_dni()
        self.validar_email()
        self.validar_telefono()
        self.validar_codigo_postal()
        self.validar_comunidad()
        self.validar_fecha_nacimiento()

    def validar_dni(self):
        dni_val = re.search("^\d{8}[A-Za-z]$", self.dni)
        if(dni_val == None):
            raise ValidationError('El DNI no sigue un formato valido. Por ejemplo: 12345678A')

    def validar_telefono(self):
        tel_val = re.search("^(?:\+\d{11}|\d{9})$", self.telefono)
        if(tel_val == None):
            raise ValidationError('El telefono no sigue un formato valido. Por ejemplo: 666777888')

    def validar_email(self):
        email_val = re.fullmatch("([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+", self.email)
        if not email_val:
            raise ValidationError('El email no sigue un formato valido. Por ejemplo: prueba@host.com')
        pacientes = Paciente.objects.all()
        paciente_email = []
        for p in pacientes:
            if p.email == self.email and p.dni != self.dni:
                paciente_email.append(p)
        if paciente_email:
            raise ValidationError('El email ya está escogido por otro usuario')


    def validar_fecha_nacimiento(self):
        if((datetime.now(tz=pytz.timezone('Europe/Madrid'))+ timedelta(hours=1)).date() <= self.fecha_nacimiento):
            raise ValidationError('La fecha de nacimiento tiene que ser anterior al día de hoy')

    def validar_comunidad(self):
        comunidades = [
            "ANDALUCÍA",
            "ARAGÓN",
            "PRINCIPADO DE ASTURIAS",
            "ISLAS BALEARES",
            "CANARIAS",
            "CANTABRIA",
            "CASTILLA-LA MANCHA",
            "CASTILLA Y LEÓN",
            "CATALUÑA",
            "COMUNIDAD VALENCIANA",
            "EXTREMADURA",
            "GALICIA",
            "COMUNIDAD DE MADRID",
            "REGIÓN DE MURCIA",
            "NAVARRA",
            "PAÍS VASCO",
            "LA RIOJA",
            "CEUTA",
            "MELILLA"
        ]
        if self.pais == "ESPAÑA" and (self.comunidad == None or self.comunidad not in comunidades):
            raise ValidationError('La comunidad autónoma no es correcta')

    def validar_codigo_postal(self):
        codigo_postal_val = re.search("^\d{5}$", str(self.codigo_postal))
        if self.pais=="ESPAÑA" and codigo_postal_val == None:
            raise ValidationError('El código postal no sigue un formato válido. Por ejemplo: 12345')


    def __str__(self):
        return self.dni + "= " + self.nombre + ", " + self.apellidos

class Prescripcion(models.Model):
    id_paciente = models.ForeignKey(Paciente,on_delete=models.CASCADE)
    id_farmaco = models.ForeignKey(Farmaco,on_delete=models.CASCADE)
    cantidad = models.TextField()
    fechaInicio = models.DateField()
    fechaFin = models.DateField()

    def __str__(self):
        return "" + str(self.id_paciente)  + " -- " + str(self.id_farmaco)  + ": " + self.cantidad
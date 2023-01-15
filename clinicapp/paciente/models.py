from django.db import models


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
    dni = models.CharField(max_length=9, unique=True, blank=False)
    nombre = models.TextField()
    apellidos = models.TextField()
    direccion = models.TextField()
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length = 12)
    email = models.EmailField(unique=True, blank=False)
    codigo_postal = models.IntegerField(default=0)
    localidad = models.TextField(default="")

    SEX = (
        ('masculino', 'masculino'),
        ('femenino', 'femenino'),

    )
    sexo = models.CharField(
        max_length=20,
        choices=SEX,
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
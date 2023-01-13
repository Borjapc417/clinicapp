from django.db import models


class Alergia(models.Model):
    nombre = models.TextField(unique = True)

    def __str__(self):
        return  self.nombre

class Contexto(models.Model):
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

    SEX = (
        ('masculino', 'masculino'),
        ('femenino', 'femenino'),

    )
    sexo = models.CharField(
        max_length=20,
        choices=SEX,
        default='masculino',
    )

    pais = models.TextField()
    comunidad = models.TextField()
    alergias = models.ManyToManyField(Alergia)
    contextos = models.ManyToManyField(Contexto)
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
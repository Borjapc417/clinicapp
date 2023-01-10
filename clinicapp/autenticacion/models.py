from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.TextField()
    apellidos = models.TextField()
    dni = models.CharField(max_length=9)
    email = models.EmailField()

    def __str__(self):
        return self.dni + " = " + self.nombre + ", " + self.apellidos
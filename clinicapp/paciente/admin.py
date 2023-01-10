from django.contrib import admin
from .models import Paciente, Alergia, Contexto, Farmaco

admin.site.register(Paciente)
admin.site.register(Alergia)
admin.site.register(Contexto)
admin.site.register(Farmaco)
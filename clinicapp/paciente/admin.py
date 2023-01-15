from django.contrib import admin
from .models import Paciente, Alergia, Antecedente, Farmaco, Prescripcion

admin.site.register(Paciente)
admin.site.register(Alergia)
admin.site.register(Antecedente)
admin.site.register(Farmaco)
admin.site.register(Prescripcion)
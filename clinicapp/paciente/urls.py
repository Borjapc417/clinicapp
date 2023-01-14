from django.urls import path
from .views import *

urlpatterns = [
    path('', main),
    path('<int:paciente_id>', paciente_detalles),
    path('update/<int:paciente_id>', paciente_actualizar),
    path('add', add_paciente),
    path('alergias/<int:paciente_id>', ver_alergias),
    path('alergias/add/<int:paciente_id>', agregar_alergia_paciente),
    path('alergias/borrar/<int:alergia_id>/<int:paciente_id>', borrar_alergia_paciente),
    path('alergias/add', agregar_alergia),
    path('contexto/<int:paciente_id>', ver_contexto),
    path('contexto/add/<int:paciente_id>', agregar_contexto_paciente),
    path('contexto/borrar/<int:contexto_id>/<int:paciente_id>', borrar_contexto_paciente),
    path('contexto/add', agregar_contexto),
    path('farmacos/<int:paciente_id>', ver_farmacos),
    path('farmacos/add/<int:paciente_id>', agregar_farmacos_paciente),
    path('farmacos/borrar/<int:farmacos_id>/<int:paciente_id>', borrar_farmacos_paciente),
    path('farmacos/add', agregar_farmacos),
    
]
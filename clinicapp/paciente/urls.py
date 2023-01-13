from django.urls import path
from .views import main, paciente_detalles, add_paciente, paciente_actualizar, ver_alergias, agregar_alergia_paciente, borrar_alergia_paciente, agregar_alergia

urlpatterns = [
    path('', main),
    path('<int:paciente_id>', paciente_detalles),
    path('update/<int:paciente_id>', paciente_actualizar),
    path('add', add_paciente),
    path('alergias/<int:paciente_id>', ver_alergias),
    path('alergias/add/<int:paciente_id>', agregar_alergia_paciente),
    path('alergias/borrar/<int:alergia_id>/<int:paciente_id>', borrar_alergia_paciente),
    path('alergias/add', agregar_alergia),
    
    
]
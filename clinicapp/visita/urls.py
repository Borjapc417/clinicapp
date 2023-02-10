from django.urls import path
from .views import *

urlpatterns = [
    path('', main),
    path('intervencion', ver_intervencion),
    path('intervencion/add', add_intervencion),
    path('intervencion/borrar/<int:intervencion_id>', borrar_intervencion),
    path('intervencion/buscar', buscar_intervencion),

    path('buscar/paciente/dni', buscar_visita_por_paciente_dni),
    path('buscar/paciente/intervencion', buscar_visita_por_paciente_intervencion),
    path('buscar/paciente/fecha', buscar_visita_por_paciente_fecha),
    path('<int:visita_id>', ver_visita),
    path('update/auxiliar/<int:visita_id>', update_visita_auxiliar),
    path('update/doctor/<int:visita_id>', update_visita_doctor),
    path('update/fotos/<int:visita_id>', update_visita_fotos),
    path('historia/<int:visita_id>' ,ver_historia_visita),
    path('add', add_visita),
    path('update/<int:visita_id>', update_visita),

]
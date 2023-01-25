from django.urls import path
from .views import *

urlpatterns = [
    path('', main),
    path('add', add),
    path('buscar/fecha', buscar_fecha),
    path('update/<int:cita_id>', editar_citas),
    path('borrar/<int:cita_id>', borrar_citas),
    path('hueco-libre', hueco_libre)
]
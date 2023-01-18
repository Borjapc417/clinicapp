from django.urls import path
from .views import *

urlpatterns = [
    path('', main),
    path('add', add),
    path('buscar/fecha', buscar_fecha),
    path('horas/', cargar_horas),
]
from django.urls import path
from .views import main, paciente_detalles, add_paciente, paciente_actualizar

urlpatterns = [
    path('', main),
    path('<int:paciente_id>', paciente_detalles),
    path('update/<int:paciente_id>', paciente_actualizar),
    path('add', add_paciente),
]
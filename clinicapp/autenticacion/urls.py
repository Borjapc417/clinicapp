from django.urls import path
from .views import login, index

urlpatterns = [
    path('login/', login),
    path('index/', index),
]
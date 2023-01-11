from django.shortcuts import render
from .models import Paciente
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.template import Context, loader
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, logout, get_user_model
from django.contrib.auth import login as login_django
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
def main(request):
    template = loader.get_template("main.html") 
    pacientes = Paciente.objects.all()
    context = {"pacientes":pacientes}
    return HttpResponse(template.render(context, request))


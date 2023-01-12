from django.shortcuts import render
from .models import Paciente
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.template import Context, loader
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, logout, get_user_model
from django.contrib.auth import login as login_django
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
import re
import datetime

@login_required
def main(request):
    template = loader.get_template("main.html") 
    pacientes = Paciente.objects.all()
    context = {"pacientes":pacientes}
    return HttpResponse(template.render(context, request))

@login_required
def paciente_detalles(request, paciente_id):
    template = loader.get_template("add.html")
    paciente = Paciente.objects.get(id=paciente_id)
    context = {"paciente":paciente}
    return HttpResponse(template.render(context, request))

@login_required
def add_paciente(request):
    template = loader.get_template("add.html")
    if request.method == 'POST':
        print("entra post")
        dni = request.POST['dni']
        nombre = request.POST['nombre']
        apellidos = request.POST['apellidos']
        telefono = request.POST['telefono']
        email = request.POST['email']
        sexo = request.POST['sexo']
        fecha_nacimiento = request.POST['fecha_nacimiento']
        direccion = request.POST['direccion']

        context = {}
        print(dni)

        dni_val = re.search("^[0-9]{8,8}[A-Za-z]$", dni)
        print(dni_val)
        if(dni_val == None):
            context["error"] = "El DNI no coincide con el formato 12345678A"
            return HttpResponse(template.render(context, request))
        
        else:
            tel_val = re.search("^\\+?[1-9][0-9]{7,14}$", telefono)
            print(telefono)
            print(type(telefono))
            print(tel_val)
            if(tel_val == None):
                context["error"] = "El numero de telefono introducido no sigue un formato válido"
                return HttpResponse(template.render(context, request))
            else:
                fecha_val = datetime.datetime.strptime(fecha_nacimiento, '%d-%m-%Y').date()
                if(datetime.datetime.now().date() < fecha_val):
                    context["error"] = "La fecha de nacimiento debe ser anterior al dia de hoy"
                    return HttpResponse(template.render(context, request))
                else:
                    paciente = Paciente(dni=dni, email=email)
                    paciente.nombre = nombre
                    paciente.apellidos = apellidos
                    paciente.telefono = telefono
                    paciente.sexo=sexo
                    paciente.fecha_nacimiento=fecha_val
                    paciente.direccion=direccion
                    print("PACIENTE AÑADIDO")
                    paciente.save()
                    return redirect("/paciente/")

    else:
        context = {}
        return HttpResponse(template.render(context, request))


@login_required
def paciente_actualizar(request, paciente_id):
    if request.method == 'POST':
        paciente = Paciente.objects.get(id=paciente_id)
        dni = request.POST['dni']
        nombre = request.POST['nombre']
        apellidos = request.POST['apellidos']
        telefono = request.POST['telefono']
        email = request.POST['email']
        sexo = request.POST['sexo']
        fecha_nacimiento = request.POST['fecha_nacimiento']
        direccion = request.POST['direccion']
        paciente.nombre = nombre
        paciente.dni = dni
        paciente.apellidos = apellidos
        paciente.telefono = telefono
        paciente.sexo=sexo
        paciente.fecha_nacimiento=datetime.datetime.strptime(fecha_nacimiento, '%d-%m-%Y').date()
        paciente.direccion=direccion
        paciente.save()
        context = {}
        return redirect("/paciente")
    

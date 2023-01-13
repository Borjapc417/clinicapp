from django.shortcuts import render
from django.contrib import messages
from .models import Paciente, Alergia, Contexto, Farmaco
from django.shortcuts import render, get_object_or_404, HttpResponse, HttpResponseRedirect
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

@login_required
def ver_alergias(request, paciente_id):
    template = loader.get_template("add_detalles.html")
    paciente = Paciente.objects.get(id=paciente_id)
    alergias = Alergia.objects.all()
    context = {"paciente":paciente, "todas_alergias":alergias}
    return HttpResponse(template.render(context, request))

@login_required
def agregar_alergia_paciente(request, paciente_id):
    if request.method == 'POST':
        alergia = Alergia.objects.filter(nombre=request.POST['nombre_alergia']).get()
        paciente = Paciente.objects.get(id=paciente_id)
        paciente.alergias.add(alergia)
        return redirect("/paciente/alergias/"+str(paciente_id))

@login_required
def borrar_alergia_paciente(request, alergia_id, paciente_id):
    alergia = Alergia.objects.get(id=alergia_id)
    paciente = Paciente.objects.get(id=paciente_id)
    paciente.alergias.remove(alergia)
    return redirect("/paciente/alergias/"+str(paciente_id))

def agregar_alergia(request):
    if request.method == 'POST':
        nombre = request.POST["nombre"].upper()
        alergia_antigua = Alergia.objects.filter(nombre=nombre)
        print(alergia_antigua)
        if(alergia_antigua.count()):
            messages.error(request, "Esta alergia ya esta en el sistema")            
            next = request.POST['anterior']
            return HttpResponseRedirect(next) 
        else:    
            alergia = Alergia(nombre=nombre)
            alergia.save()
            next = request.POST['anterior']
            return HttpResponseRedirect(next)
    

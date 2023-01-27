from django.shortcuts import render
from django.contrib import messages
from .models import Paciente, Alergia, Antecedente, Farmaco, Prescripcion
from django.shortcuts import render, get_object_or_404, HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, logout, get_user_model
from django.contrib.auth import login as login_django
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
import re
from datetime import datetime, timedelta
import pytz

comunidades = [
    "ANDALUCÍA",
    "ARAGÓN",
    "PRINCIPADO DE ASTURIAS",
    "ISLAS BALEARES",
    "CANARIAS",
    "CANTABRIA",
    "CASTILLA-LA MANCHA",
    "CASTILLA Y LEÓN",
    "CATALUÑA",
    "COMUNIDAD VALENCIANA",
    "EXTREMADURA",
    "GALICIA",
    "COMUNIDAD DE MADRID",
    "REGIÓN DE MURCIA",
    "NAVARRA",
    "PAÍS VASCO",
    "LA RIOJA",
    "CEUTA",
    "MELILLA"
]

@login_required
def todos(request):
    template = loader.get_template("todos.html") 
    pacientes = Paciente.objects.all()
    context = {"pacientes":pacientes}
    return HttpResponse(template.render(context, request))

@login_required
def main(request):
    template = loader.get_template("main.html") 
    context = {}
    return HttpResponse(template.render(context, request))

@login_required
def paciente_detalles(request, paciente_id):
    template = loader.get_template("add.html")
    paciente = Paciente.objects.get(id=paciente_id)
    context = {"paciente":paciente, "comunidades":comunidades}
    return HttpResponse(template.render(context, request))


def validar_dni(dni):
    dni_val = re.search("^[0-9]{8,8}[A-Za-z]$", dni)
    val = False
    if(dni_val == None):
        val = True
    return val

def validar_telefono(telefono):
    tel_val = re.search("^(?:\+\d{11}|\d{9})$", telefono)
    val = False
    if(tel_val == None):
        val = True
    return val

def validar_email(email):
    email_val = re.fullmatch("([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+", email)
    val = True
    if(email_val):
        val = False
    paciente_email = Paciente.objects.filter(email = email)
    if paciente_email:
        val = True

    return val

def validar_fecha_nacimiento(fecha_nacimiento):
    fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').replace(tzinfo=pytz.timezone('Europe/Madrid')).date()
    val = False
    if((datetime.now(tz=pytz.timezone('Europe/Madrid'))+ timedelta(hours=1)).date() <= fecha_nacimiento):
        val = True
    return val

def validar_comunidad(pais, comunidad):
    val = False
    if pais == "ESPAÑA" and (comunidad == None or comunidad not in comunidades):
        val = True
    return val

def validar_codigo_postal(pais, codigo_postal):
    val = False
    codigo_postal_val = re.search("^\d{5}$", str(codigo_postal))
    if pais=="ESPAÑA" and codigo_postal_val == None:
        val = True
    return val

@login_required
def add_paciente(request):
    template = loader.get_template("add.html")
    if request.method == 'POST':
        dni = request.POST.get('dni', "").upper().strip()
        nombre = request.POST.get('nombre', "").upper().strip()
        apellidos = request.POST.get('apellidos', "").upper().strip()
        telefono = request.POST.get('telefono', "").strip()
        email = request.POST.get('email', "").strip()
        sexo = request.POST.get('sexo', "")
        fecha_nacimiento = request.POST.get('fecha_nacimiento', "").strip()
        direccion = request.POST.get('direccion', "").strip()
        pais = request.POST.get('pais', "").upper().strip()
        comunidad = request.POST.get('comunidad', "").upper().strip()  
        codigo_postal = request.POST.get('codigo_postal', "0").strip()
        localidad = request.POST.get('localidad', "").upper().strip()    
        vino_de = request.POST.get('vino_de', "Desconocido").strip()
        quiere_info2 = request.POST.get('quiere_info', True)
        

        if (pais != "ESPAÑA"):
            comunidad = ""
            localidad = ""
            codigo_postal = 0

        if codigo_postal != 0 and codigo_postal != "":
            codigo_postal = int(codigo_postal)

        errores = []

        if  dni == "" or validar_dni(dni):
            errores.append("El DNI no sigue un formato valido. Por ejemplo: 12345678A")
        if fecha_nacimiento == "" or validar_fecha_nacimiento(fecha_nacimiento):
            errores.append("La fecha de nacimiento no puede ser posterior al dia de hoy")
        if telefono == "" or validar_telefono(telefono):
            errores.append("El telefono no sigue un formato valido. Por ejemplo: 666777888")
        if email == "" or validar_email(email):
            errores.append("El email no sigue un formato valido o ya esta escogido por otro paciente. Por ejemplo: ejemplo@gmail.com")
        if pais == "":
            errores.append("Se debe introducir el pais")
        else:
            if validar_comunidad(pais, comunidad):
                errores.append("Como el pais es España se debe introducir una Comunidad Autonoma valida")
            if validar_codigo_postal(pais, codigo_postal):
                errores.append("El codigo postal no tiene 5 digitos exactos")
        if not bool(request.FILES):
            errores.append("Hay que selccionar una foto de consentimiento")
        else:
            foto_consentimiento = request.FILES['foto_consentimiento']
        if sexo == "":
            errores.append("El campo sexo es obligatorio")
        if nombre == "" or apellidos == "":
            errores.append("El nombre y los apeliidos son obligatorio")
        if direccion == "":
            errores.append("La direccion es obligatoria")

        if(quiere_info2 == True):
            quiere_info = False
        else:
            quiere_info = True
        
        context = {}


        if len(errores) > 0:
            context["errores"] = errores
            context["comunidades"] = comunidades
            return HttpResponse(template.render(context, request))
        else:
            fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').replace(tzinfo=pytz.timezone('Europe/Madrid')).date()
            paciente = Paciente(dni=dni, email=email)
            paciente.nombre = nombre
            paciente.apellidos = apellidos
            paciente.telefono = telefono
            paciente.sexo=sexo
            paciente.email = email
            paciente.fecha_nacimiento=fecha_nacimiento
            paciente.direccion=direccion
            paciente.pais=pais
            paciente.comunidad=comunidad
            paciente.codigo_postal=codigo_postal
            paciente.localidad = localidad
            paciente.vino_de = vino_de
            paciente.quiere_informacion = quiere_info
            paciente.foto_consentimiento.save(foto_consentimiento.name, foto_consentimiento)
            paciente.save()
            return redirect("/paciente/")

    else:
        context = {"comunidades":comunidades}
        return HttpResponse(template.render(context, request))


@login_required
def paciente_actualizar(request, paciente_id):
    template = loader.get_template("add.html")
    if request.method == 'POST':
        paciente = Paciente.objects.get(id = paciente_id)
        nombre = request.POST.get('nombre', "").upper().strip()
        apellidos = request.POST.get('apellidos', "").upper().strip()
        telefono = request.POST.get('telefono', "").strip()
        email = request.POST.get('email', "").strip()
        sexo = request.POST.get('sexo', "")
        fecha_nacimiento = request.POST.get('fecha_nacimiento', "").strip()
        direccion = request.POST.get('direccion', "").strip()
        pais = request.POST.get('pais', "").upper().strip()
        comunidad = request.POST.get('comunidad', "").upper().strip()
        codigo_postal = request.POST.get('codigo_postal', "0").strip()
        localidad = request.POST.get('localidad', "").upper()  .strip()  
        vino_de = request.POST.get('vino_de', "Desconocido").strip()
        quiere_info2 = request.POST.get('quiere_info', True)

        if (pais != "ESPAÑA"):
            comunidad = ""
            localidad = ""
            codigo_postal = 0
        errores = []

        if fecha_nacimiento == "" or validar_fecha_nacimiento(fecha_nacimiento):
            errores.append("La fecha de nacimiento no puede ser posterior al dia de hoy")
        if telefono == "" or validar_telefono(telefono):
            errores.append("El telefono no sigue un formato valido. Por ejemplo: 666777888")
        if paciente.email != email:
            if email == "" or validar_email(email):
                errores.append("El email no sigue un formato valido o ya esta escogido por otro paciente. Por ejemplo: ejemplo@gmail.com")
        if pais == "":
            errores.append("Se debe introducir el pais")
        else:
            if validar_comunidad(pais, comunidad):
                errores.append("Como el pais es España se debe introducir una Comunidad Autonoma valida")
            if validar_codigo_postal(pais, codigo_postal):
                errores.append("El codigo postal no tiene 5 digitos exactos")
        if sexo == "":
            errores.append("El campo sexo es obligatorio")
        if nombre == "" or apellidos == "":
            errores.append("El nombre y los apeliidos son obligatorio")
        if direccion == "":
            errores.append("La direccion es obligatoria")

        if(quiere_info2 == True):
            quiere_info = False
        else:
            quiere_info = True
        
        context = {}

        if len(errores) > 0:
            context["errores"] = errores
            context["paciente"] = paciente
            context["comunidades"] = comunidades
            return HttpResponse(template.render(context, request))

        else:
            fecha_nacimiento = datetime.strptime(request.POST["fecha_nacimiento"], '%Y-%m-%d').replace(tzinfo=pytz.timezone('Europe/Madrid')).date()
            paciente.nombre = nombre
            paciente.apellidos = apellidos
            paciente.telefono = telefono
            paciente.sexo=sexo
            paciente.fecha_nacimiento=fecha_nacimiento
            paciente.direccion=direccion
            paciente.pais=pais
            paciente.codigo_postal=codigo_postal
            paciente.email = email
            paciente.localidad = localidad
            paciente.comunidad=comunidad
            paciente.vino_de = vino_de
            paciente.quiere_informacion = quiere_info
            paciente.save()
            return redirect("/paciente/")
    else:
        context = {}
        return HttpResponse(template.render(context, request))


@login_required
def ver_alergias(request, paciente_id):
    template = loader.get_template("add_detalles.html")
    paciente = Paciente.objects.get(id=paciente_id)
    alergias = Alergia.objects.all()
    context = {"paciente":paciente, "todo_autocompletado":alergias, "tipo":"Alergias"}
    return HttpResponse(template.render(context, request))

@login_required
def agregar_alergia_paciente(request, paciente_id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', "").upper().strip()
        alergia = Alergia.objects.filter(nombre=nombre)

        if nombre == "" or not alergia:
            messages.error(request, "No hay alergias en el sistema con ese nombre")
        else:
            alergia = alergia.get()
            paciente = Paciente.objects.get(id=paciente_id)
            paciente.alergias.add(alergia)
        return redirect("/paciente/alergias/"+str(paciente_id))

@login_required
def borrar_alergia_paciente(request, alergia_id, paciente_id):
    alergia = Alergia.objects.get(id=alergia_id)
    paciente = Paciente.objects.get(id=paciente_id)
    paciente.alergias.remove(alergia)
    return redirect("/paciente/alergias/"+str(paciente_id))

@login_required
def agregar_alergia(request):
    if request.method == 'POST':
        nombre = request.POST["nombre"].upper().strip()
        alergia_antigua = Alergia.objects.filter(nombre=nombre)
        if(alergia_antigua.count()):
            messages.error(request, "Esta alergia ya esta en el sistema")            
            next = request.POST['anterior']
            return HttpResponseRedirect(next) 
        else:    
            alergia = Alergia(nombre=nombre)
            alergia.save()
            next = request.POST['anterior']
            return HttpResponseRedirect(next)

@login_required
def ver_antecedente(request, paciente_id):
    template = loader.get_template("add_detalles.html")
    paciente = Paciente.objects.get(id=paciente_id)
    antecedentes = Antecedente.objects.all()
    context = {"paciente":paciente, "todo_autocompletado":antecedentes, "tipo":"Antecedente"}
    return HttpResponse(template.render(context, request))

@login_required
def agregar_antecedente_paciente(request, paciente_id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', "").upper().strip()
        antecedente = Antecedente.objects.filter(nombre=nombre)
        if nombre == "" or not antecedente:
            messages.error(request, "No hay antecedentes en el sistema con ese nombre")
        else:
            antecedente = antecedente.get()
            paciente = Paciente.objects.get(id=paciente_id)
            paciente.antecedentes.add(antecedente)
        return redirect("/paciente/antecedente/"+str(paciente_id))

@login_required
def borrar_antecedente_paciente(request, antecedente_id, paciente_id):
    antecedente = Antecedente.objects.get(id=antecedente_id)
    paciente = Paciente.objects.get(id=paciente_id)
    paciente.antecedentes.remove(antecedente)
    return redirect("/paciente/antecedente/"+str(paciente_id))

@login_required
def agregar_antecedente(request):
    if request.method == 'POST':
        nombre = request.POST["nombre"].upper().strip()
        antecedente_antiguo = Antecedente.objects.filter(nombre=nombre)
        if(antecedente_antiguo.count()):
            messages.error(request, "Este antecedente ya esta en el sistema")            
            next = request.POST['anterior']
            return HttpResponseRedirect(next) 
        else:    
            antecedente = Antecedente(nombre=nombre)
            antecedente.save()
            next = request.POST['anterior']
            return HttpResponseRedirect(next)

@login_required
def ver_farmacos(request, paciente_id):
    template = loader.get_template("add_detalles.html")
    paciente = Paciente.objects.get(id=paciente_id)
    prescripciones = Prescripcion.objects.filter(id_paciente = paciente_id)
    farmacos = Farmaco.objects.all()
    context = {"paciente":paciente, "todo_autocompletado":farmacos, "tipo":"Farmacos", "prescripciones":prescripciones}
    return HttpResponse(template.render(context, request))

@login_required
def agregar_farmacos_paciente(request, paciente_id):
    if request.method == 'POST':
        paciente = Paciente.objects.get(id = paciente_id)
        nombre = request.POST.get('nombre', "").upper().strip()
        farmaco = Farmaco.objects.filter(nombre=nombre)
        
        cantidad = request.POST["cantidad"]
        fecha_inicio_str = request.POST.get("fechaInicio", "")
        fecha_fin_str = request.POST.get("fechaFin", "")

        errores = False

        if nombre == "" or not farmaco:
            errores = True
            messages.error(request, "No hay farmacos en el sistema con ese nombre")
        if fecha_inicio_str == "" or fecha_fin_str == "":
            errores = True
            messages.error(request, "Se deben introducir ambas fechas")
        else:
            fechaInicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').replace(tzinfo=pytz.timezone('Europe/Madrid')).date()
            fechaFin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').replace(tzinfo=pytz.timezone('Europe/Madrid')).date()
            if fechaFin <= fechaInicio:
                errores = True
                messages.error(request, "La fecha de fin debe ser posterior a la de inicio")     

        if cantidad == "":
            errores = True
            messages.error(request, "Se debe introducir una cantidad")       

        if errores == False:
            farmaco = farmaco.get()
            prescripcion = Prescripcion(id_paciente = paciente)
            prescripcion.id_farmaco = farmaco
            prescripcion.cantidad = cantidad
            prescripcion.fechaInicio = fechaInicio
            prescripcion.fechaFin = fechaFin
            prescripcion.save()
        
        return redirect("/paciente/farmacos/"+str(paciente_id))

@login_required
def borrar_farmacos_paciente(request, farmacos_id, paciente_id):
    farmaco = Farmaco.objects.get(id=farmacos_id)
    paciente = Paciente.objects.get(id=paciente_id)
    prescripcion = Prescripcion.objects.filter(id_paciente = paciente, id_farmaco = farmaco)
    prescripcion.delete()
    return redirect("/paciente/farmacos/"+str(paciente_id))

@login_required
def agregar_farmacos(request):
    if request.method == 'POST':
        nombre = request.POST["nombre"].upper().strip()
        farmaco_antiguo = Farmaco.objects.filter(nombre=nombre)
        if(farmaco_antiguo.count()):
            messages.error(request, "Este farmaco ya esta en el sistema")            
            next = request.POST['anterior']
            return HttpResponseRedirect(next) 
        else:    
            farmaco = Farmaco(nombre=nombre)
            farmaco.save()
            next = request.POST['anterior']
            return HttpResponseRedirect(next)

@login_required
def buscar(request):
    template = loader.get_template("todos.html")
    dni = request.POST.get('dni', False)
    if(dni == False):
        apellidos = request.POST.get('apellidos', False)
        paciente = Paciente.objects.filter(apellidos__icontains=apellidos)
    else:
        paciente = Paciente.objects.filter(dni=dni)
    context = {"pacientes":paciente}
    return HttpResponse(template.render(context, request))
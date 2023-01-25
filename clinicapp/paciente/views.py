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
    return val

def validar_fecha_nacimiento(fecha_nacimiento):
    val = False
    if(datetime.now(tz=pytz.timezone('Europe/Madrid'))+ timedelta(hours=1).date() <= fecha_nacimiento):
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
        dni = request.POST['dni'].upper()
        nombre = request.POST['nombre'].upper()
        apellidos = request.POST['apellidos'].upper()
        telefono = request.POST['telefono']
        email = request.POST['email']
        sexo = request.POST['sexo']
        fecha_nacimiento = request.POST['fecha_nacimiento']
        direccion = request.POST['direccion']
        pais = request.POST['pais'].upper()
        comunidad = request.POST.get('comunidad', "").upper()  
        codigo_postal = int(request.POST.get('codigo_postal', 0))
        localidad = request.POST.get('localidad', "").upper()    
        vino_de = request.POST['vino_de']
        quiere_info2 = request.POST.get('quiere_info', True)
        

        if (pais != "ESPAÑA"):
            comunidad = ""
            localidad = ""
            codigo_postal = 0

        fecha_nacimiento = datetime.strptime(request.POST["fecha_nacimiento"], '%Y-%m-%d').replace(tzinfo=pytz.timezone('Europe/Madrid')).date()

        errores = []

        if validar_dni(dni):
            errores.append("El DNI no sigue un formato valido. Por ejemplo: 12345678A")
        if validar_fecha_nacimiento(fecha_nacimiento):
            errores.append("La fecha de nacimiento no puede ser posterior al dia de hoy")
        if validar_telefono(telefono):
            errores.append("El telefono no sigue un formato valido. Por ejemplo: 666777888")
        if validar_email(email):
            errores.append("El email no sigue un formato valido. Por ejemplo: ejemplo@gmail.com")
        if validar_comunidad(pais, comunidad):
            errores.append("Como el pais es España se debe introducir una Comunidad Autonoma valida")
        if validar_codigo_postal(pais, codigo_postal):
            errores.append("El codigo postal no tiene 5 digitos exactos")
        if not bool(request.FILES):
            errores.append("Hay que selccionar una foto de consentimiento")
        else:
            foto_consentimiento = request.FILES['foto_consentimiento']

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
        nombre = request.POST['nombre'].upper()
        apellidos = request.POST['apellidos'].upper()
        telefono = request.POST['telefono']
        email = request.POST['email']
        sexo = request.POST['sexo']
        fecha_nacimiento = request.POST['fecha_nacimiento']
        direccion = request.POST['direccion']
        pais = request.POST['pais'].upper()
        comunidad = request.POST.get('comunidad', "").upper()
        codigo_postal = int(request.POST.get('codigo_postal', 0))
        localidad = request.POST.get('localidad', "").upper() 
        vino_de = request.POST['vino_de']
        quiere_info2 = request.POST.get('quiere_info', True)

        fecha_nacimiento = datetime.strptime(request.POST["fecha_nacimiento"], '%Y-%m-%d').replace(tzinfo=pytz.timezone('Europe/Madrid')).date()
        if (pais != "ESPAÑA"):
            comunidad = ""
            localidad = ""
            codigo_postal = 0

        print(request.POST)
        errores = []

        if validar_fecha_nacimiento(fecha_nacimiento):
            errores.append("La fecha de nacimiento no puede ser posterior al dia de hoy")
        if validar_telefono(telefono):
            errores.append("El telefono no sigue un formato valido. Por ejemplo: 666777888")
        if validar_email(email):
            errores.append("El email no sigue un formato valido. Por ejemplo: ejemplo@gmail.com")
        if validar_comunidad(pais, comunidad):
            errores.append("Como el pais es España se debe introducir una Comunidad Autonoma valida")
        if validar_codigo_postal(pais, codigo_postal):
            errores.append("El codigo postal no tiene 5 digitos exactos")

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
        alergia = Alergia.objects.filter(nombre=request.POST['nombre']).get()
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
        nombre = request.POST["nombre"].upper()
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
        antecedente = Antecedente.objects.filter(nombre=request.POST['nombre']).get()
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
        nombre = request.POST["nombre"].upper()
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
        farmaco = Farmaco.objects.filter(nombre=request.POST['nombre']).get()
        cantidad = request.POST["cantidad"]
        fechaInicio = datetime.strptime(request.POST["fechaInicio"], '%Y-%m-%d').replace(tzinfo=pytz.timezone('Europe/Madrid')).date()
        fechaFin = datetime.strptime(request.POST["fechaFin"], '%Y-%m-%d').replace(tzinfo=pytz.timezone('Europe/Madrid')).date()

        if(fechaFin > fechaInicio):
            prescripcion = Prescripcion(id_paciente = paciente)
            prescripcion.id_farmaco = farmaco
            prescripcion.cantidad = cantidad
            prescripcion.fechaInicio = fechaInicio
            prescripcion.fechaFin = fechaFin
            prescripcion.save()
        else:
            messages.error(request, "La fecha de fin debe ser posterior a la de inicio")            
        return redirect("/paciente/farmacos/"+str(paciente_id))

@login_required
def borrar_farmacos_paciente(request, farmacos_id, paciente_id):
    print(farmacos_id)
    farmaco = Farmaco.objects.get(id=farmacos_id)
    paciente = Paciente.objects.get(id=paciente_id)
    prescripcion = Prescripcion.objects.filter(id_paciente = paciente, id_farmaco = farmaco)
    prescripcion.delete()
    return redirect("/paciente/farmacos/"+str(paciente_id))

@login_required
def agregar_farmacos(request):
    if request.method == 'POST':
        nombre = request.POST["nombre"].upper()
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
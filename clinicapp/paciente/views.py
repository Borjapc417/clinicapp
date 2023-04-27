from django.contrib import messages
from .models import Paciente, Alergia, Antecedente, Farmaco, Prescripcion
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
import pytz
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage

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
    template = loader.get_template("lista_paciente.html") 
    pacientes = Paciente.objects.all().order_by('nombre')
    paginador = Paginator(pacientes, 5)
    numero_pagina = request.GET.get('pag', 1)
    try:
        pagina = paginador.get_page(numero_pagina)
    except EmptyPage:
        pagina = paginador.get_page(1)
    context = {"pacientes":pagina}
    return HttpResponse(template.render(context, request))


def main(request):
    template = loader.get_template("main_paciente.html") 
    context = {}
    return HttpResponse(template.render(context, request))

@login_required
def paciente_detalles(request, paciente_id):
    template = loader.get_template("formulario_paciente.html")
    paciente = Paciente.objects.get(id=paciente_id)
    context = {"paciente":paciente, "comunidades":comunidades}
    return HttpResponse(template.render(context, request))

@login_required
def add_paciente(request):
    template = loader.get_template("formulario_paciente.html")
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
        foto_consentimiento = request.FILES['foto_consentimiento']

        if (pais != "ESPAÑA"):
            comunidad = ""
            localidad = ""
            codigo_postal = 0
        else:
            if comunidad == "" or localidad == "" or codigo_postal == "" or codigo_postal == 0:
                messages.error(request, "La localidad, la comunidad y el código postal son obligatorios en un paciente español")
            else:
                codigo_postal = int(codigo_postal)            

        quiere_info = not quiere_info2
        
        context = {}

        fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').replace(tzinfo=pytz.timezone('Europe/Madrid')).date()
        paciente = Paciente(dni=dni, nombre=nombre, apellidos=apellidos, telefono=telefono, sexo=sexo, email=email, fecha_nacimiento=fecha_nacimiento,
        direccion=direccion, pais=pais, comunidad=comunidad, codigo_postal=codigo_postal, localidad=localidad, vino_de=vino_de, quiere_informacion=quiere_info)
     
        try:
            paciente.clean()
        except ValidationError as e:
            errors = e.error_list
            messages.error(request, errors[0].message)
            context["comunidades"] = comunidades
            return HttpResponse(template.render(context, request))
        
        paciente.foto_consentimiento.save(foto_consentimiento.name, foto_consentimiento)
        paciente._history_date = datetime.now(tz=pytz.timezone('Europe/Madrid'))
        paciente.save()
        paciente.historia.last().delete()
        return redirect("/paciente/")
    else:
        context = {"comunidades":comunidades}
        return HttpResponse(template.render(context, request))


@login_required
def paciente_actualizar(request, paciente_id):
    template = loader.get_template("formulario_paciente.html")
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
        else:
            if comunidad == "" or localidad == "" or codigo_postal == "" or codigo_postal == 0:
                messages.error(request, "La localidad, la comunidad y el código postal son obligatorios en un paciente español")
            else:
                codigo_postal = int(codigo_postal)

        quiere_info = not quiere_info2
        
        context = {}

        fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').replace(tzinfo=pytz.timezone('Europe/Madrid')).date()
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

        try:
            paciente.clean()
        except ValidationError as e:
            errors = e.error_list
            messages.error(request, errors[0].message)
            return redirect("/paciente/"+str(paciente.id))
        
        paciente.save()
        return redirect("/paciente/")
        
    else:
        context = {}
        return HttpResponse(template.render(context, request))


@login_required
def ver_alergias(request, paciente_id):
    template = loader.get_template("formulario_contexto_paciente.html")
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
        else:    
            alergia = Alergia(nombre=nombre)
            alergia.save()
        next = request.POST['anterior']
        return HttpResponseRedirect(next)

@login_required
def ver_antecedente(request, paciente_id):
    template = loader.get_template("formulario_contexto_paciente.html")
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
        else:    
            antecedente = Antecedente(nombre=nombre)
            antecedente.save()
        next = request.POST['anterior']
        return HttpResponseRedirect(next)

@login_required
def ver_farmacos(request, paciente_id):
    template = loader.get_template("formulario_contexto_paciente.html")
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
        else:    
            farmaco = Farmaco(nombre=nombre)
            farmaco.save()
        next = request.POST['anterior']
        return HttpResponseRedirect(next)

@login_required
def buscar(request):
    template = loader.get_template("lista_paciente.html")
    dni = request.GET.get('dni', False)
    paciente = []
    if(dni == False):
        apellidos = request.GET.get('apellidos', False).upper()
        pacientes = Paciente.objects.all()
        for p in pacientes:
            if apellidos in p.apellidos:
                paciente.append(p) 
    else:
        pacientes = Paciente.objects.all()
        for p in pacientes:
            if p.dni == dni:
                paciente.append(p)
    context = {"pacientes":paciente}
    return HttpResponse(template.render(context, request))


@login_required
def ver_historia_paciente(request, paciente_id):
    paciente = Paciente.objects.filter(id = paciente_id)
    if not paciente:
        messages.error(request, "El paciente especificado no ha sido encontrado")
        return redirect("/paciente")
    else:
        paciente = paciente.get()
        historia = paciente.historia.all()
        template = loader.get_template("formulario_paciente.html")
        context = {}
        context["comunidades"] = comunidades
        context["historia"] = historia
        return HttpResponse(template.render(context, request))
from datetime import datetime, timezone
from django.shortcuts import render, get_object_or_404, HttpResponse, HttpResponseRedirect, redirect
from django.template import Context, loader
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Cita
from paciente.models import Paciente 
import json
import re
from django.db.models import F, Value


@login_required
def main(request):
    template = loader.get_template("main_citas.html")
    context = {}
    fecha_hoy = datetime.now().date()
    context["fecha_hoy"] = fecha_hoy
    return HttpResponse(template.render(context, request))


def val_fecha_programada(fecha_programada):
    val = False
    if(datetime.now().replace(tzinfo=timezone.utc) > fecha_programada):
        val = True
    return val

def val_telefono(telefono):
    tel_val = re.search("^(?:\+\d{11}|\d{9})$", telefono)
    val = False
    if(tel_val == None):
        val = True
    return val

def val_motivo(motivo):
    motivos = ['INFORMACION', 'MEDICINA FAMILIAR', 'CONSULTA', 'REVISION']
    val = False
    if motivo not in motivos:
        val = True
    return val

duraciones = [15,
                30,
                45,
                60, 
                75, 
                90, 
                105,
                120,
                135,
                150,
                165,
                180,
]

@login_required
def add(request):
    if request.method == 'POST':
        nombre = request.POST.get("nombre", "").upper()
        apellidos = request.POST.get("apellidos", "").upper()
        fecha = request.POST.get("fecha", "")
        horas = request.POST.get("hora", "")
        telefono = request.POST.get("telefono", "")
        motivo = request.POST.get("motivo", "").upper()
        paciente_str = request.POST.get("paciente", "")
        duracion = int(request.POST.get("duracion", "0"))

        errores = False

        if paciente_str != "":
            dni = paciente_str.split(":")[0]
            paciente = Paciente.objects.filter(dni = dni)
            if not paciente:
                errores = True
                messages.error(request, "El paciente seleccionado no existe")
            else: 
                paciente = paciente.get()

        fecha_programada = datetime.strptime(fecha, '%Y-%m-%d')
        hora = int(horas.split(':')[0])
        minuto = int(horas.split(':')[1])
        fecha_programada = fecha_programada.replace(hour=hora, minute=minuto, second=0, microsecond=0, tzinfo=timezone.utc)
        horas_disponibles_filtradas = filtrar_horas(fecha_programada)

        if(val_fecha_programada(fecha_programada)):
            errores = True
            messages.error(request, "La fecha programada debe ser posterior al momento actual")
        if(val_motivo(motivo)):
            errores = True
            messages.error(request, "El motivo de la cita debe ser uno de los disponibles")
        if(val_telefono(telefono)):
            errores = True
            messages.error(request, "El telefono no sigue un formato valido. Por ejemplo: 666777888")
        if duracion not in duraciones:
            errores = True
            messages.error(request, "La duracion no es valida")
        if fecha_programada not in horas_disponibles_filtradas:
            errores = True
            messages.error(request, "La fecha de la cita no esta de entre las disponibles por lo que se pisa con otra cita")

        if errores:
            return redirect('/cita/add')
        else:
            fecha_g = fecha_programada.replace(hour=23, minute=59)
            citas = Cita.objects.filter(fecha_programada__gte = fecha_programada).filter(fecha_programada__lte = fecha_g).order_by("fecha_programada")
            horas_disponibles_list = horas_disponibles(fecha_programada)
            
            pos_duracion = 0
            for i in range (0, len(duraciones)):
                if duraciones[i] == duracion:
                    pos_duracion = i
                    break
            pos_inicio = 0
            for i in range (0, len(horas_disponibles_list)):
                if fecha_programada == horas_disponibles_list[i]:
                    pos_inicio = i
                    break
                        
            fecha_terminacion = horas_disponibles_list[pos_inicio+pos_duracion+1]


            for c in citas:
                if fecha_terminacion > c.fecha_programada:
                    errores = True
                    messages.error(request, "La cita dura demasiado tiempo por lo que se pisa con otra")
                    return redirect('/cita/add')

            cita = Cita()
            cita.nombre = nombre
            cita.apellidos = apellidos
            cita.telefono = telefono
            cita.fecha_creacion = datetime.now()
            cita.fecha_programada = fecha_programada
            cita.motivo = motivo
            cita.duracion = duracion
            if paciente_str != "":
                cita.id_paciente = paciente
            else:
                cita.id_paciente = None
            cita.save()

            return redirect('/cita')
    else:
        template = loader.get_template("add_citas.html")
        context = {}
        pacientes = Paciente.objects.all()
        context["pacientes"] = pacientes
        context["duraciones"] = duraciones
        return HttpResponse(template.render(context, request))


@login_required
def buscar_fecha(request):
    if request.method == 'POST':
        fecha = request.POST.get("fecha", "")
        if(fecha != ""):
            template = loader.get_template("citas.html")
            fecha_l= datetime.strptime(fecha, '%Y-%m-%d')
            fecha_g = datetime.strptime(fecha, '%Y-%m-%d').replace(hour=23, minute=59)
            citas = Cita.objects.filter(fecha_programada__gte = fecha_l).filter(fecha_programada__lte = fecha_g).order_by("fecha_programada")
            context = {}
            context['fecha'] = fecha_l
            context['citas'] = citas
            return HttpResponse(template.render(context, request))
        else:
            messages.error(request, "No se ha introducido fecha")
            return redirect("/cita")



def horas_disponibles(fecha):
    horas = set()
    for i in range(10, 14):
        for j in range(0, 60, 15):
            date = datetime.now()
            date = date.replace(year=fecha.year, month=fecha.month, day=fecha.day, hour=i, minute=j, second=0, microsecond=0, tzinfo=timezone.utc)
            horas.add(date)
    for i in range(16, 20):
        for j in range(0, 60, 15):
            date = datetime.now()
            date = date.replace(year=fecha.year, month=fecha.month, day=fecha.day,hour=i, minute=j, second=0, microsecond=0, tzinfo=timezone.utc)
            horas.add(date)

    return sorted(list(horas))

def filtrar_horas(fecha_l):
    fecha_g = fecha_l.replace(hour=23, minute=59)
    citas = Cita.objects.filter(fecha_programada__gte = fecha_l).filter(fecha_programada__lte = fecha_g)
    
    horas_escogidas = set()
    for cita in citas:
        horas_escogidas.add(cita.fecha_programada)

    horas = horas_disponibles(fecha_l)

    for i in range (0, len(citas)):
        cita = citas[i]
        posicion_hora_inicial = 0
        for j in range (0, len(horas)):
            if horas[j] == cita.fecha_programada:
                posicion_hora_inicial = j
                break

        hora_comodin = datetime.now().replace(year=fecha_l.year, month=fecha_l.month, day=fecha_l.day, hour=13, minute=45, second=0, microsecond=0, tzinfo=timezone.utc)
        
        
        for j in range (posicion_hora_inicial, (posicion_hora_inicial + int(cita.duracion/15)), 1):  
            if horas[posicion_hora_inicial] == hora_comodin:
                horas.pop(posicion_hora_inicial)  
                break
            horas.pop(posicion_hora_inicial)

    return sorted(list(horas))


def cargar_horas(request):
    fecha_l= datetime.strptime(request.GET['fecha'], '%Y-%m-%d')
    ret = filtrar_horas(fecha_l)
    return HttpResponse( json.dumps( ret, indent=4, sort_keys=True, default=str), content_type='application/json' )

@login_required
def editar_citas(request, cita_id):
    cita = Cita.objects.get(id = cita_id)
    if request.method == 'POST':
        nombre = request.POST.get("nombre", "").upper()
        apellidos = request.POST.get("apellidos", "").upper()
        fecha = request.POST.get("fecha", "")
        horas = request.POST.get("hora", "")
        telefono = request.POST.get("telefono", "")
        motivo = request.POST.get("motivo", "").upper()
        paciente_str = request.POST.get("paciente", "")
        duracion = int(request.POST.get("duracion", "0"))
        
        errores = False

        if paciente_str != "":
            dni = paciente_str.split(":")[0]
            paciente = Paciente.objects.filter(dni = dni)
            if not paciente:
                errores = True
                messages.error(request, "El paciente seleccionado no existe")
            else: 
                paciente = paciente.get()


        fecha_programada = datetime.strptime(fecha, '%Y-%m-%d')
        hora = int(horas.split(':')[0])
        minuto = int(horas.split(':')[1])
        fecha_programada = fecha_programada.replace(hour=hora, minute=minuto, second=0, microsecond=0, tzinfo=timezone.utc)
        horas_disponibles_filtradas = filtrar_horas(fecha_programada)

        if(val_fecha_programada(fecha_programada)):
            errores = True
            messages.error(request, "La fecha programada debe ser posterior al momento actual")
        if(val_motivo(motivo)):
            errores = True
            messages.error(request, "El motivo de la cita debe ser uno de los disponibles")
        if(val_telefono(telefono)):
            errores = True
            messages.error(request, "El telefono no sigue un formato valido. Por ejemplo: 666777888")
        if duracion not in duraciones:
            errores = True
            messages.error(request, "La duracion no es valida")
        if ((fecha_programada not in horas_disponibles_filtradas) and (fecha_programada != cita.fecha_programada)):
            errores = True
            messages.error(request, "La fecha de la cita no esta de entre las disponibles por lo que se pisa con otra cita")
        if errores:
            return redirect('/cita/update/'+str(cita_id))
        else:
            fecha_g = fecha_programada.replace(hour=23, minute=59)
            citas = Cita.objects.filter(fecha_programada__gte = fecha_programada).filter(fecha_programada__lte = fecha_g).order_by("fecha_programada")
            horas_disponibles_list = horas_disponibles(fecha_programada)
            
            pos_duracion = 0
            for i in range (0, len(duraciones)):
                if duraciones[i] == duracion:
                    pos_duracion = i
                    break
            pos_inicio = 0
            for i in range (0, len(horas_disponibles_list)):
                if fecha_programada == horas_disponibles_list[i]:
                    pos_inicio = i
                    break
                        
            fecha_terminacion = horas_disponibles_list[pos_inicio+pos_duracion+1]


            for c in citas:
                if c != cita:
                    if fecha_terminacion > c.fecha_programada:
                        errores = True
                        messages.error(request, "La cita dura demasiado tiempo por lo que se pisa con otra")
                        return redirect('/cita/update/'+str(cita_id))

            cita.nombre = nombre
            cita.apellidos = apellidos
            cita.telefono = telefono
            cita.fecha_creacion = datetime.now()
            cita.fecha_programada = fecha_programada
            cita.motivo = motivo
            cita.duracion = duracion
            if paciente_str != "":
                cita.id_paciente = paciente
            else:
                cita.id_paciente = None
            cita.save()

            return redirect('/cita')
    else:
        template = loader.get_template("add_citas.html")
        context = {}
        context["cita"] = cita
        pacientes = Paciente.objects.all()
        context["pacientes"] = pacientes
        context["duraciones"] = duraciones
        return HttpResponse(template.render(context, request))

@login_required
def borrar_citas(request, cita_id):
    cita = Cita.objects.get(id = cita_id).delete()
    return redirect("/cita")
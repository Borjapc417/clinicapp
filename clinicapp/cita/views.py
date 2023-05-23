from datetime import datetime, timezone, timedelta
import pytz
from django.shortcuts import HttpResponse, redirect
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cita
from paciente.models import Paciente 
import json
from django.core.exceptions import ValidationError

huso = 'Europe/Madrid'
formato_fecha = '%Y-%m-%d'

@login_required
def main(request):
    template = loader.get_template("main_cita.html")
    context = {}
    fecha_hoy = datetime.now(tz=pytz.timezone(huso)).replace(tzinfo=pytz.utc).date()
    context["fecha_hoy"] = fecha_hoy
    return HttpResponse(template.render(context, request))

duraciones = [15, 30, 45, 60,  75, 90, 105, 120, 135, 150, 165, 180,]

@login_required
def add(request):
    if request.method == 'POST':
        nombre = request.POST.get("nombre", "").upper().strip()
        apellidos = request.POST.get("apellidos", "").upper().strip()
        fecha = request.POST.get("fecha", "")
        horas = request.POST.get("hora", "")
        telefono = request.POST.get("telefono", "").strip()
        motivo = request.POST.get("motivo", "").upper().strip()
        paciente_str = request.POST.get("paciente", "")
        duracion = int(request.POST.get("duracion", "0"))

        if paciente_str != "":
            dni = paciente_str.split(":")[0]
            pacientes = Paciente.objects.all()
            paciente = []
            for p in pacientes:
                if p.dni == dni:
                    paciente.append(p)
            if not paciente:
                messages.error(request, "El paciente seleccionado no existe")
                return redirect('/cita/add')
            else: 
                paciente = paciente[0]

        fecha_programada = datetime.strptime(fecha, formato_fecha)
        hora = int(horas.split(':')[0])
        minuto = int(horas.split(':')[1])
        fecha_programada = fecha_programada.replace(hour=hora, minute=minuto, second=0, microsecond=0)
        fecha_programada = fecha_programada.replace(tzinfo=pytz.utc)
        fecha_terminacion = fecha_programada + timedelta(minutes=duracion)
        
        cita = Cita()
        cita.nombre = nombre
        cita.apellidos = apellidos
        cita.telefono = telefono
        cita.fecha_creacion = datetime.now(tz=pytz.timezone(huso)).replace(tzinfo=pytz.utc)
        cita.fecha_programada = fecha_programada
        cita.motivo = motivo
        cita.fecha_terminacion = fecha_terminacion
        if paciente_str != "":
            cita.id_paciente = paciente
        else:
            cita.id_paciente = None
        try:
            cita.clean()
            cita.save()
        except ValidationError as e:
            errors = e.error_list
            messages.error(request, errors[0].message)
            return redirect("/cita/add")
        return redirect('/cita')
    else:
        template = loader.get_template("formulario_cita.html")
        context = {}
        pacientes = Paciente.objects.all()
        context["pacientes"] = pacientes
        context["duraciones"] = duraciones

        return HttpResponse(template.render(context, request))


@login_required
def buscar_fecha(request):
    if request.method == 'GET':
        fecha = request.GET.get("fecha", "")
        if(fecha != ""):
            template = loader.get_template("lista_cita.html")
            fecha_l= datetime.strptime(fecha, formato_fecha)
            fecha_g = datetime.strptime(fecha, formato_fecha).replace(hour=23, minute=59)
            citas = Cita.objects.filter(fecha_programada__gte = fecha_l).filter(fecha_programada__lte = fecha_g).order_by("fecha_programada")
            context = {}
            context['fecha'] = fecha_l
            
            context['citas'] = citas
            return HttpResponse(template.render(context, request))
        else:
            messages.error(request, "No se ha introducido fecha")
            return redirect("/cita")

@login_required
def buscar_fecha_medicina_familiar(request):
    if request.method == 'GET':
        fecha = request.GET.get("fecha", "")
        if(fecha != ""):
            template = loader.get_template("lista_cita.html")
            fecha_l= datetime.strptime(fecha, formato_fecha).replace(tzinfo=pytz.utc)
            fecha_g = datetime.strptime(fecha, formato_fecha).replace(hour=23, minute=59).replace(tzinfo=pytz.utc)
            citas = Cita.objects.filter(fecha_programada__gte = fecha_l).filter(fecha_programada__lte = fecha_g).filter(motivo = 'MEDICINA FAMILIAR').order_by("fecha_programada")
            context = {}
            context['fecha'] = fecha_l
            context['citas'] = citas
            return HttpResponse(template.render(context, request))
        else:
            messages.error(request, "No se ha introducido fecha")
            return redirect("/cita")


def hueco_libre(request):
    fecha = request.GET.get("fecha", "")
    horas = request.GET.get("hora", "")
    duracion = int(request.GET.get("duracion", "0"))
    fecha_programada = datetime.strptime(fecha, formato_fecha)
    hora = int(horas.split(':')[0])
    minuto = int(horas.split(':')[1])

    fecha_programada = fecha_programada.replace(hour=hora, minute=minuto, second=0, microsecond=0).replace(tzinfo=pytz.utc)
    fecha_terminacion = fecha_programada + timedelta(minutes=duracion)
    fecha_l = fecha_programada.replace(hour=1, minute=0).replace(tzinfo=pytz.utc)
    fecha_g = fecha_programada.replace(hour=23, minute=59).replace(tzinfo=pytz.utc)
    citas = Cita.objects.filter(fecha_programada__range = (fecha_l, fecha_g)).order_by("fecha_programada")
    
    citas_pisadas = []

    for c in citas:
        if not ((c.fecha_programada < fecha_programada and c.fecha_terminacion <= fecha_programada and c.fecha_programada < fecha_terminacion and c.fecha_terminacion < fecha_terminacion) or (c.fecha_programada > fecha_programada and c.fecha_terminacion > fecha_programada and c.fecha_programada >= fecha_terminacion and c.fecha_terminacion > fecha_terminacion)):
            citas_pisadas.append(c)
    return HttpResponse( json.dumps( citas_pisadas, indent=4, sort_keys=True, default=str), content_type='application/json' )


@login_required
def editar_citas(request, cita_id):
    cita = Cita.objects.get(id = cita_id)
    if request.method == 'POST':
        nombre = request.POST.get("nombre", "").upper().strip()
        apellidos = request.POST.get("apellidos", "").upper().strip()
        fecha = request.POST.get("fecha", "")
        horas = request.POST.get("hora", "")
        telefono = request.POST.get("telefono", "").strip()
        motivo = request.POST.get("motivo", "").upper().strip()
        paciente_str = request.POST.get("paciente", "")
        duracion = int(request.POST.get("duracion", "0"))


        if paciente_str != "":
            dni = paciente_str.split(":")[0]
            pacientes = Paciente.objects.all()
            paciente = []
            for p in pacientes:
                if p.dni == dni:
                    paciente.append(p)
            if not paciente:
                messages.error(request, "El paciente seleccionado no existe")
                return redirect('/cita/update/'+str(cita_id))
            else: 
                paciente = paciente[0]

        fecha_programada = datetime.strptime(fecha, formato_fecha)
        hora = int(horas.split(':')[0])
        minuto = int(horas.split(':')[1])
        fecha_programada = fecha_programada.replace(hour=hora, minute=minuto, second=0, microsecond=0).replace(tzinfo=pytz.utc)
        fecha_terminacion = fecha_programada + timedelta(minutes=duracion)
    
        cita.nombre = nombre
        cita.apellidos = apellidos
        cita.telefono = telefono
        cita.fecha_creacion = datetime.now(tz=pytz.timezone(huso)).replace(tzinfo=pytz.utc)
        cita.fecha_programada = fecha_programada
        cita.motivo = motivo
        cita.fecha_terminacion = fecha_terminacion
        if paciente_str != "":
            cita.id_paciente = paciente
        else:
            cita.id_paciente = None

        try:
            cita.clean()
            cita.save()
        except ValidationError as e:
            errors = e.error_list
            messages.error(request, errors[0].message)
            return redirect("/cita/update/"+str(cita_id))
        return redirect('/cita')

    else:
        template = loader.get_template("formulario_cita.html")
        context = {}
        context["cita"] = cita
        pacientes = Paciente.objects.all()
        context["pacientes"] = pacientes
        context["duraciones"] = duraciones
        duracion_cita = cita.fecha_terminacion - cita.fecha_programada
        context["duracion_cita"] = duracion_cita.total_seconds() / 60
        return HttpResponse(template.render(context, request))

@login_required
def borrar_citas(request, cita_id):
    Cita.objects.get(id = cita_id).delete()
    return redirect("/cita")
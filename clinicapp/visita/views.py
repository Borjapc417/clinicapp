from django.shortcuts import HttpResponse, redirect
from django.template import loader
from .models import Intervencion, Resultados, Visita
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from paciente.models import Paciente
from datetime import datetime
import json
import pytz
import os
from django.core.paginator import Paginator, EmptyPage
from django import forms

TIPO = ['CIRUGIA', 'PEQUEÑA CIRUGIA', 'TRAT FACIAL', 'TRAT CORPORAL']
huso = 'Europe/Madrid'
formato_hora = '%Y-%m-%d'

@login_required
def main(request):
    template = loader.get_template("principal_visita.html")
    context = {}
    intervenciones = Intervencion.objects.all().order_by('nombre')
    context["intervenciones"] = intervenciones
    return HttpResponse(template.render(context, request))

@login_required
def ver_intervencion(request):
    template = loader.get_template("lista_intervenciones_visita.html")
    intervenciones = Intervencion.objects.all()
    paginador = Paginator(intervenciones, 5)
    numero_pagina = request.GET.get('pag', 1)
    try:
        pagina = paginador.get_page(numero_pagina)
    except EmptyPage:
        pagina = paginador.get_page(1)
    context = {}
    context["intervenciones"] = pagina
    context["tipos"] = TIPO
    return HttpResponse(template.render(context, request))

@login_required
def add_intervencion(request):
    if request.method == 'POST':
        nombre = request.POST["nombre"].upper()
        tipo = request.POST["tipo"].upper()
        if tipo in TIPO:
            intervencion_anterior = Intervencion.objects.filter(nombre = nombre)
            if not intervencion_anterior:
                intervencion = Intervencion(nombre=nombre, tipo=tipo)
                intervencion.save()
            else:
                messages.error(request, "Esta intervencion ya está en el sistema")
        else:
            messages.error(request, "El tipo no coincide con ninguno de los disponibles")
        return redirect("/visita/intervencion")

@login_required
def borrar_intervencion(request, intervencion_id):
    intervencion =Intervencion.objects.get(id = intervencion_id)
    intervencion.delete()
    return redirect("/visita/intervencion")

@login_required
def buscar_intervencion(request):
    template = loader.get_template("lista_intervenciones_visita.html")
    intervenciones = Intervencion.objects.filter(nombre__icontains = request.GET.get("nombre", ""))
    context = {}
    context["intervenciones"] = intervenciones
    context["tipos"] = TIPO
    return HttpResponse(template.render(context, request))

@login_required
def buscar_visita_por_paciente_dni(request):
    if request.method == 'GET':
        template = loader.get_template("lista_visita.html")
        dni = request.GET.get("dni", "").upper()
        if dni == "":
            return redirect("/visita")
        else:
            paciente = []
            pacientes = Paciente.objects.all()
            for p in pacientes:
                if p.dni == dni:
                    paciente = p
            if not paciente:
                messages.error(request, "Paciente no encontrado")
                return redirect("/visita")
            else:
                visitas = Visita.objects.filter(id_paciente = paciente).select_related("resultados__id_intervencion").order_by('-fecha')
                context = {}
                context["visitas"] = visitas
                context["paciente"] = paciente
                return HttpResponse(template.render(context, request))

@login_required
def buscar_visita_por_paciente_intervencion(request):
    if request.method == 'GET':
        template = loader.get_template("lista_visita.html")
        intervencion_str = request.GET.get("intervencion", "").upper()
        fecha_i = request.GET.get("fecha_i", "")
        fecha_f = request.GET.get("fecha_f", "")

        if intervencion_str == "" or fecha_i == "" or fecha_f == "":
            return redirect("/visita")
        else:
            fecha_i_d =  datetime.strptime(fecha_i, formato_hora).replace(hour=1, minute=0, second=0, microsecond=0).replace(tzinfo=pytz.timezone(huso))
            fecha_f_d =  datetime.strptime(fecha_f, formato_hora).replace(hour=23, minute=59, second=0, microsecond=0).replace(tzinfo=pytz.timezone(huso))
            intervencion = Intervencion.objects.filter(nombre = intervencion_str)

            if not intervencion:
                messages.error(request, "La intervencion seleccionada no existe en el sistema")
                return redirect("/visita")

            intervencion = intervencion.get()
            visitas = Visita.objects.filter(motivo = "CONSULTA").filter(fecha__range = (fecha_i_d, fecha_f_d))
            resultados = Resultados.objects.filter(id_intervencion=intervencion)
            visitas_filtradas = visitas.filter(id__in=resultados.values("id_visita"))

            context = {}
            context["visitas"] = visitas_filtradas
            context["fecha_i"] = fecha_i_d
            context["fecha_f"] = fecha_f_d
            context["intervencion"] = intervencion_str
            return HttpResponse(template.render(context, request))

@login_required
def buscar_visita_por_paciente_fecha(request):
    if request.method == 'GET':
        fecha_i = request.GET.get("fecha_i", "")
        fecha_f = request.GET.get("fecha_f", "")

        if fecha_i == "" or fecha_f == "":
            return redirect("/visita")
        else:
            fecha_i_d =  datetime.strptime(fecha_i, formato_hora).replace(hour=1, minute=0, second=0, microsecond=0).replace(tzinfo=pytz.timezone(huso))
            fecha_f_d =  datetime.strptime(fecha_f, formato_hora).replace(hour=23, minute=59, second=0, microsecond=0).replace(tzinfo=pytz.timezone(huso))
            
            visitas_filtradas = Visita.objects.filter(fecha__range = (fecha_i_d, fecha_f_d))
            pacientes = visitas_filtradas.values('id_paciente').distinct()

            visitas_lista = []
            for p in pacientes:
                paciente_objeto = Paciente.objects.get(id = p["id_paciente"])
                visita = visitas_filtradas.filter(id_paciente = paciente_objeto).order_by("-fecha").first()
                visitas_lista.append(visita)

            context = {}
            context["visitas"] = visitas_lista
            context["fecha_i"] = fecha_i_d
            context["fecha_f"] = fecha_f_d
            template = loader.get_template("lista_visita.html")
            return HttpResponse(template.render(context, request))

@login_required
def add_visita(request):
    template = loader.get_template("formulario_visita.html")
    if request.method == 'POST':
        visita = Visita()
        dni = request.POST.get("dni", "").upper()
        paciente = None
        pacientes = Paciente.objects.all()
        for p in pacientes:
            if p.dni == dni:
                paciente = p
        if not paciente:
            messages.error(request, "El DNI del paciente introducido no existe")
            return redirect("/visita/add")
        
        motivo = request.POST["motivo"].upper()
        fecha = request.POST.get("fecha_fecha", "")
        horas = request.POST.get("fecha_hora", "")
        if fecha != "" and horas != "":
            fecha = datetime.strptime(fecha, "%Y-%m-%d")
            hora = int(horas.split(':')[0])
            minuto = int(horas.split(':')[1])
            fecha = fecha.replace(hour=hora, minute=minuto, second=0, microsecond=0)
            fecha = fecha.replace(tzinfo=pytz.utc)

            if datetime.now(pytz.timezone(huso)).replace(tzinfo=pytz.utc) >= fecha:
                visita.fecha = fecha
            else:
                messages.error(request, "La fecha no puede ser anterior al momento actual")
                return redirect("/visita/add")
        else:
            visita.fecha = datetime.now(pytz.timezone(huso)).replace(second=0, microsecond=0).replace(tzinfo=pytz.utc)

        visita.id_paciente = paciente
        visita.motivo=motivo
        visita._history_date = datetime.now(pytz.timezone(huso)).replace(tzinfo=pytz.utc)
        if motivo == "CONSULTA":
            intervencion_nombre = request.POST.get("intervencion", "").upper()
            if intervencion_nombre != "":
                intervencion = Intervencion.objects.filter(nombre = intervencion_nombre)
                if intervencion:
                    visita.save()
                    intervencion = intervencion.get()
                    resultados = Resultados(id_visita = visita, id_intervencion = intervencion)
                    resultados.save()
                else:
                    messages.error(request, "La intervencion seleccionada no esta guardada en el sistema")
                    return redirect("/visita/add")
        
        visita.save()
        return redirect("/visita")
    else:
        context = {}
        intervenciones = Intervencion.objects.all()
        context["intervenciones"] = intervenciones
        return HttpResponse(template.render(context, request))
        
@login_required
def update_visita(request, visita_id):
    template = loader.get_template("formulario_visita.html")
    if request.method == 'POST':
        visita = Visita.objects.get(id = visita_id)

        dni = request.POST.get("dni", "").upper()
        motivo = request.POST["motivo"].upper()
        fecha = request.POST.get("fecha_fecha", "")
        horas = request.POST.get("fecha_hora", "")
        intervencion_nombre = request.POST.get("intervencion", "").upper()

        if fecha != "" and horas != "":
            fecha = datetime.strptime(fecha, "%Y-%m-%d")
            hora = int(horas.split(':')[0])
            minuto = int(horas.split(':')[1])
            fecha = fecha.replace(hour=hora, minute=minuto, second=0, microsecond=0)
            fecha = fecha.replace(tzinfo=pytz.utc)
        else:
            fecha = datetime.now(pytz.timezone(huso)).replace(tzinfo=pytz.utc)
    
        paciente = []
        pacientes = Paciente.objects.all()
        for p in pacientes:
            if p.dni == dni:
                paciente.append(p)
        if not paciente:
            messages.error(request, "El DNI del paciente introducido no existe")
            return redirect("/visita/"+str(visita_id))
        

        validar_resultados = False
        resultados = Resultados.objects.filter(id_visita = visita)
        if not resultados:
            if motivo == "CONSULTA" and intervencion_nombre != "":
                resultado = Resultados(id_visita=visita)
                validar_resultados = False
            else:
                validar_resultados = True
        else:
            if motivo == "CONSULTA" and intervencion_nombre != "":
                resultado = resultados.get()
                intervencion = resultado.id_intervencion.nombre
                if intervencion == intervencion_nombre:
                    validar_resultados = True
                else:
                    validar_resultados = False
            else:
                resultado = resultados.get()
                resultado.delete()
                validar_resultados = True

        print(paciente[0])
        print(visita.id_paciente)
        print(motivo)
        print(visita.motivo)
        print(fecha)
        print(visita.fecha)
        print(paciente[0] != visita.id_paciente or motivo != visita.motivo or fecha != visita.fecha)

        if paciente[0] != visita.id_paciente or motivo != visita.motivo or fecha != visita.fecha:
            if datetime.now(pytz.timezone(huso)).replace(tzinfo=pytz.utc) >= fecha:
                visita.fecha = fecha
            else:
                messages.error(request, "La fecha no puede ser anterior al momento actual")
                return redirect("/visita/"+str(visita_id))
            visita.id_paciente = paciente[0]
            visita.motivo=motivo
            visita._history_date = datetime.now(pytz.timezone(huso)).replace(tzinfo=pytz.utc)
            visita.save()
            
        print(validar_resultados)
        if (not validar_resultados) and motivo == "CONSULTA" and intervencion_nombre != "":
            intervencion = Intervencion.objects.filter(nombre = intervencion_nombre)
            if not intervencion:
                messages.error(request, "La intervencion seleccionada no esta guardada en el sistema")
                return redirect("/visita/"+str(visita_id))
            intervencion = intervencion.get()
            resultado.id_intervencion = intervencion
            resultado.save()

        return redirect("/visita")
    else:
        context = {}
        intervenciones = Intervencion.objects.all()
        context["intervenciones"] = intervenciones
        return HttpResponse(template.render(context, request))

@login_required
def ver_visita(request, visita_id):
    template = loader.get_template("formulario_visita.html")
    visita = Visita.objects.get(id = visita_id)
    context = {}
    if visita.motivo == "CONSULTA":
        resultados = Resultados.objects.filter(id_visita = visita)
        if resultados:
            context["resultados"] = resultados.get()
        else:
            context["mostrar"] = True
    intervenciones = Intervencion.objects.all()
    context["intervenciones"] = intervenciones
    context["visita"] = visita
    return HttpResponse(template.render(context, request))


def es_auxiliar(user):
    return user.groups.filter(name='Auxiliar').exists()

def es_doctor(user):
    return user.groups.filter(name='Doctor').exists()
    
@login_required
@user_passes_test(es_auxiliar)
def update_visita_auxiliar(request, visita_id):
    visita = Visita.objects.get(id = visita_id)
    if request.method == 'POST':
        observaciones_auxiliar = request.POST.get("observaciones", "")
        if observaciones_auxiliar == visita.observaciones_auxiliar:
            return redirect("/visita")
        visita.observaciones_auxiliar = observaciones_auxiliar
        visita._history_date = datetime.now(pytz.timezone(huso)).replace(tzinfo=pytz.utc)
        visita.save()
        return redirect("/visita")
    else:
        template = loader.get_template("formulario_observaciones_visita.html")
        context = {}
        context["visita"] = visita
        context["observaciones"] = visita.observaciones_auxiliar
        context["auxiliar"] = True
        return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(es_doctor)
def update_visita_doctor(request, visita_id):
    visita = Visita.objects.get(id = visita_id)
    if request.method == 'POST':
        observaciones_doctor = request.POST.get("observaciones", "")
        if observaciones_doctor == visita.observaciones_doctor:
            return redirect("/visita")
        visita.observaciones_doctor = observaciones_doctor
        visita._history_date = datetime.now(pytz.timezone(huso)).replace(tzinfo=pytz.utc)
        visita.save()
        return redirect("/visita")
    else:
        template = loader.get_template("formulario_observaciones_visita.html")
        context = {}
        context["visita"] = visita
        context["observaciones"] = visita.observaciones_doctor
        return HttpResponse(template.render(context, request))

class FotosForm(forms.ModelForm):
    foto_antes =  forms.ImageField(required = False)
    foto_despues = forms.ImageField(required = False)
    foto_consentimiento = forms.ImageField(required = False)
    foto_etiqueta = forms.ImageField(required = False)
    class Meta:
        model = Resultados
        exclude = ['id_visita','id_intervencion','foto_antes', 'foto_despues', 'foto_consentimiento', 'foto_etiqueta']


@login_required
def update_visita_fotos(request, visita_id):
    visita = Visita.objects.get(id = visita_id)
    resultados = Resultados.objects.filter(id_visita = visita)
    if request.method == 'POST':
        form = FotosForm(request.POST, request.FILES)
        if form.is_valid():
            foto_antes = form.cleaned_data['foto_antes']
            foto_despues = form.cleaned_data['foto_despues']
            foto_consentimiento = form.cleaned_data['foto_consentimiento']
            foto_etiqueta = form.cleaned_data['foto_etiqueta']            

            if resultados:
                resultados = resultados.get()            
            else:
                messages.error(request, "No se pueden añadir fotos sin haber seleccionado una intervencion.")
                return redirect("/visita/update/fotos/"+str(visita_id))

            if foto_antes:
                if resultados.foto_antes.name != "":
                    os.remove(os.path.abspath("media/"+resultados.foto_antes.name))
                resultados.foto_antes.save(foto_antes.name, foto_antes)
            if foto_despues:
                if resultados.foto_despues.name != "":   
                    os.remove(os.path.abspath("media/"+resultados.foto_despues.name))
                resultados.foto_despues.save(foto_despues.name, foto_despues)
            if foto_consentimiento:
                if resultados.foto_consentimiento.name != "":
                    os.remove(os.path.abspath("media/"+resultados.foto_consentimiento.name))
                resultados.foto_consentimiento.save(foto_consentimiento.name, foto_consentimiento)
            if foto_etiqueta:
                if resultados.foto_etiqueta.name != "":
                    os.remove(os.path.abspath("media/"+resultados.foto_etiqueta.name))
                resultados.foto_etiqueta.save(foto_etiqueta.name, foto_etiqueta)

            resultados.save()

        return redirect("/visita/update/fotos/"+str(visita_id))
    else:
        template = loader.get_template("formulario_fotos_visita.html")
        context = {}
        context["visita"] = visita
        form = FotosForm()
        context["form"] = form
        if resultados:
            context["resultados"] = resultados.get()
        return HttpResponse(template.render(context, request))

@login_required
def ver_historia_visita(request, visita_id):
    visita = Visita.objects.filter(id = visita_id)
    if not visita:
        messages.error(request, "La visita especificada no ha sido encontrada")
        return redirect("/visita")
    else:
        visita = visita.get()
        historia = visita.historia.all()
        template = loader.get_template("lista_visita.html")
        context = {}
        context["historia"] = historia
        return HttpResponse(template.render(context, request))
    
@login_required
def verificar_dni(request):
    dni = request.GET.get("dni", "")
    pacientes = Paciente.objects.all()
    for p in pacientes:
        if p.dni == dni:
            return HttpResponse( json.dumps( {"nombre":p.nombre, "apellidos":p.apellidos}, indent=4, sort_keys=True, default=str), content_type='application/json' )
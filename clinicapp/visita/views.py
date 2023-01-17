from django.shortcuts import render, get_object_or_404, HttpResponse, HttpResponseRedirect, redirect
from django.template import Context, loader
from .models import Intervencion, Resultados, Visita
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from paciente.models import Paciente
from datetime import datetime

TIPO = ['CIRUGIA', 'PEQUEÑA CIRUGIA', 'TRAT FACIAL', 'TRAT CORPORAL']

@login_required
def main(request):
    template = loader.get_template("main_visita.html")
    context = {}
    return HttpResponse(template.render(context, request))

@login_required
def ver_intervencion(request):
    template = loader.get_template("todos_visita.html")
    intervenciones = Intervencion.objects.all()
    context = {}
    context["intervenciones"] = intervenciones
    context["tipos"] = TIPO
    return HttpResponse(template.render(context, request))

@login_required
def add_intervencion(request):
    if request.method == 'POST':
        nombre = request.POST["nombre"].upper()
        tipo = request.POST["tipo"].upper()
        if tipo in TIPO:
            intervencion = Intervencion(nombre=nombre, tipo=tipo)
            intervencion.save()
        else:
            messages.error(request, "El tipo no coincide con ninguno de los disponibles")
        return HttpResponseRedirect("/visita/intervencion")

@login_required
def borrar_intervencion(request, intervencion_id):
    intervencion =Intervencion.objects.get(id = intervencion_id)
    intervencion.delete()
    return redirect("/visita/intervencion")

@login_required
def buscar_intervencion(request):
    template = loader.get_template("todos_visita.html")
    intervenciones = Intervencion.objects.filter(nombre__icontains = request.POST.get("nombre", ""))
    context = {}
    context["intervenciones"] = intervenciones
    context["tipos"] = TIPO
    return HttpResponse(template.render(context, request))

@login_required
def buscar_visita_por_paciente_dni(request):
    if request.method == 'POST':
        template = loader.get_template("visitas.html")
        dni = request.POST.get("dni", "").upper()
        if dni == "":
            return redirect("/visita")
        else:
            paciente = Paciente.objects.filter(dni = dni)
            if not paciente:
                messages.error(request, "Paciente no encontrado")
                return redirect("/visita")
            else:
                paciente = paciente.get()
                visitas = Visita.objects.filter(id_paciente = paciente).select_related("resultados__id_intervencion").order_by('-fecha')
                context = {}
                context["visitas"] = visitas
                context["paciente"] = paciente
                return HttpResponse(template.render(context, request))

def es_auxiliar(user):
    return user.groups.filter(name='Auxiliar').exists()

def es_doctor(user):
    return user.groups.filter(name='Doctor').exists()


@login_required
def add_visita(request):
    template = loader.get_template("add_visitas.html")
    if request.method == 'POST':
        dni = request.POST["dni"].upper()

        paciente = Paciente.objects.get(dni = dni)
        if(paciente == None):
            messages.error(request, "El DNI del paciente introducido no existe")
            return HttpResponseRedirect("/visita/add")

        motivo = request.POST["motivo"].upper()
        visita = Visita()
        visita.id_paciente = paciente
        visita.motivo=motivo
        visita.fecha = datetime.now()
        visita.save()
        if motivo == "CONSULTA":
            intervencion_nombre = request.POST.get("intervencion", "").upper()
            if intervencion_nombre != "":
                intervencion = Intervencion.objects.get(nombre = intervencion_nombre)
                resultados = Resultados(id_visita = visita, id_intervencion = intervencion)
                resultados.save()
        return redirect("/visita")
    else:
        context = {}
        pacientes = Paciente.objects.all().values('dni', 'nombre', 'apellidos')
        intervenciones = Intervencion.objects.all()
        context["pacientes"] = list(pacientes)
        context["intervenciones"] = intervenciones
        return HttpResponse(template.render(context, request))
        
@login_required
def update_visita(request, visita_id):
    template = loader.get_template("add_visitas.html")
    if request.method == 'POST':
        dni = request.POST["dni"].upper()

        paciente = Paciente.objects.get(dni = dni)
        if(paciente == None):
            messages.error(request, "El DNI del paciente introducido no existe")
            return HttpResponseRedirect("/visita/add")

        motivo = request.POST["motivo"].upper()
        visita = Visita.objects.get(id = visita_id)
        visita.id_paciente = paciente
        visita.motivo=motivo
        visita.save()
        if motivo == "CONSULTA":
            intervencion_nombre = request.POST.get("intervencion", "").upper()
            if intervencion_nombre != "":
                intervencion = Intervencion.objects.get(nombre = intervencion_nombre)
                print(intervencion)

                resultados = Resultados.objects.filter(id_visita = visita)
                if not resultados:
                    resultado = Resultados(id_visita=visita, id_intervencion = intervencion)
                else:
                    resultado = resultados.get()
                    resultado.id_intervencion = intervencion
                resultado.save()
        else:
            resultados = Resultados.objects.filter(id_visita = visita)
            if resultados:
                resultado = resultados.get()
                resultado.delete()


        return redirect("/visita")
    else:
        context = {}
        pacientes = Paciente.objects.all().values('dni', 'nombre', 'apellidos')
        intervenciones = Intervencion.objects.all()
        context["pacientes"] = list(pacientes)
        context["intervenciones"] = intervenciones
        return HttpResponse(template.render(context, request))



@login_required
def ver_visita(request, visita_id):
    template = loader.get_template("add_visitas.html")
    visita = Visita.objects.get(id = visita_id)
    context = {}
    if visita.motivo == "CONSULTA":
        resultados = Resultados.objects.filter(id_visita = visita)
        if resultados:
            context["resultados"] = resultados.get()
        else:
            context["mostrar"] = True
    pacientes = Paciente.objects.all().values('dni', 'nombre', 'apellidos')
    intervenciones = Intervencion.objects.all()
    context["pacientes"] = list(pacientes)
    context["intervenciones"] = intervenciones
    context["visita"] = visita
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(es_auxiliar)
def update_visita_auxiliar(request, visita_id):
    visita = Visita.objects.get(id = visita_id)
    if request.method == 'POST':
        visita.observaciones_auxiliar = request.POST.get("observaciones", "")
        visita.save()
        return redirect("/visita")
    else:
        template = loader.get_template("observaciones_visitas.html")
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
        visita.observaciones_doctor = request.POST.get("observaciones", "")
        visita.save()
        return redirect("/visita")
    else:
        template = loader.get_template("observaciones_visitas.html")
        context = {}
        context["visita"] = visita
        context["observaciones"] = visita.observaciones_doctor
        return HttpResponse(template.render(context, request))

from django import forms
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
                resultados.foto_antes.save(foto_antes.name, foto_antes)
            if foto_despues:
                resultados.foto_despues.save(foto_despues.name, foto_despues)
            if foto_consentimiento:
                resultados.foto_consentimiento.save(foto_consentimiento.name, foto_consentimiento)
            if foto_etiqueta:
                resultados.foto_etiqueta.save(foto_etiqueta.name, foto_etiqueta)

            resultados.save()

        return redirect("/visita/update/fotos/"+str(visita_id))
    else:
        template = loader.get_template("add_fotos_visita.html")
        context = {}
        context["visita"] = visita
        form = FotosForm()
        context["form"] = form
        if resultados:
            context["resultados"] = resultados.get()
        return HttpResponse(template.render(context, request))
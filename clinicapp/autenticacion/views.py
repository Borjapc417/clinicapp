from django.shortcuts import render, get_object_or_404, HttpResponse
from django.template import Context, loader
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, logout, get_user_model
from django.contrib.auth import login as login_django
from .models import Usuario
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        dni = request.POST['dni']
        contrasenia = request.POST['contrasenia']
        
        context =  {}   

        usuario = Usuario.objects.filter(dni = dni).get()
        template = loader.get_template("login.html")

        if Usuario is None or usuario.dni != usuario.user.username:
            context["error"] = "El DNI introducido no ha sido registrado en el sistema. Por favor, reviselo o pongase en contacto con su administrador."
            return HttpResponse(template.render(context, request))
        else:
            password = usuario.user.password
            user = authenticate(username=dni, password=contrasenia)

            if contrasenia is not None and user is not None:
                login_django(request, user)
                setUserSession(user,request)
                return redirect("/paciente")
            else:
                context["error"] = "La contraseña introducida no es correcta."
                return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template("login.html")
        context = {}
        return HttpResponse(template.render(context, request))
    

def setUserSession(user,request):
     request.session['logged'] = True
     request.session['username']=user.get_username()



def es_auxiliar(user):
    return user.groups.filter(name='Auxiliar').exists()

@login_required
def logout_view(request):
    logout(request)
    return redirect("/autenticacion/login")





from django.shortcuts import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as login_django
from .models import Usuario
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        dni = request.POST['dni']
        contrasenia = request.POST['contrasenia']
        
        context =  {}   

        usuario = Usuario.objects.filter(dni = dni)
        template = loader.get_template("login.html")

        if not usuario:
            context["error"] = "El DNI introducido no ha sido registrado en el sistema. Por favor, reviselo o pongase en contacto con su administrador."
            return HttpResponse(template.render(context, request))
        else:
            usuario = usuario.get()
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


@login_required
def logout_view(request):
    logout(request)
    return redirect("/autenticacion/login")

def redireccionar(request):
    return redirect("/autenticacion/login")

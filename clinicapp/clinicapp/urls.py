"""clinicapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from autenticacion.views import redireccionar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redireccionar),
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("favicon.ico")),
    ),
    path(
        "jquery-3.6.3.min.js",
        RedirectView.as_view(url=staticfiles_storage.url("jquery-3.6.3.min.js")),
    ),
    path(
        "bootstrap.bundle.min.js",
        RedirectView.as_view(url=staticfiles_storage.url("bootstrap.bundle.min.js")),
    ),
    path(
        "bootstrap.min.css",
        RedirectView.as_view(url=staticfiles_storage.url("bootstrap.min.css")),
    ),
    path(
        "bootstrap.bundle.min.js.map",
        RedirectView.as_view(url=staticfiles_storage.url("bootstrap.bundle.min.js.map")),
    ),
    path(
        "bootstrap.min.css.map",
        RedirectView.as_view(url=staticfiles_storage.url("bootstrap.min.css.map")),
    ),
    path(
        "jquery-ui.js",
        RedirectView.as_view(url=staticfiles_storage.url("jquery-ui.js")),
    ),
    path(
        "jquery-ui.css",
        RedirectView.as_view(url=staticfiles_storage.url("jquery-ui.css")),
    ),
    path(
        "jquery-ui.structure.css",
        RedirectView.as_view(url=staticfiles_storage.url("jquery-ui.structure.css")),
    ),
]

for module in settings.MODULES:
    urlpatterns += [
        path('{}/'.format(module), include('{}.urls'.format(module)))
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

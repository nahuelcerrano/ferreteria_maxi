"""Rutas principales del proyecto.

- ``/``          Portal de preventistas (login, catálogo, carrito)  -> app Portal
- ``/abm/``      Panel de altas, bajas y modificaciones (staff)     -> app Administrador
- ``/api/``      API REST de productos                              -> app recursos_api
- ``/admin/``    Admin de Django
"""

from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Ferretería Maxi - Administración"
admin.site.site_title = "Ferretería Maxi"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("recursos_api.urls")),
    path("", include("Administrador.urls")),
    path("", include("Portal.urls")),
]

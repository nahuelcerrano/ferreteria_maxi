from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("inicio/", views.home, name="inicio"),
    path("contacto/", views.contacto, name="contacto"),
    path("about/", views.about, name="about"),
    path("lineas/", views.lineas, name="lineas"),
    path("lineas/<str:linea>/", views.seleccion, name="seleccion"),
    path("rubros/<path:rubro>/", views.gondola, name="gondola"),
    path("buscar/", views.portal_search, name="portalSearch"),
    path("servicios/", views.servicios, name="servicios"),
]

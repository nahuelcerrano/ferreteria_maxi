"""Vistas del portal para preventistas (catálogo, carrito, contacto)."""

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Min, Q
from django.http import Http404
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.views.decorators.http import require_GET

from .forms import FormularioContacto, LoginForm
from .imagenes import ruta_imagen_producto
from .models import Producto, Servicio

RESULTADOS_POR_PAGINA = 50


class LoginView(auth_views.LoginView):
    template_name = "Portal/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


@login_required
def home(request):
    return render(request, "Portal/home.html")


def about(request):
    return render(request, "Portal/about.html")


def contacto(request):
    if request.method == "POST":
        formulario = FormularioContacto(request.POST)
        if formulario.is_valid():
            # TODO: enviar la consulta por email (django.core.mail.send_mail) o guardarla.
            messages.success(request, "¡Gracias! Recibimos tu consulta y te responderemos a la brevedad.")
            return redirect("contacto")
    else:
        formulario = FormularioContacto()
    return render(request, "Portal/contacto.html", {"formulario_contacto": formulario})


@login_required
def lineas(request):
    nombres = Producto.objects.order_by("linea").values_list("linea", flat=True).distinct()
    lineas = [{"nombre": n, "imagen_url": static(ruta_imagen_producto(n))} for n in nombres]
    return render(request, "Portal/mostrarLineas.html", {"lineas": lineas})


@login_required
def seleccion(request, linea):
    """Rubros de una línea, cada uno con la imagen de alguno de sus productos."""
    filas = (
        Producto.objects.filter(linea=linea)
        .values("rubro")
        .annotate(imagen=Min("imagen", filter=~Q(imagen="")))
        .order_by("rubro")
    )
    if not filas:
        raise Http404("Línea inexistente")
    rubros = [
        {"nombre": f["rubro"], "imagen_url": static(ruta_imagen_producto(f["imagen"]))} for f in filas
    ]
    return render(request, "Portal/mostrarRubros.html", {"linea": linea, "rubros": rubros})


@login_required
def gondola(request, rubro):
    articulos = Producto.objects.filter(rubro=rubro).order_by("cod_producto")
    return render(request, "Portal/mostrarArticulos.html", {"articulos": articulos, "titulo": rubro})


@login_required
@require_GET
def portal_search(request):
    keyword = request.GET.get("keyword", "").strip()
    resultados = Producto.objects.buscar(keyword).order_by("linea", "rubro", "cod_producto")
    pagina = Paginator(resultados, RESULTADOS_POR_PAGINA).get_page(request.GET.get("page"))
    contexto = {
        "articulos": pagina,
        "page_obj": pagina,
        "keyword": keyword,
        "titulo": f"Resultados para «{keyword}»" if keyword else "Búsqueda",
    }
    return render(request, "Portal/mostrarArticulos.html", contexto)


@login_required
def servicios(request):
    servicios = Servicio.objects.select_related("linea")
    return render(request, "Portal/mostrarServicios.html", {"servicios": servicios})

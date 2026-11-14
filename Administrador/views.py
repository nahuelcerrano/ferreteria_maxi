"""Panel de altas, bajas y modificaciones (ABM). Solo accesible para usuarios staff."""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from Portal.models import Cliente, Producto, Servicio

from .forms import (
    ClienteForm,
    ProductoForm,
    SearchClienteForm,
    SearchForm,
    SearchServicioForm,
    ServicioForm,
)

RESULTADOS_POR_PAGINA = 50


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Exige un usuario autenticado con ``is_staff=True``."""

    def test_func(self):
        return self.request.user.is_staff


def staff_member_required(vista):
    """Igual que StaffRequiredMixin, pero para vistas basadas en funciones."""

    @login_required
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return vista(request, *args, **kwargs)

    return envoltura


class _ABMMixin(StaffRequiredMixin, SuccessMessageMixin):
    success_url = reverse_lazy("abm")


def _buscar(request, form_class, queryset_fn, template_form, template_resultados):
    """Búsqueda genérica por GET: muestra el formulario o, si es válido, los resultados paginados."""
    form = form_class(request.GET or None)
    if form.is_valid():
        resultados = queryset_fn(form.cleaned_data["keyword"])
        pagina = Paginator(resultados, RESULTADOS_POR_PAGINA).get_page(request.GET.get("page"))
        contexto = {"articulos": pagina, "page_obj": pagina, "keyword": form.cleaned_data["keyword"]}
        return render(request, template_resultados, contexto)
    return render(request, template_form, {"busqueda": form})


@staff_member_required
def abm(request):
    contexto = {
        "total_productos": Producto.objects.count(),
        "total_servicios": Servicio.objects.count(),
        "total_clientes": Cliente.objects.count(),
    }
    return render(request, "Administrador/abm.html", contexto)


# --- Productos ---------------------------------------------------------------


class ProductoListView(StaffRequiredMixin, ListView):
    model = Producto
    paginate_by = RESULTADOS_POR_PAGINA
    template_name = "Administrador/productoListView.html"


class ProductoCreateView(_ABMMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "Administrador/productoCreateView.html"
    success_message = "Producto creado correctamente"


class ProductoUpdateView(_ABMMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "Administrador/productoUpdateForm.html"
    success_message = "Producto editado correctamente"


class ProductoEliminarView(_ABMMixin, DeleteView):
    model = Producto
    template_name = "Administrador/productoEliminar.html"
    success_message = "Producto eliminado correctamente"


@staff_member_required
def search(request):
    return _buscar(
        request,
        SearchForm,
        lambda kw: Producto.objects.buscar(kw),
        "Administrador/productoSearch.html",
        "Administrador/ResultadosSearch.html",
    )


# --- Servicios ---------------------------------------------------------------


class ServicioCreateView(_ABMMixin, CreateView):
    model = Servicio
    form_class = ServicioForm
    template_name = "Administrador/servicioCreateView.html"
    success_message = "Servicio creado correctamente"


class ServicioUpdateView(_ABMMixin, UpdateView):
    model = Servicio
    form_class = ServicioForm
    template_name = "Administrador/servicioUpdateForm.html"
    success_message = "Servicio editado correctamente"


class ServicioEliminarView(_ABMMixin, DeleteView):
    model = Servicio
    template_name = "Administrador/servicioEliminar.html"
    success_message = "Servicio eliminado correctamente"


@staff_member_required
def servicio_search(request):
    return _buscar(
        request,
        SearchServicioForm,
        lambda kw: Servicio.objects.select_related("linea").filter(descripcion__icontains=kw),
        "Administrador/servicioSearch.html",
        "Administrador/serviciosResultadosSearch.html",
    )


# --- Clientes ----------------------------------------------------------------


class ClienteCreateView(_ABMMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "Administrador/clienteCreateView.html"
    success_message = "Cliente creado correctamente"


class ClienteUpdateView(_ABMMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "Administrador/clienteUpdateForm.html"
    success_message = "Cliente editado correctamente"


class ClienteEliminarView(_ABMMixin, DeleteView):
    model = Cliente
    template_name = "Administrador/clienteEliminar.html"
    success_message = "Cliente eliminado correctamente"


@staff_member_required
def cliente_search(request):
    return _buscar(
        request,
        SearchClienteForm,
        lambda kw: Cliente.objects.filter(
            Q(nombre__icontains=kw) | Q(apellido__icontains=kw) | Q(email__icontains=kw)
        ),
        "Administrador/clienteSearch.html",
        "Administrador/clienteResultadosSearch.html",
    )

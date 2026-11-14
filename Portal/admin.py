from django.contrib import admin

from .models import Cliente, LineaServicio, MetodoDePago, Producto, Servicio


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ["cod_producto", "descripcion", "linea", "rubro", "pcio_lista", "unidad"]
    list_filter = ["linea"]
    search_fields = ["cod_producto", "descripcion", "rubro"]
    list_per_page = 50


@admin.register(LineaServicio)
class LineaServicioAdmin(admin.ModelAdmin):
    search_fields = ["linea"]


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ["descripcion", "linea", "pcio_lista"]
    list_filter = ["linea"]
    search_fields = ["descripcion"]
    autocomplete_fields = ["linea"]


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ["apellido", "nombre", "email"]
    search_fields = ["nombre", "apellido", "email"]


@admin.register(MetodoDePago)
class MetodoDePagoAdmin(admin.ModelAdmin):
    list_display = ["tipo"]
    filter_horizontal = ["clientes"]

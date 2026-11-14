from django.db import models
from django.templatetags.static import static

from .imagenes import ruta_imagen_producto


class ProductoQuerySet(models.QuerySet):
    def buscar(self, termino):
        """Productos cuyo código, descripción, línea o rubro contengan ``termino``."""
        termino = (termino or "").strip()
        if not termino:
            return self.none()
        return self.filter(
            models.Q(cod_producto__icontains=termino)
            | models.Q(descripcion__icontains=termino)
            | models.Q(linea__icontains=termino)
            | models.Q(rubro__icontains=termino)
        )


class Producto(models.Model):
    """Artículo del catálogo mayorista.

    El catálogo se organiza en tres niveles: ``linea`` (p. ej. SANITARIOS) >
    ``rubro`` (p. ej. ABRAZADERAS) > producto. Los productos se cargan de forma
    masiva con ``python manage.py cargar_productos``.
    """

    cod_producto = models.CharField("código", max_length=20, db_index=True)
    descripcion = models.CharField("descripción", max_length=200)
    pcio_lista = models.DecimalField("precio de lista", max_digits=14, decimal_places=4)
    unidad = models.CharField("unidad", max_length=50, blank=True, default="")
    imagen = models.CharField(
        "imagen",
        max_length=50,
        blank=True,
        default="",
        help_text="Nombre del archivo en static/img, sin extensión (p. ej. 101100).",
    )
    linea = models.CharField("línea", max_length=100, db_index=True)
    rubro = models.CharField("rubro", max_length=100, db_index=True)

    objects = ProductoQuerySet.as_manager()

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"
        ordering = ["linea", "rubro", "cod_producto"]
        constraints = [
            # En el listado del proveedor hay códigos repetidos para productos
            # distintos, por eso la clave natural es código + descripción.
            models.UniqueConstraint(
                fields=["cod_producto", "descripcion"], name="producto_codigo_descripcion_unico"
            ),
        ]

    def __str__(self):
        return f"{self.cod_producto} - {self.descripcion}"

    @property
    def imagen_url(self):
        """URL de la imagen del producto, o un placeholder si no existe el archivo."""
        return static(ruta_imagen_producto(self.imagen))


class LineaServicio(models.Model):
    linea = models.CharField("línea", max_length=100, unique=True)

    class Meta:
        verbose_name = "línea de servicio"
        verbose_name_plural = "líneas de servicio"
        ordering = ["linea"]

    def __str__(self):
        return self.linea


class Servicio(models.Model):
    descripcion = models.CharField("descripción", max_length=100)
    pcio_lista = models.DecimalField("precio", max_digits=12, decimal_places=2)
    linea = models.ForeignKey(
        LineaServicio, on_delete=models.PROTECT, related_name="servicios", verbose_name="línea"
    )

    class Meta:
        verbose_name = "servicio"
        verbose_name_plural = "servicios"
        ordering = ["linea__linea", "descripcion"]

    def __str__(self):
        return f"{self.descripcion} ({self.linea})"

    @property
    def imagen_url(self):
        return static(ruta_imagen_producto(self.linea.linea))


class Cliente(models.Model):
    nombre = models.CharField("nombre", max_length=50)
    apellido = models.CharField("apellido", max_length=50)
    email = models.EmailField("email", max_length=254, unique=True)

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"


class MetodoDePago(models.Model):
    tipo = models.CharField("método de pago", max_length=50, unique=True)
    clientes = models.ManyToManyField(Cliente, related_name="metodos_de_pago", blank=True)

    class Meta:
        verbose_name = "método de pago"
        verbose_name_plural = "métodos de pago"
        ordering = ["tipo"]

    def __str__(self):
        return self.tipo

from django import forms

from Portal.models import Cliente, Producto, Servicio


class _EstiloMixin:
    """Agrega la clase ``input`` (definida en assets/css/app.css) a todos los campos."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs.setdefault("class", "input")


class ProductoForm(_EstiloMixin, forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["cod_producto", "descripcion", "linea", "rubro", "pcio_lista", "unidad", "imagen"]


class ServicioForm(_EstiloMixin, forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ["descripcion", "linea", "pcio_lista"]


class ClienteForm(_EstiloMixin, forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "apellido", "email"]


class _BusquedaForm(_EstiloMixin, forms.Form):
    keyword = forms.CharField(max_length=150)


class SearchForm(_BusquedaForm):
    keyword = forms.CharField(
        max_length=150,
        label="Palabra o código a buscar",
        widget=forms.TextInput(attrs={"placeholder": "código, descripción, línea, rubro"}),
    )


class SearchServicioForm(_BusquedaForm):
    keyword = forms.CharField(
        max_length=150, label="Palabra a buscar", widget=forms.TextInput(attrs={"placeholder": "descripción"})
    )


class SearchClienteForm(_BusquedaForm):
    keyword = forms.CharField(
        max_length=150,
        label="Nombre, apellido o email a buscar",
        widget=forms.TextInput(attrs={"placeholder": "nombre, apellido o email"}),
    )

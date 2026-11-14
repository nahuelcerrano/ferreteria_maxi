from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator

validar_nombre = RegexValidator(
    r"^[a-zA-ZÀ-ÿ\s]{4,40}$",
    "El nombre solo puede contener letras y espacios (entre 4 y 40 caracteres).",
)
validar_telefono = RegexValidator(r"^\d{10}$", "El teléfono debe contener exactamente 10 dígitos.")

_clase_campo = "form-control col-12 my-2 text-center"


class FormularioContacto(forms.Form):
    nombreContacto = forms.CharField(
        label="Nombre",
        max_length=40,
        validators=[validar_nombre],
        error_messages={"required": "Por favor completá el campo"},
        widget=forms.TextInput(attrs={"class": _clase_campo, "placeholder": "Ingrese su nombre"}),
    )
    emailContacto = forms.EmailField(
        label="Email",
        max_length=254,
        error_messages={"required": "Por favor completá el campo", "invalid": "El email ingresado es inválido."},
        widget=forms.EmailInput(attrs={"class": _clase_campo, "placeholder": "Ingrese su mail"}),
    )
    telefonoContacto = forms.CharField(
        label="Teléfono",
        max_length=10,
        validators=[validar_telefono],
        widget=forms.TextInput(
            attrs={"class": _clase_campo, "placeholder": "Ingrese su teléfono", "pattern": r"^[0-9]{10}$", "inputmode": "numeric"}
        ),
    )
    mensajeContacto = forms.CharField(
        label="Mensaje",
        max_length=1000,
        widget=forms.Textarea(attrs={"class": "form-control col-12 my-2", "placeholder": "Ingrese su mensaje acá..."}),
    )


class LoginForm(AuthenticationForm):
    """Formulario de login de Django con los estilos de Bootstrap del sitio."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuario"
        self.fields["username"].widget.attrs.update(
            {"class": "form-control my-2 text-center", "placeholder": "Ingrese su usuario"}
        )
        self.fields["password"].label = "Contraseña"
        self.fields["password"].widget.attrs.update(
            {"class": "form-control my-2 text-center", "placeholder": "Ingrese su contraseña"}
        )

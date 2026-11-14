import tempfile
from decimal import Decimal
from io import StringIO
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.test import TestCase
from django.urls import reverse

from .importacion import leer_csv, parsear_precio, reparar_precio
from .models import Producto

CSV_EJEMPLO = """cod producto|linea|rubro|descripcion|pcio_lista|unidad|imagen
101.100|SANITARIOS|ABRAZADERAS|ABRAZADERA A-6|1544.38|(C/U)|101100
101.101|SANITARIOS|ABRAZADERAS|ABRAZADERA A-7|1750|(C/U)|101100
101.102|SANITARIOS|ABRAZADERAS|ABRAZADERA A-8|1.660.166|(C/U)|
314.404|GAS|LLAVINES|LLAVIN 1/2|3019.92|(C/U)|314400
314.404|GAS|LLAVINES|LLAVIN 3/8|3405.22|(C/U)|314400
999.999|GAS|LLAVINES|PRECIO ROTO|abc|(C/U)|
"""


def crear_csv(contenido=CSV_EJEMPLO):
    archivo = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="latin-1")
    archivo.write(contenido)
    archivo.close()
    return Path(archivo.name)


class PreciosTests(TestCase):
    def test_parsea_precios_normales(self):
        self.assertEqual(parsear_precio("244.38"), Decimal("244.3800"))
        self.assertEqual(parsear_precio("0"), Decimal("0"))
        self.assertEqual(parsear_precio("12,5"), Decimal("12.5"))

    def test_repara_precio_con_separadores_de_miles(self):
        # 1.660.166 cerca de una referencia de ~1000 -> 1660.166
        self.assertEqual(reparar_precio("1.660.166", Decimal("1000")), Decimal("1660.1660"))
        # 61.830.834 cerca de una referencia de ~100 -> 61.830834 (redondeado a 4 decimales)
        self.assertEqual(reparar_precio("61.830.834", Decimal("100")), Decimal("61.8308"))


class LecturaCSVTests(TestCase):
    def test_lee_y_marca_precios_reparados(self):
        resultado = leer_csv(crear_csv())
        self.assertEqual(len(resultado.filas), 5)
        self.assertEqual(len(resultado.errores), 1)  # "abc"
        self.assertEqual(len(resultado.reparadas), 1)
        reparada = resultado.reparadas[0]
        self.assertEqual(reparada.cod_producto, "101.102")
        self.assertEqual(reparada.pcio_lista, Decimal("1660.1660"))


class CargarProductosCommandTests(TestCase):
    def test_importa_y_es_idempotente(self):
        ruta = crear_csv()
        call_command("cargar_productos", archivo=str(ruta), stdout=StringIO(), stderr=StringIO())
        self.assertEqual(Producto.objects.count(), 5)
        # Códigos repetidos con distinta descripción se guardan como productos distintos.
        self.assertEqual(Producto.objects.filter(cod_producto="314.404").count(), 2)

        Producto.objects.filter(cod_producto="101.100").update(pcio_lista=1)
        call_command("cargar_productos", archivo=str(ruta), stdout=StringIO(), stderr=StringIO())
        self.assertEqual(Producto.objects.count(), 5)
        self.assertEqual(Producto.objects.get(cod_producto="101.100").pcio_lista, Decimal("1544.38"))

    def test_simular_no_guarda(self):
        call_command("cargar_productos", archivo=str(crear_csv()), simular=True, stdout=StringIO(), stderr=StringIO())
        self.assertFalse(Producto.objects.exists())

    def test_archivo_inexistente(self):
        with self.assertRaises(CommandError):
            call_command("cargar_productos", archivo="no-existe.csv", stdout=StringIO())

    def test_csv_del_proyecto_se_puede_leer(self):
        resultado = leer_csv(Path(__file__).resolve().parent.parent / "LISTPROVconPipecorregido.csv")
        self.assertGreater(len(resultado.filas), 9000)
        self.assertEqual(resultado.errores, [])


class VistasPortalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user("preventista", password="clave-segura-123")
        Producto.objects.create(
            cod_producto="101.100", descripcion="ABRAZADERA A-6", pcio_lista=Decimal("1234.5"),
            unidad="(C/U)", imagen="101100", linea="SANITARIOS", rubro="PERILLAS COCINA / ESTUFA",
        )

    def test_catalogo_requiere_login(self):
        respuesta = self.client.get(reverse("lineas"))
        self.assertRedirects(respuesta, f"{reverse('login')}?next={reverse('lineas')}")

    def test_login_y_logout(self):
        respuesta = self.client.post(reverse("login"), {"username": "preventista", "password": "clave-segura-123"})
        self.assertRedirects(respuesta, reverse("inicio"))
        respuesta = self.client.post(reverse("logout"))
        self.assertRedirects(respuesta, reverse("login"))

    def test_login_incorrecto_muestra_error(self):
        respuesta = self.client.post(reverse("login"), {"username": "preventista", "password": "mal"})
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context["form"].errors)

    def test_navegacion_del_catalogo(self):
        self.client.force_login(self.usuario)
        self.assertContains(self.client.get(reverse("lineas")), "SANITARIOS")
        self.assertContains(self.client.get(reverse("seleccion", args=["SANITARIOS"])), "PERILLAS COCINA / ESTUFA")
        # Rubro con "/" en el nombre
        respuesta = self.client.get(reverse("gondola", args=["PERILLAS COCINA / ESTUFA"]))
        self.assertContains(respuesta, "ABRAZADERA A-6")
        # El precio se muestra con punto decimal para que el carrito (JS) pueda parsearlo
        self.assertContains(respuesta, "1234.50")
        self.assertContains(respuesta, "/static/img/101100.jpg")

    def test_linea_inexistente_da_404(self):
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(reverse("seleccion", args=["NO EXISTE"])).status_code, 404)

    def test_busqueda(self):
        self.client.force_login(self.usuario)
        self.assertContains(self.client.get(reverse("portalSearch"), {"keyword": "abrazadera"}), "101.100")
        self.assertContains(self.client.get(reverse("portalSearch"), {"keyword": "zzz"}), "No se encontraron")

    def test_imagen_inexistente_usa_placeholder(self):
        producto = Producto(imagen="no-existe")
        self.assertTrue(producto.imagen_url.endswith("img/ferreteria.png"))

    def test_contacto_valido_redirige_con_mensaje(self):
        datos = {
            "nombreContacto": "Juan Perez",
            "emailContacto": "juan@example.com",
            "telefonoContacto": "1143443600",
            "mensajeContacto": "Hola",
        }
        respuesta = self.client.post(reverse("contacto"), datos, follow=True)
        self.assertContains(respuesta, "Recibimos tu consulta")

    def test_contacto_invalido_muestra_errores(self):
        respuesta = self.client.post(reverse("contacto"), {"nombreContacto": "J"})
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context["formulario_contacto"].errors)

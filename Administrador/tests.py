from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from Portal.models import Cliente, LineaServicio, Producto, Servicio


class PanelABMTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.staff = User.objects.create_user("admin", password="x", is_staff=True)
        cls.preventista = User.objects.create_user("prev", password="x")
        cls.producto = Producto.objects.create(
            cod_producto="1", descripcion="MARTILLO", pcio_lista=Decimal("10"), linea="FERRETERIA", rubro="MARTILLOS"
        )

    def test_anonimo_es_redirigido_al_login(self):
        for nombre in ["abm", "search", "ProductoCreateView", "clienteSearch"]:
            respuesta = self.client.get(reverse(nombre))
            self.assertEqual(respuesta.status_code, 302, nombre)
            self.assertTrue(respuesta.url.startswith(reverse("login")), nombre)

    def test_usuario_no_staff_recibe_403(self):
        self.client.force_login(self.preventista)
        self.assertEqual(self.client.get(reverse("abm")).status_code, 403)
        respuesta = self.client.post(reverse("productosEliminar", args=[self.producto.pk]))
        self.assertEqual(respuesta.status_code, 403)
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())

    def test_staff_puede_hacer_abm_de_productos(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse("abm")).status_code, 200)
        self.assertContains(self.client.get(reverse("search"), {"keyword": "martillo"}), "MARTILLO")

        datos = {
            "cod_producto": "2", "descripcion": "PINZA", "linea": "FERRETERIA", "rubro": "PINZAS",
            "pcio_lista": "99.5", "unidad": "(C/U)", "imagen": "",
        }
        self.assertRedirects(self.client.post(reverse("ProductoCreateView"), datos), reverse("abm"))
        pinza = Producto.objects.get(descripcion="PINZA")

        datos["pcio_lista"] = "120"
        self.client.post(reverse("productosEditar", args=[pinza.pk]), datos)
        pinza.refresh_from_db()
        self.assertEqual(pinza.pcio_lista, Decimal("120"))

        self.client.post(reverse("productosEliminar", args=[pinza.pk]))
        self.assertFalse(Producto.objects.filter(pk=pinza.pk).exists())

    def test_staff_puede_hacer_abm_de_clientes_y_servicios(self):
        self.client.force_login(self.staff)
        datos = {"nombre": "Ana", "apellido": "Gómez", "email": "ana@example.com"}
        self.assertRedirects(self.client.post(reverse("clienteCreateView"), datos), reverse("abm"))
        cliente = Cliente.objects.get()
        datos["nombre"] = "Ana María"
        self.assertRedirects(self.client.post(reverse("clienteEditar", args=[cliente.pk]), datos), reverse("abm"))
        self.assertContains(self.client.get(reverse("clienteSearch"), {"keyword": "gómez"}), "Ana María")

        linea = LineaServicio.objects.create(linea="FERRETERIA")
        datos = {"descripcion": "Corte de caños", "linea": linea.pk, "pcio_lista": "500"}
        self.assertRedirects(self.client.post(reverse("ServicioCreateView"), datos), reverse("abm"))
        self.assertEqual(Servicio.objects.count(), 1)

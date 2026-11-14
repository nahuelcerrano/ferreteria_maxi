from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from Portal.models import Producto


class ProductoAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.staff = User.objects.create_user("admin", password="x", is_staff=True)
        cls.preventista = User.objects.create_user("prev", password="x")
        Producto.objects.create(
            cod_producto="1", descripcion="MARTILLO", pcio_lista=Decimal("10"), linea="FERRETERIA", rubro="MARTILLOS"
        )
        Producto.objects.create(
            cod_producto="2", descripcion="CANILLA", pcio_lista=Decimal("20"), linea="SANITARIOS", rubro="CANILLAS"
        )

    def test_requiere_autenticacion(self):
        self.assertEqual(self.client.get("/api/productos/").status_code, 403)

    def test_listado_paginado_y_filtros(self):
        self.client.force_authenticate(self.preventista)
        datos = self.client.get("/api/productos/").json()
        self.assertEqual(datos["count"], 2)
        self.assertIn("imagen_url", datos["results"][0])
        self.assertEqual(self.client.get("/api/productos/", {"q": "martillo"}).json()["count"], 1)
        self.assertEqual(self.client.get("/api/productos/", {"linea": "SANITARIOS"}).json()["count"], 1)

    def test_solo_staff_puede_escribir(self):
        nuevo = {"cod_producto": "3", "descripcion": "PINZA", "linea": "FERRETERIA", "rubro": "PINZAS", "pcio_lista": "5"}
        self.client.force_authenticate(self.preventista)
        self.assertEqual(self.client.post("/api/productos/", nuevo).status_code, 403)
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.post("/api/productos/", nuevo).status_code, 201)

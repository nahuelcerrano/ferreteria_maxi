from rest_framework import viewsets

from Portal.models import Producto

from .permissions import EsStaffOSoloLectura
from .serializers import ProductoSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    """CRUD de productos.

    - ``GET /api/productos/``                 listado paginado (``?page=N``)
    - ``GET /api/productos/?q=texto``         búsqueda por código, descripción, línea o rubro
    - ``GET /api/productos/?linea=X&rubro=Y`` filtros exactos
    - ``POST/PUT/PATCH/DELETE``               solo usuarios staff
    """

    serializer_class = ProductoSerializer
    permission_classes = [EsStaffOSoloLectura]

    def get_queryset(self):
        queryset = Producto.objects.all()
        params = self.request.query_params
        if q := params.get("q"):
            queryset = queryset.buscar(q)
        if linea := params.get("linea"):
            queryset = queryset.filter(linea=linea)
        if rubro := params.get("rubro"):
            queryset = queryset.filter(rubro=rubro)
        return queryset

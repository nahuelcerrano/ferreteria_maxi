from django.urls import path

from . import views

urlpatterns = [
    path("abm/", views.abm, name="abm"),
    # Productos
    path("abm/productos/", views.ProductoListView.as_view(), name="ProductosView"),
    path("abm/productos/nuevo/", views.ProductoCreateView.as_view(), name="ProductoCreateView"),
    path("abm/productos/buscar/", views.search, name="search"),
    path("abm/productos/<int:pk>/editar/", views.ProductoUpdateView.as_view(), name="productosEditar"),
    path("abm/productos/<int:pk>/eliminar/", views.ProductoEliminarView.as_view(), name="productosEliminar"),
    # Servicios
    path("abm/servicios/nuevo/", views.ServicioCreateView.as_view(), name="ServicioCreateView"),
    path("abm/servicios/buscar/", views.servicio_search, name="servicioSearch"),
    path("abm/servicios/<int:pk>/editar/", views.ServicioUpdateView.as_view(), name="servicioEditar"),
    path("abm/servicios/<int:pk>/eliminar/", views.ServicioEliminarView.as_view(), name="servicioEliminar"),
    # Clientes
    path("abm/clientes/nuevo/", views.ClienteCreateView.as_view(), name="clienteCreateView"),
    path("abm/clientes/buscar/", views.cliente_search, name="clienteSearch"),
    path("abm/clientes/<int:pk>/editar/", views.ClienteUpdateView.as_view(), name="clienteEditar"),
    path("abm/clientes/<int:pk>/eliminar/", views.ClienteEliminarView.as_view(), name="clienteEliminar"),
]

from rest_framework import serializers

from Portal.models import Producto


class ProductoSerializer(serializers.ModelSerializer):
    imagen_url = serializers.CharField(read_only=True)

    class Meta:
        model = Producto
        fields = ["id", "cod_producto", "descripcion", "linea", "rubro", "pcio_lista", "unidad", "imagen", "imagen_url"]

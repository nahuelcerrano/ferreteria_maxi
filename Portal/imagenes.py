"""Resolución de imágenes de productos dentro de ``static/img``.

Los nombres de imagen del CSV no traen extensión y en el disco hay archivos
``.jpg`` y ``.JPG``. Como Linux distingue mayúsculas, se arma un índice
insensible a mayúsculas una sola vez y se resuelve el nombre real del archivo.
"""

from functools import lru_cache

from django.contrib.staticfiles import finders

CARPETA = "img"
PLACEHOLDER = "img/ferreteria.png"
EXTENSIONES = (".jpg", ".jpeg", ".png", ".webp")


@lru_cache(maxsize=1)
def _indice_imagenes():
    """Devuelve {nombre_sin_extension_en_minusculas: ruta_relativa_static}."""
    indice = {}
    for finder in finders.get_finders():
        for ruta, _storage in finder.list(ignore_patterns=[]):
            ruta = ruta.replace("\\", "/")
            carpeta, _, archivo = ruta.rpartition("/")
            if carpeta != CARPETA:
                continue
            nombre, punto, extension = archivo.rpartition(".")
            if punto and f".{extension.lower()}" in EXTENSIONES:
                indice.setdefault(nombre.lower(), ruta)
    return indice


def ruta_imagen_producto(nombre):
    """Ruta relativa a ``static/`` para ``nombre``, o el placeholder si no existe."""
    if not nombre:
        return PLACEHOLDER
    nombre = str(nombre).strip().lower()
    indice = _indice_imagenes()
    return indice.get(nombre) or indice.get(nombre.replace(".", "")) or PLACEHOLDER

"""Lectura y limpieza del listado de productos del proveedor (CSV separado por ``|``).

Formato esperado (primera fila = encabezados)::

    cod producto|linea|rubro|descripcion|pcio_lista|unidad|imagen
    101.100|SANITARIOS|ABRAZADERAS|ABRAZADERA ALAMBRE A-6 (10 X 13 mm.)|244.38|(C/U)|101100

Problema conocido del archivo original: unos 450 precios fueron exportados
desde una planilla con separadores de miles y perdieron el punto decimal
(p. ej. ``1.660.166`` en lugar de ``1660.166``). Para esos casos el valor
no se puede recuperar con certeza, así que se elige la posición decimal que
deja el precio más cerca de la mediana de su rubro y la fila se marca como
``precio_reparado`` para que pueda revisarse a mano.
"""

import csv
import math
import statistics
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path

DECIMALES = 4
_CUANTO = Decimal(1).scaleb(-DECIMALES)

# Encabezado del CSV -> campo del modelo Producto
COLUMNAS = {
    "cod producto": "cod_producto",
    "cod_producto": "cod_producto",
    "linea": "linea",
    "rubro": "rubro",
    "descripcion": "descripcion",
    "pcio_lista": "pcio_lista",
    "unidad": "unidad",
    "imagen": "imagen",
}
OBLIGATORIAS = {"cod_producto", "linea", "rubro", "descripcion", "pcio_lista"}


class ErrorDeFormato(ValueError):
    """El archivo no tiene el formato esperado."""


@dataclass
class FilaProducto:
    numero_linea: int
    cod_producto: str
    linea: str
    rubro: str
    descripcion: str
    unidad: str
    imagen: str
    precio_original: str
    pcio_lista: Decimal | None = None
    precio_reparado: bool = False

    def como_kwargs(self):
        return {
            "cod_producto": self.cod_producto,
            "linea": self.linea,
            "rubro": self.rubro,
            "descripcion": self.descripcion,
            "unidad": self.unidad,
            "imagen": self.imagen,
            "pcio_lista": self.pcio_lista,
        }


@dataclass
class ResultadoLectura:
    filas: list[FilaProducto] = field(default_factory=list)
    errores: list[str] = field(default_factory=list)
    duplicadas: int = 0

    @property
    def reparadas(self):
        return [f for f in self.filas if f.precio_reparado]


def es_precio_ambiguo(texto):
    """Un precio con más de un punto perdió su separador decimal."""
    return texto.count(".") > 1


def parsear_precio(texto):
    """Convierte un precio "bien formado" a Decimal. Lanza InvalidOperation si no se puede."""
    texto = texto.strip().replace("$", "").replace(" ", "")
    if not texto:
        return Decimal(0)
    if "," in texto and "." not in texto:
        texto = texto.replace(",", ".")
    valor = Decimal(texto)
    if not valor.is_finite() or valor < 0:
        raise InvalidOperation(texto)
    return valor.quantize(_CUANTO)


def reparar_precio(texto, referencia):
    """Elige la posición del punto decimal que deja el valor más cerca de ``referencia``.

    La cercanía se mide en escala logarítmica, que es lo adecuado para
    comparar órdenes de magnitud de precios.
    """
    digitos = texto.replace(".", "").strip()
    if not digitos.isdigit():
        raise InvalidOperation(texto)
    entero = Decimal(digitos)
    if entero == 0 or not referencia or referencia <= 0:
        return entero.quantize(_CUANTO)
    candidatos = [entero.scaleb(-k) for k in range(len(digitos))]
    objetivo = math.log(float(referencia))
    mejor = min(candidatos, key=lambda c: abs(math.log(float(c)) - objetivo))
    return mejor.quantize(_CUANTO)


def _normalizar_encabezados(encabezados):
    mapeo = {}
    for indice, nombre in enumerate(encabezados):
        clave = COLUMNAS.get(nombre.strip().lower())
        if clave:
            mapeo[clave] = indice
    faltantes = OBLIGATORIAS - mapeo.keys()
    if faltantes:
        raise ErrorDeFormato(
            f"Faltan columnas obligatorias: {', '.join(sorted(faltantes))}. "
            f"Encabezados encontrados: {encabezados}"
        )
    return mapeo


def leer_csv(ruta, encoding="latin-1", delimitador="|"):
    """Lee el CSV y devuelve un :class:`ResultadoLectura` con precios ya resueltos."""
    ruta = Path(ruta)
    resultado = ResultadoLectura()
    vistos = set()

    with ruta.open(encoding=encoding, newline="") as archivo:
        lector = csv.reader(archivo, delimiter=delimitador)
        try:
            encabezados = next(lector)
        except StopIteration:
            raise ErrorDeFormato("El archivo está vacío.") from None
        columnas = _normalizar_encabezados(encabezados)

        def celda(fila, nombre):
            indice = columnas.get(nombre)
            return fila[indice].strip() if indice is not None and indice < len(fila) else ""

        for numero, fila in enumerate(lector, start=2):
            if not any(c.strip() for c in fila):
                continue
            if len(fila) < len(encabezados):
                resultado.errores.append(f"Línea {numero}: tiene {len(fila)} columnas, se esperaban {len(encabezados)}.")
                continue
            item = FilaProducto(
                numero_linea=numero,
                cod_producto=celda(fila, "cod_producto"),
                linea=celda(fila, "linea"),
                rubro=celda(fila, "rubro"),
                descripcion=celda(fila, "descripcion"),
                unidad=celda(fila, "unidad"),
                imagen=celda(fila, "imagen"),
                precio_original=celda(fila, "pcio_lista"),
            )
            if not (item.cod_producto and item.descripcion and item.linea and item.rubro):
                resultado.errores.append(f"Línea {numero}: faltan código, descripción, línea o rubro.")
                continue
            clave = (item.cod_producto, item.descripcion)
            if clave in vistos:
                resultado.duplicadas += 1
                continue
            vistos.add(clave)
            if not es_precio_ambiguo(item.precio_original):
                try:
                    item.pcio_lista = parsear_precio(item.precio_original)
                except InvalidOperation:
                    resultado.errores.append(f"Línea {numero}: precio inválido '{item.precio_original}'.")
                    continue
            resultado.filas.append(item)

    _resolver_precios_ambiguos(resultado)
    return resultado


def _mediana(valores):
    valores = [v for v in valores if v > 0]
    return statistics.median(valores) if valores else None


def _resolver_precios_ambiguos(resultado):
    por_rubro, por_linea, todos = {}, {}, []
    for f in resultado.filas:
        if f.pcio_lista is not None:
            por_rubro.setdefault((f.linea, f.rubro), []).append(f.pcio_lista)
            por_linea.setdefault(f.linea, []).append(f.pcio_lista)
            todos.append(f.pcio_lista)
    mediana_global = _mediana(todos)

    pendientes = []
    for f in resultado.filas:
        if f.pcio_lista is not None:
            continue
        referencia = (
            _mediana(por_rubro.get((f.linea, f.rubro), []))
            or _mediana(por_linea.get(f.linea, []))
            or mediana_global
        )
        try:
            f.pcio_lista = reparar_precio(f.precio_original, referencia)
            f.precio_reparado = True
        except InvalidOperation:
            resultado.errores.append(f"Línea {f.numero_linea}: precio inválido '{f.precio_original}'.")
            pendientes.append(f)
    for f in pendientes:
        resultado.filas.remove(f)

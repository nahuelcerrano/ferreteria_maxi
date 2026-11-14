"""Carga (o actualiza) el catálogo de productos desde el CSV del proveedor.

Uso::

    python manage.py cargar_productos                       # usa LISTPROVconPipecorregido.csv
    python manage.py cargar_productos --archivo otro.csv
    python manage.py cargar_productos --vaciar              # borra todo y vuelve a cargar
    python manage.py cargar_productos --simular            # valida sin escribir en la BD
    python manage.py cargar_productos --reporte revisar.csv # exporta precios reparados

Es idempotente: si se ejecuta dos veces, los productos existentes (mismo código
y descripción) se actualizan en lugar de duplicarse.
"""

import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from Portal.importacion import ErrorDeFormato, leer_csv
from Portal.models import Producto

ARCHIVO_POR_DEFECTO = "LISTPROVconPipecorregido.csv"
CAMPOS_ACTUALIZABLES = ["linea", "rubro", "unidad", "imagen", "pcio_lista"]


class Command(BaseCommand):
    help = "Importa los productos desde el CSV del proveedor (separado por '|')."

    def add_arguments(self, parser):
        parser.add_argument(
            "--archivo",
            default=str(Path(settings.BASE_DIR) / ARCHIVO_POR_DEFECTO),
            help=f"Ruta del CSV (por defecto: {ARCHIVO_POR_DEFECTO} en la raíz del proyecto).",
        )
        parser.add_argument("--encoding", default="latin-1", help="Codificación del archivo (por defecto: latin-1).")
        parser.add_argument("--delimitador", default="|", help="Separador de columnas (por defecto: '|').")
        parser.add_argument("--vaciar", action="store_true", help="Elimina todos los productos antes de importar.")
        parser.add_argument("--simular", action="store_true", help="Lee y valida el archivo sin guardar nada.")
        parser.add_argument(
            "--reporte",
            metavar="ARCHIVO",
            help="Guarda en un CSV las filas cuyo precio tuvo que repararse, para revisarlas a mano.",
        )
        parser.add_argument("--lote", type=int, default=1000, help="Tamaño de lote para inserciones (por defecto: 1000).")

    def handle(self, *args, **opciones):
        ruta = Path(opciones["archivo"])
        if not ruta.is_file():
            raise CommandError(f"No se encontró el archivo: {ruta}")

        self.stdout.write(f"Leyendo {ruta} ...")
        try:
            resultado = leer_csv(ruta, encoding=opciones["encoding"], delimitador=opciones["delimitador"])
        except (ErrorDeFormato, UnicodeDecodeError) as exc:
            raise CommandError(f"No se pudo leer el archivo: {exc}") from exc

        for error in resultado.errores:
            self.stderr.write(self.style.WARNING(f"  Omitida -> {error}"))

        filas = resultado.filas
        reparadas = resultado.reparadas
        self.stdout.write(f"  Filas válidas: {len(filas)}")
        if resultado.duplicadas:
            self.stdout.write(f"  Filas repetidas ignoradas: {resultado.duplicadas}")
        if reparadas:
            self.stdout.write(
                self.style.WARNING(
                    f"  Precios mal formateados reparados automáticamente: {len(reparadas)} "
                    "(conviene revisarlos; usá --reporte para exportarlos)."
                )
            )

        if opciones["reporte"]:
            self._escribir_reporte(Path(opciones["reporte"]), reparadas)

        if opciones["simular"]:
            self.stdout.write(self.style.SUCCESS("Simulación terminada: no se guardó nada."))
            return

        with transaction.atomic():
            if opciones["vaciar"]:
                borrados, _ = Producto.objects.all().delete()
                self.stdout.write(f"  Productos eliminados: {borrados}")
            antes = Producto.objects.count()
            Producto.objects.bulk_create(
                [Producto(**f.como_kwargs()) for f in filas],
                batch_size=opciones["lote"],
                update_conflicts=True,
                unique_fields=["cod_producto", "descripcion"],
                update_fields=CAMPOS_ACTUALIZABLES,
            )
            despues = Producto.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Importación completa: {despues - antes} productos nuevos, "
                f"{len(filas) - (despues - antes)} actualizados. Total en la base: {despues}."
            )
        )

    def _escribir_reporte(self, ruta, reparadas):
        with ruta.open("w", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["linea_csv", "cod_producto", "rubro", "descripcion", "precio_original", "precio_cargado"])
            for f in reparadas:
                escritor.writerow(
                    [f.numero_linea, f.cod_producto, f.rubro, f.descripcion, f.precio_original, f.pcio_lista]
                )
        self.stdout.write(f"  Reporte de precios reparados guardado en {ruta}")

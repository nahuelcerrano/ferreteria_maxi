# Ferretería Maxi

Sitio web mayorista de ferretería donde los **preventistas** consultan el catálogo
(~9.400 artículos), arman pedidos en un carrito y el personal **administrador**
gestiona productos, servicios y clientes.

Comisión 23320 · Grupo 2 — [Juan Alberto Mazzocchi](https://github.com/JuanMazzocchi),
[Nahuel Cerrano](https://github.com/nahuelcerrano),
[Sofia Irene Radulovich](https://github.com/sofiaradulovich)

---

## Índice

1. [Tecnologías](#tecnologías)
2. [Inicio rápido](#inicio-rápido)
3. [Cargar los productos desde el CSV](#cargar-los-productos-desde-el-csv)
4. [Configuración (.env)](#configuración-env)
5. [Usar MySQL en lugar de SQLite](#usar-mysql-en-lugar-de-sqlite)
6. [Estructura del proyecto](#estructura-del-proyecto)
7. [Modelo de datos](#modelo-de-datos)
8. [Rutas del sitio](#rutas-del-sitio)
9. [API REST](#api-rest)
10. [Usuarios y permisos](#usuarios-y-permisos)
11. [Tests](#tests)
12. [Puesta en producción](#puesta-en-producción)
13. [Problemas frecuentes](#problemas-frecuentes)

---

## Tecnologías

| Componente | Versión |
|---|---|
| Python | 3.10 o superior |
| [Django](https://docs.djangoproject.com/en/5.2/) | 5.2 LTS (soporte hasta abril 2028) |
| [Django REST Framework](https://www.django-rest-framework.org/) | 3.16+ |
| [django-environ](https://django-environ.readthedocs.io/) | configuración por variables de entorno |
| [WhiteNoise](https://whitenoise.readthedocs.io/) | archivos estáticos en producción |
| Base de datos | SQLite (por defecto) o MySQL / PostgreSQL |
| Front-end | Bootstrap 5, SweetAlert2, JavaScript (carrito en `localStorage`) |

## Inicio rápido

```bash
# 1. Clonar y entrar al proyecto
git clone https://github.com/nahuelcerrano/grupo2-django.git
cd grupo2-django

# 2. Crear y activar el entorno virtual
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear el archivo de configuración
cp .env.example .env               # Windows: copy .env.example .env
#    y editar SECRET_KEY (ver sección "Configuración")

# 5. Crear las tablas
python manage.py migrate

# 6. Cargar el catálogo de productos desde el CSV
python manage.py cargar_productos

# 7. Crear un usuario administrador
python manage.py createsuperuser

# 8. Levantar el servidor
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/> e ingresar con el usuario creado en el paso 7.

> Sin configurar nada más, el proyecto usa **SQLite** (archivo `db.sqlite3`),
> así que no hace falta instalar MySQL para trabajar.

## Cargar los productos desde el CSV

El catálogo viene del listado del proveedor, `LISTPROVconPipecorregido.csv`
(raíz del proyecto). Se importa con un comando de Django:

```bash
python manage.py cargar_productos
```

Salida esperada:

```
Leyendo .../LISTPROVconPipecorregido.csv ...
  Filas válidas: 9417
  Precios mal formateados reparados automáticamente: 450 (conviene revisarlos; usá --reporte para exportarlos).
Importación completa: 9417 productos nuevos, 0 actualizados. Total en la base: 9417.
```

### Opciones

| Opción | Descripción |
|---|---|
| `--archivo RUTA` | Usar otro CSV (por defecto `LISTPROVconPipecorregido.csv`). |
| `--encoding ENC` | Codificación del archivo (por defecto `latin-1`, que es la del CSV original). |
| `--delimitador C` | Separador de columnas (por defecto `\|`). |
| `--vaciar` | Borra **todos** los productos antes de importar. |
| `--simular` | Lee y valida el archivo sin guardar nada. |
| `--reporte ARCHIVO.csv` | Exporta las filas cuyo precio se reparó, para revisarlas. |

El comando es **idempotente**: si se corre de nuevo (por ejemplo, con una lista
de precios actualizada) actualiza los productos existentes en vez de duplicarlos.
Un producto se identifica por **código + descripción**, porque en el listado hay
códigos repetidos para artículos distintos (p. ej. `314.404`).

### Formato del CSV

```
cod producto|linea|rubro|descripcion|pcio_lista|unidad|imagen
101.100|SANITARIOS|ABRAZADERAS|ABRAZADERA ALAMBRE A-6 (10 X 13 mm.)|244.38|(C/U)|101100
```

- Separador `|`, primera fila con encabezados, codificación Latin-1.
- `imagen` es el nombre del archivo en `static/img/` **sin extensión**. Si no
  existe, se muestra el logo de la ferretería como imagen por defecto.

### Precios con formato roto (importante)

Unos **450 precios** del CSV original vienen con separadores de miles en vez de
punto decimal (ej.: `1.660.166`, `88.696.231`). Con esos datos es imposible
saber con certeza dónde iba la coma, así que el importador elige la posición
decimal que deja el precio más cerca de la mediana de su rubro y lo informa.
**Esos precios son una estimación**: generá el reporte, revisalo y corregí
los valores a mano en el CSV o desde el panel.

```bash
python manage.py cargar_productos --simular --reporte precios_a_revisar.csv
```

## Configuración (.env)

Toda la configuración sensible se lee del archivo `.env` (no se sube a git).
Plantilla: [`.env.example`](.env.example).

| Variable | Por defecto | Descripción |
|---|---|---|
| `DEBUG` | `False` | Modo depuración. `True` solo en desarrollo. |
| `SECRET_KEY` | — | Obligatoria con `DEBUG=False`. |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Dominios permitidos, separados por coma. |
| `CSRF_TRUSTED_ORIGINS` | vacío | Orígenes https de confianza (producción). |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | Conexión a la base de datos. |
| `LOG_LEVEL` | `INFO` | Nivel de log. |

Generar una `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

## Usar MySQL en lugar de SQLite

1. Instalar las librerías de cliente de MySQL del sistema
   (Debian/Ubuntu: `sudo apt install default-libmysqlclient-dev build-essential pkg-config`;
   Windows: `pip` descarga una versión precompilada).
2. Instalar el conector: `pip install -r requirements-mysql.txt`
3. Crear la base:
   ```sql
   CREATE DATABASE ferreteria CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
4. En `.env`:
   ```
   DATABASE_URL=mysql://usuario:clave@localhost:3306/ferreteria
   ```
5. `python manage.py migrate` y `python manage.py cargar_productos`.

## Estructura del proyecto

```
.
├── Ferreteria/                 # Configuración del proyecto Django
│   ├── settings.py             #   settings leídos desde .env
│   └── urls.py                 #   rutas principales
├── Portal/                     # App de preventistas: catálogo, carrito, contacto, login
│   ├── models.py               #   Producto, Servicio, LineaServicio, Cliente, MetodoDePago
│   ├── importacion.py          #   lectura y limpieza del CSV del proveedor
│   ├── imagenes.py             #   resuelve la imagen de cada producto en static/img
│   ├── management/commands/
│   │   └── cargar_productos.py #   comando de importación
│   ├── views.py / urls.py / forms.py / admin.py / tests.py
├── Administrador/              # Panel ABM (altas, bajas, modificaciones) solo para staff
├── recursos_api/               # API REST de productos (Django REST Framework)
├── templates/                  # Plantillas HTML
│   ├── Portal/                 #   sitio público y catálogo
│   ├── Administrador/          #   panel ABM
│   └── includes/               #   mensajes y paginación reutilizables
├── static/
│   ├── img/                    #   imágenes de productos (nombre = columna "imagen" del CSV)
│   ├── js/script.js            #   carrito de pedidos (localStorage)
│   └── js/scriptForm.js        #   validación del formulario de contacto
├── LISTPROVconPipecorregido.csv  # listado de productos del proveedor
├── requirements.txt            # dependencias
├── requirements-mysql.txt      # dependencias extra para MySQL
└── .env.example                # plantilla de configuración
```

## Modelo de datos

```
Producto                         LineaServicio 1 ──< Servicio
  cod_producto  (indexado)
  descripcion                    Cliente >──< MetodoDePago
  linea         (indexado)
  rubro         (indexado)
  pcio_lista    Decimal(14,4)
  unidad
  imagen
  único: (cod_producto, descripcion)
```

El catálogo se navega en tres niveles: **línea** (SANITARIOS, GAS, FERRETERIA…)
→ **rubro** (ABRAZADERAS, CANILLAS…) → **productos**.

## Rutas del sitio

| URL | Nombre | Acceso | Descripción |
|---|---|---|---|
| `/` | `login` | público | Inicio de sesión |
| `/logout/` | `logout` | logueado (POST) | Cerrar sesión |
| `/inicio/` | `inicio` | logueado | Home |
| `/lineas/` | `lineas` | logueado | Líneas de productos |
| `/lineas/<linea>/` | `seleccion` | logueado | Rubros de una línea |
| `/rubros/<rubro>/` | `gondola` | logueado | Productos de un rubro |
| `/buscar/?keyword=` | `portalSearch` | logueado | Búsqueda (paginada) |
| `/servicios/` | `servicios` | logueado | Servicios |
| `/about/`, `/contacto/` | `about`, `contacto` | público | Institucional / contacto |
| `/abm/…` | `abm`, `search`, … | staff | Panel de administración propio |
| `/admin/` | — | staff | Admin de Django |
| `/api/…` | — | ver abajo | API REST |

## API REST

Base: `/api/`. Requiere estar autenticado (sesión o login en `/api/auth/login/`).

| Método | URL | Permiso | Descripción |
|---|---|---|---|
| GET | `/api/productos/` | logueado | Listado paginado (50 por página, `?page=N`) |
| GET | `/api/productos/?q=llave` | logueado | Búsqueda por código, descripción, línea o rubro |
| GET | `/api/productos/?linea=GAS&rubro=LLAVINES` | logueado | Filtros exactos |
| GET | `/api/productos/<id>/` | logueado | Detalle |
| POST/PUT/PATCH/DELETE | `/api/productos/…` | staff | Alta, edición y baja |

## Usuarios y permisos

- **Preventista**: usuario común (creado desde `/admin/`). Ve el catálogo y usa el carrito.
- **Administrador**: usuario con `is_staff=True`. Además accede al panel `/abm/`
  y puede escribir en la API. Con `createsuperuser` se crea uno con todos los permisos.

## Tests

```bash
python manage.py test
```

Cubren la importación del CSV (incluida la reparación de precios y la
idempotencia), el login/logout, la navegación del catálogo, la búsqueda,
el control de acceso del panel ABM y los permisos de la API.

## Puesta en producción

1. En `.env`: `DEBUG=False`, una `SECRET_KEY` nueva, `ALLOWED_HOSTS` y
   `CSRF_TRUSTED_ORIGINS` con el dominio real, y `DATABASE_URL`.
2. `python manage.py collectstatic` (WhiteNoise sirve los estáticos comprimidos).
3. `python manage.py migrate`
4. `python manage.py check --deploy`
5. Servir con un servidor WSGI, por ejemplo `gunicorn Ferreteria.wsgi`.

## Problemas frecuentes

| Problema | Solución |
|---|---|
| `Set the SECRET_KEY environment variable` | Falta el `.env` o `DEBUG=False` sin `SECRET_KEY`. Copiar `.env.example` a `.env`. |
| Las líneas aparecen vacías | No se cargaron los productos: `python manage.py cargar_productos`. |
| `UnicodeDecodeError` al importar | El CSV tiene otra codificación: `--encoding utf-8`. |
| `mysqlclient` no instala | Faltan las librerías de desarrollo de MySQL (ver "Usar MySQL") o usar SQLite. |
| El panel ABM da 403 | El usuario no es staff: marcar "Es staff" desde `/admin/`. |

## Historial de cambios importantes

Ver [CHANGELOG.md](CHANGELOG.md).

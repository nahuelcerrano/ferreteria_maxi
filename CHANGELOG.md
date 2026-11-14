# Changelog

## [2.0.0] — 2026-11-14 · Refactor y puesta en marcha

### Corregido (la página no funcionaba)
- **No había forma de cargar los productos**: nuevo comando `python manage.py cargar_productos`
  que importa `LISTPROVconPipecorregido.csv` (Latin-1, separado por `|`), es idempotente
  y repara/informa ~450 precios exportados con separadores de miles (`1.660.166`).
- La base de datos estaba fija a un MySQL local (`gustavo` / `root`). Ahora se configura con
  `DATABASE_URL` y por defecto usa SQLite, sin instalar nada.
- `requirements.txt` estaba en UTF-16 y `pip` no lo podía leer bien; además pedía `mysqlclient`
  obligatorio. Ahora es UTF-8 y MySQL es opcional (`requirements-mysql.txt`).
- Imágenes de productos con extensión `.JPG` no cargaban en Linux; rutas `/static/...` escritas
  a mano; búsqueda con ruta de plantilla de Windows (`'Portal\mostrarArticulos.html'`).
- `ClienteUpdateView` redirigía a una URL relativa inválida; la búsqueda de clientes usaba el
  formulario de servicios; el borrado de productos no mostraba mensaje.
- El carrito fallaba con precios localizados; ahora el precio se muestra siempre con punto decimal.

### Seguridad
- El panel ABM (`/abm/`) era accesible **sin iniciar sesión**: cualquiera podía crear o borrar
  productos. Ahora exige usuario staff (403 para usuarios comunes).
- La API permitía escribir a cualquier usuario logueado; ahora solo staff, y lectura solo autenticados.
- `DEBUG`, `SECRET_KEY` y `ALLOWED_HOSTS` se leen del entorno; ajustes de seguridad para producción.
- Logout por POST (requisito de Django 5) y login con el `AuthenticationForm` de Django.

### Cambiado
- Django 3.2 (sin soporte desde 2024) → **Django 5.2 LTS**.
- Modelos: precio `DecimalField` (antes `FloatField`), índices en línea/rubro/código, restricción
  única código+descripción, `EmailField` único en clientes, nombres de clase PEP 8
  (`LineaServicio`, `MetodoDePago`) con migraciones que conservan los datos.
- Vistas: búsquedas por GET con paginación, consultas con `Q` en vez de `union`, la vista de rubros
  hace una sola consulta (antes N+1), 404 para líneas inexistentes.
- URLs con nombre y `{% url %}` en todas las plantillas; rutas más claras (`/lineas/`, `/rubros/`, `/abm/productos/...`).
- Admin de Django con búsqueda, filtros y columnas.
- Idioma `es-ar` y zona horaria de Buenos Aires.
- Archivos estáticos con WhiteNoise.

### Agregado
- Tests automatizados (`python manage.py test`).
- `README.md` completo, `.env.example` y este changelog.

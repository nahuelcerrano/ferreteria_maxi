/*
 * Carrito de pedidos de Ferretería Maxi.
 *
 * El carrito vive en el navegador (localStorage, clave "productos") como una
 * lista de objetos: {id, imagen, descripcion, precio, unidad, cantidad}.
 *
 * Marcado que espera en las plantillas:
 *  - Cada artículo: un elemento con [data-producto] y los atributos
 *    data-codigo, data-descripcion, data-precio, data-unidad, data-imagen.
 *    Adentro: un <input data-cantidad> y un <button data-agregar>.
 *  - Botón con [data-ver-imagen] (y data-imagen/data-descripcion) para ampliar la foto.
 *  - Diálogo #carrito con #carrito-items, #carrito-total, #carrito-vacio,
 *    #carrito-pedido y los botones [data-vaciar-carrito] y [data-finalizar-pedido].
 *  - Contadores [data-contador-carrito] en la cabecera.
 */
(function () {
  "use strict";

  const CLAVE = "productos";
  const moneda = new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" });

  // --- Persistencia --------------------------------------------------------

  function leer() {
    try {
      const datos = JSON.parse(localStorage.getItem(CLAVE));
      return Array.isArray(datos) ? datos : [];
    } catch {
      return [];
    }
  }

  function guardar(productos) {
    localStorage.setItem(CLAVE, JSON.stringify(productos));
    actualizarContadores();
  }

  function total(productos) {
    return productos.reduce((suma, p) => suma + parseFloat(p.precio) * parseFloat(p.cantidad), 0);
  }

  // --- Acciones ------------------------------------------------------------

  function agregar(elemento) {
    const d = elemento.dataset;
    const input = elemento.querySelector("[data-cantidad]");
    const cantidad = Math.max(1, parseInt(input?.value, 10) || 1);
    if (input) input.value = cantidad;

    const productos = leer();
    const existente = productos.find((p) => p.id === d.codigo);
    if (existente) {
      existente.cantidad = String(cantidad);
    } else {
      productos.push({
        id: d.codigo,
        imagen: d.imagen,
        descripcion: d.descripcion,
        precio: d.precio,
        unidad: d.unidad,
        cantidad: String(cantidad),
      });
    }
    guardar(productos);
    window.mostrarAviso?.(existente ? "Cantidad actualizada en el carrito" : "Producto añadido al carrito");
  }

  function cambiarCantidad(id, cantidad) {
    const productos = leer();
    const producto = productos.find((p) => p.id === id);
    if (!producto) return;
    if (cantidad <= 0) {
      guardar(productos.filter((p) => p.id !== id));
    } else {
      producto.cantidad = String(cantidad);
      guardar(productos);
    }
    renderizar();
    sincronizarCantidades();
  }

  function vaciar() {
    guardar([]);
    renderizar();
    sincronizarCantidades();
  }

  // --- Interfaz ------------------------------------------------------------

  function actualizarContadores() {
    const cantidad = leer().length;
    document.querySelectorAll("[data-contador-carrito]").forEach((c) => {
      c.textContent = cantidad;
      c.classList.toggle("hidden", cantidad === 0);
    });
  }

  // Muestra en cada artículo de la página la cantidad que ya está en el carrito
  function sincronizarCantidades() {
    const enCarrito = new Map(leer().map((p) => [p.id, p.cantidad]));
    document.querySelectorAll("[data-producto]").forEach((el) => {
      const input = el.querySelector("[data-cantidad]");
      const boton = el.querySelector("[data-agregar]");
      const cantidad = enCarrito.get(el.dataset.codigo);
      if (input) input.value = cantidad || 1;
      if (boton) {
        boton.textContent = cantidad ? "Actualizar" : "Agregar";
        boton.classList.toggle("btn-oscuro", Boolean(cantidad));
        boton.classList.toggle("btn-primario", !cantidad);
      }
    });
  }

  function crear(etiqueta, clases, texto) {
    const el = document.createElement(etiqueta);
    if (clases) el.className = clases;
    if (texto !== undefined) el.textContent = texto;
    return el;
  }

  function renderizar() {
    const lista = document.getElementById("carrito-items");
    const vacio = document.getElementById("carrito-vacio");
    const pie = document.getElementById("carrito-pie");
    const totalEl = document.getElementById("carrito-total");
    if (!lista) return;

    const productos = leer();
    lista.replaceChildren();
    vacio?.classList.toggle("hidden", productos.length > 0);
    pie?.classList.toggle("hidden", productos.length === 0);

    for (const p of productos) {
      const fila = crear("li", "flex items-center gap-4 py-4");
      fila.dataset.id = p.id;

      const img = crear("img", "size-16 shrink-0 rounded-lg bg-stone-100 object-contain p-1 ring-1 ring-stone-200");
      img.src = p.imagen;
      img.alt = "";

      const info = crear("div", "min-w-0 flex-1");
      info.append(
        crear("p", "truncate text-sm font-medium text-stone-900", p.descripcion),
        crear("p", "text-xs text-stone-500", `Cód. ${p.id} · ${p.unidad} · ${moneda.format(parseFloat(p.precio))} c/u`)
      );

      const cantidad = crear("input", "input-cantidad");
      cantidad.type = "number";
      cantidad.min = "0";
      cantidad.value = p.cantidad;
      cantidad.setAttribute("aria-label", `Cantidad de ${p.descripcion}`);
      cantidad.addEventListener("change", () => cambiarCantidad(p.id, parseInt(cantidad.value, 10) || 0));

      const subtotal = crear(
        "p",
        "hidden w-28 text-right text-sm font-semibold text-stone-900 sm:block",
        moneda.format(parseFloat(p.precio) * parseFloat(p.cantidad))
      );

      const quitar = crear("button", "btn btn-fantasma btn-sm text-red-600 hover:text-red-700", "Quitar");
      quitar.type = "button";
      quitar.addEventListener("click", () => cambiarCantidad(p.id, 0));

      fila.append(img, info, cantidad, subtotal, quitar);
      lista.append(fila);
    }
    if (totalEl) totalEl.textContent = moneda.format(total(productos));
  }

  // --- Eventos -------------------------------------------------------------

  document.addEventListener("click", (evento) => {
    const agregarBtn = evento.target.closest("[data-agregar]");
    if (agregarBtn) {
      agregar(agregarBtn.closest("[data-producto]"));
      sincronizarCantidades();
      return;
    }

    const verImagen = evento.target.closest("[data-ver-imagen]");
    if (verImagen) {
      const dialogo = document.getElementById("visor-imagen");
      dialogo.querySelector("img").src = verImagen.dataset.imagen;
      dialogo.querySelector("img").alt = verImagen.dataset.descripcion;
      dialogo.querySelector("[data-titulo]").textContent = verImagen.dataset.descripcion;
      dialogo.showModal();
      return;
    }

    if (evento.target.closest("[data-abrir-dialogo='carrito']")) {
      document.getElementById("carrito-pedido")?.classList.add("hidden");
      renderizar();
      return;
    }

    if (evento.target.closest("[data-vaciar-carrito]")) {
      if (confirm("¿Vaciar el carrito?")) vaciar();
      return;
    }

    if (evento.target.closest("[data-finalizar-pedido]")) {
      document.getElementById("carrito-pedido")?.classList.remove("hidden");
    }
  });

  document.getElementById("form-pedido")?.addEventListener("submit", (evento) => {
    evento.preventDefault();
    // TODO: enviar el pedido al servidor (no implementado en el backend todavía).
    window.mostrarAviso?.("El envío de pedidos todavía no está implementado.", "info");
  });

  actualizarContadores();
  sincronizarCantidades();
})();

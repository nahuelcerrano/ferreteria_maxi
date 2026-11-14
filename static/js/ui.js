/*
 * Interacciones generales del sitio (sin dependencias):
 *  - menú de navegación en celulares
 *  - cierre de mensajes y de diálogos <dialog>
 *  - avisos flotantes (toasts): window.mostrarAviso("texto", "exito" | "info" | "error")
 */
(function () {
  "use strict";

  // Menú móvil
  const botonMenu = document.querySelector("[data-menu-boton]");
  const menu = document.querySelector("[data-menu]");
  if (botonMenu && menu) {
    botonMenu.addEventListener("click", () => {
      const abierto = menu.classList.toggle("hidden") === false;
      botonMenu.setAttribute("aria-expanded", String(abierto));
    });
  }

  // Botones que cierran el mensaje que los contiene
  document.addEventListener("click", (evento) => {
    const cerrar = evento.target.closest("[data-cerrar-mensaje]");
    if (cerrar) cerrar.closest("[data-mensaje]")?.remove();
  });

  // Diálogos: abrir con data-abrir-dialogo="id", cerrar con data-cerrar-dialogo o clic en el fondo
  document.addEventListener("click", (evento) => {
    const abrir = evento.target.closest("[data-abrir-dialogo]");
    if (abrir) {
      document.getElementById(abrir.dataset.abrirDialogo)?.showModal();
      return;
    }
    const cerrar = evento.target.closest("[data-cerrar-dialogo]");
    if (cerrar) {
      cerrar.closest("dialog")?.close();
      return;
    }
    if (evento.target instanceof HTMLDialogElement) evento.target.close();
  });

  // Avisos flotantes
  const ESTILOS = {
    exito: "bg-emerald-600",
    info: "bg-stone-900",
    error: "bg-red-600",
  };

  window.mostrarAviso = function (mensaje, tipo = "exito") {
    let zona = document.getElementById("zona-avisos");
    if (!zona) {
      zona = document.createElement("div");
      zona.id = "zona-avisos";
      zona.className = "pointer-events-none fixed top-20 right-4 z-50 flex flex-col items-end gap-2";
      zona.setAttribute("aria-live", "polite");
      document.body.append(zona);
    }
    const aviso = document.createElement("div");
    aviso.className = `${ESTILOS[tipo] || ESTILOS.info} pointer-events-auto rounded-lg px-4 py-3 text-sm font-medium text-white shadow-lg transition duration-300 opacity-0 translate-y-2`;
    aviso.textContent = mensaje;
    zona.append(aviso);
    requestAnimationFrame(() => aviso.classList.remove("opacity-0", "translate-y-2"));
    setTimeout(() => {
      aviso.classList.add("opacity-0");
      setTimeout(() => aviso.remove(), 300);
    }, 3000);
  };
})();

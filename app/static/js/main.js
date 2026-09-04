// JS global. Scripts específicos de un módulo pueden ir en su propio
// archivo dentro de static/js/ (ej. static/js/inventario.js) e incluirse
// solo en los templates que lo necesiten.

// --- Menú lateral (sidebar) ---
document.addEventListener("DOMContentLoaded", function () {
  var boton = document.getElementById("menu-toggle");
  var overlay = document.getElementById("sidebar-overlay");

  if (!boton) return;

  function aplicarEstado(abierto) {
    document.body.classList.toggle("menu-abierto", abierto);
    boton.setAttribute("aria-expanded", abierto ? "true" : "false");
  }

  // En pantallas anchas el menú arranca visible; en móvil, oculto.
  aplicarEstado(window.innerWidth >= 992);

  boton.addEventListener("click", function () {
    aplicarEstado(!document.body.classList.contains("menu-abierto"));
  });

  if (overlay) {
    overlay.addEventListener("click", function () {
      aplicarEstado(false);
    });
  }
});

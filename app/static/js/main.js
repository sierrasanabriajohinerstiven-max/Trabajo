// JS global. Scripts específicos de un módulo pueden ir en su propio
// archivo dentro de static/js/ (ej. static/js/inventario.js) e incluirse
// solo en los templates que lo necesiten.

// --- Menú lateral (sidebar) ---
document.addEventListener("DOMContentLoaded", function () {
  var boton = document.getElementById("menu-toggle");
  var sidebar = document.getElementById("sidebar");
  var overlay = document.getElementById("sidebar-overlay");

  if (!boton || !sidebar || !overlay) return;

  function alternarMenu() {
    var abierto = sidebar.classList.toggle("abierto");
    overlay.classList.toggle("visible", abierto);
    boton.setAttribute("aria-expanded", abierto ? "true" : "false");
  }

  function cerrarMenu() {
    sidebar.classList.remove("abierto");
    overlay.classList.remove("visible");
    boton.setAttribute("aria-expanded", "false");
  }

  boton.addEventListener("click", alternarMenu);
  overlay.addEventListener("click", cerrarMenu);
});

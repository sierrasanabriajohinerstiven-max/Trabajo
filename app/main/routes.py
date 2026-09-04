"""Rutas del inicio y del dashboard (resumen del negocio)."""
from flask import render_template

from app.main import bp
from app.main.services import resumen_panel

# NOTA: las vistas están temporalmente SIN @login_required para poder navegar
# el panel mientras Persona A implementa el formulario de login.
# TODO (Persona A): volver a proteger estas rutas con @login_required.

# Accesos rápidos del inicio. Cada entrada: (texto, endpoint, id del icono)
SECCIONES = [
    ("Dashboard", "main.dashboard", "i-tablero"),
    ("Facturas", "facturas.index", "i-facturas"),
    ("Inventario", "inventario.index", "i-inventario"),
    ("Ventas", "ventas.index", "i-ventas"),
    ("Proveedores", "proveedores.index", "i-proveedores"),
]


@bp.route("/")
def index():
    return render_template("main/inicio.html", secciones=SECCIONES)


@bp.route("/dashboard")
def dashboard():
    return render_template("main/dashboard.html", resumen=resumen_panel())

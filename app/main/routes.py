"""Ruta del dashboard: resumen general del D1 y accesos rápidos."""
from flask import render_template

from app.main import bp
from app.main.services import resumen_panel

# NOTA: vista temporalmente SIN @login_required mientras Persona A
# implementa el login. TODO (Persona A): volver a protegerla.

# Accesos rápidos del dashboard. Cada entrada: (texto, endpoint, id del icono)
SECCIONES = [
    ("Facturas", "facturas.index", "i-facturas"),
    ("Inventario", "inventario.index", "i-inventario"),
    ("Ventas", "ventas.index", "i-ventas"),
    ("Proveedores", "proveedores.index", "i-proveedores"),
]


@bp.route("/")
def dashboard():
    return render_template(
        "main/dashboard.html", resumen=resumen_panel(), secciones=SECCIONES
    )

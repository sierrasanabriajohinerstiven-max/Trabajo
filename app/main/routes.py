"""Ruta del panel de inicio: resumen del negocio + accesos a cada sección."""
from flask import render_template
from flask_login import login_required

from app.main import bp
from app.main.services import resumen_panel

# Accesos rápidos del panel. Cada entrada: (texto, endpoint, id del icono)
SECCIONES = [
    ("Facturas", "facturas.index", "i-facturas"),
    ("Inventario", "inventario.index", "i-inventario"),
    ("Ventas", "ventas.index", "i-ventas"),
    ("Proveedores", "proveedores.index", "i-proveedores"),
]


@bp.route("/")
@login_required
def index():
    return render_template(
        "main/dashboard.html", secciones=SECCIONES, resumen=resumen_panel()
    )

"""Ruta del dashboard: menú principal con un botón hacia cada sección."""
from flask import render_template
from flask_login import login_required

from app.main import bp

# Botones del menú principal. Cada entrada: (texto, endpoint del blueprint, ícono)
SECCIONES = [
    ("Facturas", "facturas.index", "🧾"),
    ("Inventario", "inventario.index", "📦"),
    ("Ventas", "ventas.index", "💵"),
    ("Proveedores", "proveedores.index", "🚚"),
]


@bp.route("/")
@login_required
def index():
    return render_template("main/dashboard.html", secciones=SECCIONES)

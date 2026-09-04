"""Rutas (vistas) del módulo inventario.

Control de stock: altas, bajas y ajustes de inventario.

Responsable: Persona B
"""
from flask import render_template

from app.inventario import bp


# NOTA: vista temporalmente SIN @login_required mientras Persona A
# implementa el login. TODO (Persona A): volver a protegerla.
@bp.route("/")
def index():
    # TODO (Persona B): listar Producto
    return render_template("inventario/listado.html")

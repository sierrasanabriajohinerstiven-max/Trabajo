"""Rutas (vistas) del módulo inventario.

Control de stock: altas, bajas y ajustes de inventario.

Responsable: Persona B
"""
from flask import render_template
from flask_login import login_required

from app.inventario import bp


@bp.route("/")
@login_required
def index():
    # TODO (Persona B): listar Producto
    return render_template("inventario/listado.html")

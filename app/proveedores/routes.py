"""Rutas (vistas) del módulo proveedores.

Alta y gestión de proveedores que abastecen el inventario.

Responsable: Persona B
"""
from flask import render_template
from flask_login import login_required

from app.proveedores import bp


@bp.route("/")
@login_required
def index():
    # TODO (Persona B): listar Proveedor
    return render_template("proveedores/listado.html")

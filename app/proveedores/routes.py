"""Rutas (vistas) del módulo proveedores.

Alta y gestión de proveedores que abastecen el inventario.

Responsable: Persona B
"""
from flask import render_template

from app.proveedores import bp


# NOTA: vista temporalmente SIN @login_required mientras Persona A
# implementa el login. TODO (Persona A): volver a protegerla.
@bp.route("/")
def index():
    # TODO (Persona B): listar Proveedor
    return render_template("proveedores/listado.html")

"""Rutas (vistas) del módulo facturas.

Emisión y consulta de facturas, generadas a partir de una venta.

Responsable: Persona A
"""
from flask import render_template

from app.facturas import bp


# NOTA: vista temporalmente SIN @login_required mientras Persona A
# implementa el login. TODO (Persona A): volver a protegerla.
@bp.route("/")
def index():
    # TODO (Persona A): listar Factura
    return render_template("facturas/listado.html")

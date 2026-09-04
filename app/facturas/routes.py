"""Rutas (vistas) del módulo facturas.

Emisión y consulta de facturas, generadas a partir de una venta.

Responsable: Persona A
"""
from flask import render_template
from flask_login import login_required

from app.facturas import bp


@bp.route("/")
@login_required
def index():
    # TODO (Persona A): listar Factura
    return render_template("facturas/listado.html")

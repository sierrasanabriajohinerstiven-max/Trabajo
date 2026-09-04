"""Consulta y exportación imprimible de facturas."""
from flask import abort, render_template
from flask_login import login_required
"""Rutas (vistas) del módulo facturas.

Emisión y consulta de facturas, generadas a partir de una venta.

Responsable: Persona A
"""
from flask import render_template

from app.facturas import bp
from app.facturas.models import Factura
from app.extensions import db


# NOTA: vista temporalmente SIN @login_required mientras Persona A
# implementa el login. TODO (Persona A): volver a protegerla.
@bp.route("/")
def index():
    facturas = Factura.query.order_by(Factura.fecha.desc(), Factura.id.desc()).all()
    return render_template("facturas/listado.html", facturas=facturas)


@bp.route("/<int:factura_id>/imprimir")
@login_required
def imprimir(factura_id):
    factura = db.session.get(Factura, factura_id)
    if factura is None:
        abort(404)
    return render_template("facturas/imprimir.html", factura=factura)

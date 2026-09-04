"""Consulta y exportación imprimible de facturas."""
from flask import abort, render_template
from flask_login import login_required

from app.facturas import bp
from app.facturas.models import Factura
from app.extensions import db


@bp.route("/")
@login_required
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

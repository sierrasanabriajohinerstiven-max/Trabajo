"""Rutas (vistas) del módulo ventas.

Registro de ventas; cada venta debe poder generar una factura.

Responsable: Persona C
"""
from flask import render_template
from flask_login import login_required

from app.ventas import bp


@bp.route("/")
@login_required
def index():
    # TODO (Persona C): listar Venta
    return render_template("ventas/listado.html")

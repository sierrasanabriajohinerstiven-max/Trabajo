"""Rutas (vistas) del módulo ventas.

Registro de ventas; cada venta debe poder generar una factura.

Responsable: Persona C
"""
from flask import render_template

from app.ventas import bp


# NOTA: vista temporalmente SIN @login_required mientras Persona A
# implementa el login. TODO (Persona A): volver a protegerla.
@bp.route("/")
def index():
    # TODO (Persona C): listar Venta
    return render_template("ventas/listado.html")

"""Rutas (vistas) del módulo auth: login cerrado (sin registro público).

Responsable: Persona A
"""
from flask import render_template

from app.auth import bp

# TODO (Persona A):
# - GET/POST /auth/login  -> valida credenciales, flask_login.login_user()
# - GET      /auth/logout -> flask_login.logout_user() (usar @login_required)
# - Los usuarios se crean por un admin/seed, NO hay registro público.


@bp.route("/login")
def login():
    return render_template("auth/login.html")

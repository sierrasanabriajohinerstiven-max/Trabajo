"""Rutas (vistas) del módulo auth: login cerrado (sin registro público).

Responsable: Persona A
"""
from flask import flash, redirect, render_template, url_for
from flask_login import logout_user

from app.auth import bp

# TODO (Persona A):
# - POST /auth/login -> validar credenciales con el formulario y
#   flask_login.login_user(usuario, remember=...)
# - Los usuarios se crean por un admin/seed, NO hay registro público.


@bp.route("/login")
def login():
    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Cierra la sesión. Sin @login_required para que el enlace del menú
    funcione siempre y no rebote al login cuando no hay sesión activa."""
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))

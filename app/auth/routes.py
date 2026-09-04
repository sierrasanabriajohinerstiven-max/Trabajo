"""Rutas (vistas) del módulo auth: login cerrado (sin registro público).

Responsable: Persona A
"""
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from urllib.parse import urlsplit

from app.auth import bp
from app.auth.forms import LoginForm
from app.models.usuario import Usuario

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("facturas.index"))
# TODO (Persona A):
# - POST /auth/login -> validar credenciales con el formulario y
#   flask_login.login_user(usuario, remember=...)
# - Los usuarios se crean por un admin/seed, NO hay registro público.

    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data.lower().strip()).first()
        if usuario and usuario.activo and usuario.check_password(form.password.data):
            login_user(usuario)
            siguiente = request.args.get("next")
            if not siguiente or urlsplit(siguiente).netloc or not siguiente.startswith("/"):
                siguiente = url_for("facturas.index")
            return redirect(siguiente)
        flash("Correo o contraseña incorrectos.", "error")
    return render_template("auth/login.html", form=form)

@bp.route("/login")
def login():
    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Cierra la sesión. Sin @login_required para que el enlace del menú
    funcione siempre y no rebote cuando no hay sesión activa."""
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    # TODO (Persona A): cuando exista el login real, redirigir a auth.login.
    return redirect(url_for("main.index"))

"""Modelo de Usuario, compartido por toda la app (login cerrado: sin
registro público, los usuarios se dan de alta por un admin o por seed).

Responsable principal: Persona A (módulo auth), pero es compartido porque
otros módulos pueden necesitar referenciar quién creó/modificó un registro
(por ejemplo factura.usuario_id, venta.usuario_id).
"""
from flask_login import UserMixin

from app.extensions import db, login_manager


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    # TODO (Persona A): métodos set_password / check_password (usar
    # werkzeug.security: generate_password_hash / check_password_hash)


@login_manager.user_loader
def load_usuario(usuario_id: str):
    return db.session.get(Usuario, int(usuario_id))

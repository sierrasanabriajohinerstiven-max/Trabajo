"""Modelo de Usuario, compartido por toda la app (login cerrado: sin
registro público, los usuarios se dan de alta por un admin o por seed).

Responsable principal: Persona A (módulo auth), pero es compartido porque
otros módulos pueden necesitar referenciar quién creó/modificó un registro
(por ejemplo factura.usuario_id, venta.usuario_id).
"""
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_usuario(usuario_id: str):
    return Usuario.query.get(int(usuario_id))

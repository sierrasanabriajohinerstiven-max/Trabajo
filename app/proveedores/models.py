"""Modelos de datos del módulo proveedores.

Responsable: Persona B

NOTA: este modelo es el "contrato" de datos base del sistema (otros módulos
lo referencian). Amplíalo con los campos que necesites, pero evita renombrar
la tabla o la clave primaria sin avisar al equipo.
"""
from app.extensions import db


class Proveedor(db.Model):
    __tablename__ = "proveedores"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    nit = db.Column(db.String(40), unique=True)
    telefono = db.Column(db.String(40))
    email = db.Column(db.String(120))
    activo = db.Column(db.Boolean, default=True, nullable=False)

    productos = db.relationship("Producto", back_populates="proveedor")

    def __repr__(self) -> str:
        return f"<Proveedor {self.nombre}>"

    # TODO (Persona B): dirección, ciudad, contacto, condiciones de pago...

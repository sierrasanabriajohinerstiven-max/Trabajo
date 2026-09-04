"""Modelos de datos del módulo facturas.

Responsable: Persona A

Una factura se emite a partir de una venta ya registrada (relación 1 a 1).
"""
from app.extensions import db
from app.utils import ahora_utc


class Factura(db.Model):
    __tablename__ = "facturas"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(40), unique=True, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=ahora_utc, index=True)
    total = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    venta_id = db.Column(db.Integer, db.ForeignKey("ventas.id"), unique=True)
    venta = db.relationship("Venta")

    def __repr__(self) -> str:
        return f"<Factura {self.numero}>"

    # TODO (Persona A): datos del cliente, impuestos, estado (emitida/anulada).

"""Modelos de datos del módulo ventas.

Responsable: Persona C

NOTA: estos modelos son el "contrato" de datos base (facturas y el resumen
del panel los consultan). Amplíalos con lo que necesites, pero evita
renombrar tablas o claves primarias sin avisar al equipo.
"""
from app.extensions import db
from app.utils import ahora_utc


class Venta(db.Model):
    __tablename__ = "ventas"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False, default=ahora_utc, index=True)
    total = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    cliente = db.Column(db.String(120))

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    usuario = db.relationship("Usuario")

    detalles = db.relationship(
        "DetalleVenta", back_populates="venta", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Venta {self.id} total={self.total}>"

    # TODO (Persona C): método de pago, estado (pagada/anulada), descuento...


class DetalleVenta(db.Model):
    """Una línea de la venta: qué producto se vendió, cuántos y a qué precio."""

    __tablename__ = "detalles_venta"

    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    precio_unitario = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    venta_id = db.Column(db.Integer, db.ForeignKey("ventas.id"), nullable=False)
    venta = db.relationship("Venta", back_populates="detalles")

    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    producto = db.relationship("Producto")

    @property
    def subtotal(self):
        return (self.precio_unitario or 0) * (self.cantidad or 0)

    def __repr__(self) -> str:
        return f"<DetalleVenta venta={self.venta_id} producto={self.producto_id}>"

    # TODO (Persona C): al guardar una venta, descontar stock del Producto.

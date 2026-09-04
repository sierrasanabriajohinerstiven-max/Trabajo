"""Modelos de datos del módulo inventario.

Responsable: Persona B

NOTA: este modelo es el "contrato" de datos base del sistema (ventas y el
resumen del panel lo consultan). Amplíalo con los campos que necesites, pero
evita renombrar la tabla o la clave primaria sin avisar al equipo.
"""
from app.extensions import db


class Producto(db.Model):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    sku = db.Column(db.String(60), unique=True)
    descripcion = db.Column(db.String(255))
    precio = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"))
    proveedor = db.relationship("Proveedor", back_populates="productos")

    @property
    def valor_en_stock(self):
        """Precio * unidades disponibles (valor inmovilizado de este producto)."""
        return (self.precio or 0) * (self.stock or 0)

    def __repr__(self) -> str:
        return f"<Producto {self.nombre} stock={self.stock}>"

    # TODO (Persona B): categoría, stock mínimo para alertas, unidad de medida...

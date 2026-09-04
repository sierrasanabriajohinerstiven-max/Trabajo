"""Modelos de datos del módulo inventario.

Un producto es cada referencia que el D1 tiene en bodega. Puede estar
asociado a un proveedor, que es quien lo abastece.

Responsable: Persona B

NOTA: este modelo es el "contrato" de datos base del sistema (ventas y el
resumen del panel lo consultan). Amplíalo con los campos que necesites, pero
evita renombrar la tabla o la clave primaria sin avisar al equipo.
"""
from app.extensions import db
from app.utils import ahora_utc

STOCK_BAJO = 5  # unidades o menos se consideran stock bajo


class Producto(db.Model):
    """Referencia de inventario."""

    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)

    # --- Identificación ---
    nombre = db.Column(db.String(120), nullable=False)
    sku = db.Column(db.String(60), unique=True, index=True)
    descripcion = db.Column(db.String(255))

    # --- Precio y existencias ---
    precio = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    stock = db.Column(db.Integer, nullable=False, default=0)

    # --- Estado ---
    activo = db.Column(db.Boolean, nullable=False, default=True)

    # --- Auditoría ---
    creado_en = db.Column(db.DateTime, nullable=False, default=ahora_utc)
    actualizado_en = db.Column(
        db.DateTime, nullable=False, default=ahora_utc, onupdate=ahora_utc
    )

    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"))
    proveedor = db.relationship("Proveedor", back_populates="productos")

    def __repr__(self) -> str:  # pragma: no cover - solo ayuda al depurar
        return f"<Producto {self.nombre} stock={self.stock}>"

    @property
    def estado(self) -> str:
        """Texto legible del estado, para mostrar en las plantillas."""
        return "Activo" if self.activo else "Inactivo"

    @property
    def valor_en_stock(self):
        """Precio * unidades disponibles (valor inmovilizado de este producto)."""
        return (self.precio or 0) * (self.stock or 0)

    @property
    def stock_bajo(self) -> bool:
        return (self.stock or 0) <= STOCK_BAJO

    @classmethod
    def buscar(cls, termino: str | None = None, estado: str | None = None):
        """Consulta de listado con filtro de texto y de estado.

        - `termino` busca en nombre, SKU y nombre del proveedor.
        - `estado` acepta "activos", "inactivos", "stock_bajo" o None/"todos".
        """
        from app.proveedores.models import Proveedor

        consulta = cls.query.outerjoin(Proveedor, cls.proveedor_id == Proveedor.id)

        if termino:
            patron = f"%{termino.strip()}%"
            consulta = consulta.filter(
                db.or_(
                    cls.nombre.ilike(patron),
                    cls.sku.ilike(patron),
                    Proveedor.nombre.ilike(patron),
                )
            )

        if estado == "activos":
            consulta = consulta.filter(cls.activo.is_(True))
        elif estado == "inactivos":
            consulta = consulta.filter(cls.activo.is_(False))
        elif estado == "stock_bajo":
            consulta = consulta.filter(cls.stock <= STOCK_BAJO)

        return consulta.order_by(cls.nombre.asc())

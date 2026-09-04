"""Modelos de datos del módulo proveedores.

Un proveedor es la empresa o persona que abastece los productos del
inventario. Se identifica de forma única por su NIT.

Responsable: Persona B

NOTA: este modelo es el "contrato" de datos base del sistema (otros módulos
lo referencian). Amplíalo con los campos que necesites, pero evita renombrar
la tabla o la clave primaria sin avisar al equipo.
"""
from app.extensions import db
from app.utils import ahora_utc


class Proveedor(db.Model):
    """Empresa o persona que abastece productos al inventario."""

    __tablename__ = "proveedores"

    id = db.Column(db.Integer, primary_key=True)

    # --- Identificación ---
    nombre = db.Column(db.String(120), nullable=False)
    nit = db.Column(db.String(40), unique=True, nullable=False, index=True)

    # --- Contacto ---
    contacto = db.Column(db.String(120))
    email = db.Column(db.String(120))
    telefono = db.Column(db.String(40))

    # --- Ubicación ---
    direccion = db.Column(db.String(200))
    ciudad = db.Column(db.String(80))

    # --- Estado y notas ---
    activo = db.Column(db.Boolean, nullable=False, default=True)
    notas = db.Column(db.Text)

    # --- Auditoría ---
    creado_en = db.Column(db.DateTime, nullable=False, default=ahora_utc)
    actualizado_en = db.Column(
        db.DateTime, nullable=False, default=ahora_utc, onupdate=ahora_utc
    )

    # Productos de inventario que abastece este proveedor.
    productos = db.relationship("Producto", back_populates="proveedor")

    def __repr__(self) -> str:  # pragma: no cover - solo ayuda al depurar
        return f"<Proveedor {self.nit} {self.nombre}>"

    @property
    def estado(self) -> str:
        """Texto legible del estado, para mostrar en las plantillas."""
        return "Activo" if self.activo else "Inactivo"

    @staticmethod
    def normalizar_nit(nit: str) -> str:
        """Deja el NIT en un formato comparable: sin espacios, puntos ni guiones."""
        if not nit:
            return ""
        return "".join(c for c in nit if c.isalnum()).upper()

    @classmethod
    def buscar(cls, termino: str | None = None, estado: str | None = None):
        """Consulta de listado con filtro de texto y de estado.

        - `termino` busca en nombre, NIT, contacto y ciudad.
        - `estado` acepta "activos", "inactivos" o None/"todos".
        """
        consulta = cls.query

        if termino:
            patron = f"%{termino.strip()}%"
            consulta = consulta.filter(
                db.or_(
                    cls.nombre.ilike(patron),
                    cls.nit.ilike(patron),
                    cls.contacto.ilike(patron),
                    cls.ciudad.ilike(patron),
                )
            )

        if estado == "activos":
            consulta = consulta.filter(cls.activo.is_(True))
        elif estado == "inactivos":
            consulta = consulta.filter(cls.activo.is_(False))

        return consulta.order_by(cls.nombre.asc())

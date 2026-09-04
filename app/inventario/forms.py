"""Formularios (Flask-WTF) del módulo inventario.

Responsable: Persona B
"""
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DecimalField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)

from app.inventario.models import Producto
from app.proveedores.models import Proveedor

SIN_PROVEEDOR = 0


class ProductoForm(FlaskForm):
    """Alta y edición de un producto del inventario.

    Al editar hay que pasar `producto_id` para que la validación de SKU
    único no choque contra el propio registro que se está editando.
    """

    nombre = StringField(
        "Nombre del producto",
        validators=[DataRequired("El nombre es obligatorio."), Length(max=120)],
    )
    sku = StringField("Código / SKU", validators=[Optional(), Length(max=60)])
    descripcion = TextAreaField(
        "Descripción", validators=[Optional(), Length(max=255)]
    )
    precio = DecimalField(
        "Precio unitario",
        places=2,
        validators=[
            DataRequired("El precio es obligatorio."),
            NumberRange(min=0, message="El precio no puede ser negativo."),
        ],
    )
    stock = IntegerField(
        "Unidades en bodega",
        validators=[
            DataRequired("El stock es obligatorio."),
            NumberRange(min=0, message="El stock no puede ser negativo."),
        ],
    )
    proveedor_id = SelectField("Proveedor", coerce=int, validators=[Optional()])
    activo = BooleanField("Producto activo", default=True)
    submit = SubmitField("Guardar")

    def __init__(self, *args, producto_id: int | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.producto_id = producto_id
        # El desplegable se llena aquí para que siempre tenga las opciones
        # válidas, tanto al pintar el formulario como al validarlo.
        self.proveedor_id.choices = [(SIN_PROVEEDOR, "— Sin proveedor —")] + [
            (p.id, p.nombre)
            for p in Proveedor.query.order_by(Proveedor.nombre).all()
        ]

    def validate_sku(self, campo) -> None:
        """El SKU es opcional, pero si se usa debe ser único."""
        valor = (campo.data or "").strip().upper()
        if not valor:
            campo.data = None
            return

        existente = Producto.query.filter_by(sku=valor).first()
        if existente is not None and existente.id != self.producto_id:
            raise ValidationError("Ya existe un producto con ese código.")

        campo.data = valor

    def volcar_en(self, producto: Producto) -> Producto:
        """Copia los datos validados del formulario al modelo."""
        producto.nombre = self.nombre.data.strip()
        producto.sku = self.sku.data
        producto.descripcion = (self.descripcion.data or "").strip() or None
        producto.precio = self.precio.data
        producto.stock = self.stock.data
        producto.activo = bool(self.activo.data)
        producto.proveedor_id = self.proveedor_id.data or None
        return producto


class EliminarProductoForm(FlaskForm):
    """Formulario vacío: existe solo para proteger el borrado con CSRF."""

    submit = SubmitField("Eliminar")

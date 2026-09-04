"""Formularios (Flask-WTF) del módulo inventario.

Responsable: Persona B
"""
from flask_wtf import FlaskForm
from wtforms import BooleanField, DecimalField, IntegerField, SelectField, StringField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ProductoForm(FlaskForm):
    nombre = StringField(
        "Nombre", validators=[DataRequired("El nombre es obligatorio."), Length(max=120)]
    )
    sku = StringField("Código / SKU", validators=[Optional(), Length(max=60)])
    descripcion = StringField("Descripción", validators=[Optional(), Length(max=255)])
    precio = DecimalField(
        "Precio",
        places=2,
        validators=[
            DataRequired("El precio es obligatorio."),
            NumberRange(min=0, message="El precio no puede ser negativo."),
        ],
    )
    stock = IntegerField(
        "Stock",
        validators=[
            DataRequired("El stock es obligatorio."),
            NumberRange(min=0, message="El stock no puede ser negativo."),
        ],
    )
    proveedor_id = SelectField("Proveedor", coerce=int, validators=[Optional()])
    activo = BooleanField("Activo", default=True)

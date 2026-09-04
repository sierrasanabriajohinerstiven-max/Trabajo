"""Formularios (Flask-WTF) del módulo ventas.

Una venta se abre vacía (VentaForm) y se le van agregando líneas de
producto (DetalleVentaForm) hasta que el vendedor la da por terminada.

Responsable: Persona C
"""
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class VentaForm(FlaskForm):
    """Abre una venta nueva. El cliente es opcional (venta de mostrador)."""

    cliente = StringField("Cliente", validators=[Optional(), Length(max=120)])
    submit = SubmitField("Iniciar venta")


class DetalleVentaForm(FlaskForm):
    """Agrega una línea de producto a una venta ya abierta.

    `producto_id.choices` se llena en la vista con los productos activos
    (necesita una consulta a la base de datos, por eso no se define aquí).
    """

    producto_id = SelectField(
        "Producto", coerce=int, validators=[DataRequired("Elige un producto.")]
    )
    cantidad = IntegerField(
        "Cantidad",
        default=1,
        validators=[DataRequired(), NumberRange(min=1, message="Mínimo 1 unidad.")],
    )
    submit = SubmitField("Agregar producto")


class EliminarForm(FlaskForm):
    """Formulario vacío: solo protege borrados/acciones con token CSRF."""

    submit = SubmitField("Eliminar")

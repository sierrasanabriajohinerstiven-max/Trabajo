"""Formularios (Flask-WTF) del módulo proveedores.

Responsable: Persona B
"""
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    Optional,
    ValidationError,
)

from app.proveedores.models import Proveedor


class ProveedorForm(FlaskForm):
    """Alta y edición de un proveedor.

    Al editar hay que pasar `proveedor_id` para que la validación de NIT
    único no choque contra el propio registro que se está editando.
    """

    nombre = StringField(
        "Nombre o razón social",
        validators=[DataRequired("El nombre es obligatorio."), Length(max=120)],
    )
    nit = StringField(
        "NIT",
        validators=[DataRequired("El NIT es obligatorio."), Length(max=30)],
    )
    contacto = StringField(
        "Persona de contacto", validators=[Optional(), Length(max=120)]
    )
    email = StringField(
        "Correo electrónico",
        validators=[Optional(), Email("Escribe un correo válido."), Length(max=120)],
    )
    telefono = StringField("Teléfono", validators=[Optional(), Length(max=30)])
    direccion = StringField("Dirección", validators=[Optional(), Length(max=200)])
    ciudad = StringField("Ciudad", validators=[Optional(), Length(max=80)])
    activo = BooleanField("Proveedor activo", default=True)
    notas = TextAreaField("Notas", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Guardar")

    def __init__(self, *args, proveedor_id: int | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.proveedor_id = proveedor_id

    def validate_nit(self, campo) -> None:
        """El NIT debe ser único entre todos los proveedores."""
        normalizado = Proveedor.normalizar_nit(campo.data)
        if not normalizado:
            raise ValidationError("El NIT debe contener letras o números.")

        existente = Proveedor.query.filter_by(nit=normalizado).first()
        if existente is not None and existente.id != self.proveedor_id:
            raise ValidationError("Ya existe un proveedor con ese NIT.")

        # Se guarda siempre normalizado para que la unicidad sea real.
        campo.data = normalizado

    def volcar_en(self, proveedor: Proveedor) -> Proveedor:
        """Copia los datos validados del formulario al modelo."""
        proveedor.nombre = self.nombre.data.strip()
        proveedor.nit = self.nit.data
        proveedor.contacto = (self.contacto.data or "").strip() or None
        proveedor.email = (self.email.data or "").strip() or None
        proveedor.telefono = (self.telefono.data or "").strip() or None
        proveedor.direccion = (self.direccion.data or "").strip() or None
        proveedor.ciudad = (self.ciudad.data or "").strip() or None
        proveedor.activo = bool(self.activo.data)
        proveedor.notas = (self.notas.data or "").strip() or None
        return proveedor


class EliminarProveedorForm(FlaskForm):
    """Formulario vacío: existe solo para proteger el borrado con CSRF."""

    submit = SubmitField("Eliminar")

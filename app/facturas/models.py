"""Modelo de datos de facturas."""
from datetime import date

from app.extensions import db


class Factura(db.Model):
	__tablename__ = "facturas"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(40), unique=True, nullable=False)
    cliente = db.Column(db.String(160), nullable=False)
    fecha = db.Column(db.Date, nullable=False, default=date.today)
    total = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    estado = db.Column(db.String(20), nullable=False, default="pendiente")
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

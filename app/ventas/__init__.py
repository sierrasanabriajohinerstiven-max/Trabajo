"""Blueprint de ventas. Responsable: Persona C."""
from flask import Blueprint

bp = Blueprint("ventas", __name__, template_folder="../templates/ventas")

from app.ventas import routes  # noqa: E402,F401

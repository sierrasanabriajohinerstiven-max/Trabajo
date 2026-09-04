"""Blueprint de inventario. Responsable: Persona B."""
from flask import Blueprint

bp = Blueprint("inventario", __name__, template_folder="../templates/inventario")

from app.inventario import routes  # noqa: E402,F401

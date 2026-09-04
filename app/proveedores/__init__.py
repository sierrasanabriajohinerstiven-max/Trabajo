"""Blueprint de proveedores. Responsable: Persona B."""
from flask import Blueprint

bp = Blueprint("proveedores", __name__, template_folder="../templates/proveedores")

from app.proveedores import routes  # noqa: E402,F401

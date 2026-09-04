"""Blueprint de facturas. Responsable: Persona A."""
from flask import Blueprint

bp = Blueprint("facturas", __name__, template_folder="../templates/facturas")

from app.facturas import routes  # noqa: E402,F401

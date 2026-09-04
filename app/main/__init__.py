"""Blueprint del dashboard (menú principal). Compartido por los 3 módulos."""
from flask import Blueprint

bp = Blueprint("main", __name__, template_folder="../templates/main")

from app.main import routes  # noqa: E402,F401

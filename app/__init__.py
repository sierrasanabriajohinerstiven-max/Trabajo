"""App factory: aquí se ensambla la aplicación y se registran los blueprints
de cada módulo. Cada persona registra su propio blueprint en la sección
correspondiente; evitar tocar el resto del archivo para no generar conflictos
de merge innecesarios.
"""
from flask import Flask

from app.config import Config
from app.extensions import db, login_manager, migrate


def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # --- Extensiones ---
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = "auth.login"

    # --- Modelos compartidos (necesarios para que las migraciones los vean) ---
    from app.models import usuario  # noqa: F401

    # --- Blueprints ---
    # Persona A - Login / Autenticación
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # Persona A - Facturas
    from app.facturas import bp as facturas_bp
    app.register_blueprint(facturas_bp, url_prefix="/facturas")

    # Persona B - Inventario
    from app.inventario import bp as inventario_bp
    app.register_blueprint(inventario_bp, url_prefix="/inventario")

    # Persona B - Proveedores
    from app.proveedores import bp as proveedores_bp
    app.register_blueprint(proveedores_bp, url_prefix="/proveedores")

    # Persona C - Ventas
    from app.ventas import bp as ventas_bp
    app.register_blueprint(ventas_bp, url_prefix="/ventas")

    return app

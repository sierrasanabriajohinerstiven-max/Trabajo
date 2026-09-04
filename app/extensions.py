"""Instancias de extensiones de Flask, separadas para evitar imports circulares.

Cada blueprint importa lo que necesite desde aquí, por ejemplo:
    from app.extensions import db
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

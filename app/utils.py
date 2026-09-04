"""Utilidades compartidas por todos los módulos."""
from datetime import datetime, timezone


def ahora_utc() -> datetime:
    """Fecha y hora actual en UTC, sin zona horaria (naive).

    Se usa como valor por defecto de las columnas de fecha. Reemplaza a
    datetime.utcnow(), que quedó deprecado en Python 3.12.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)

"""Consultas que alimentan el resumen del panel de inicio.

Si las tablas todavía no existen (nadie ha corrido `flask db upgrade`), las
funciones devuelven valores en cero en vez de romper la página.
"""
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.inventario.models import Producto
from app.utils import ahora_utc
from app.ventas.models import DetalleVenta, Venta


def _inicio_del_mes() -> datetime:
    hoy = ahora_utc()
    return datetime(hoy.year, hoy.month, 1)


def ventas_del_mes() -> dict:
    """Total facturado y cantidad de ventas del mes en curso."""
    try:
        total, cantidad = (
            db.session.query(func.coalesce(func.sum(Venta.total), 0), func.count(Venta.id))
            .filter(Venta.fecha >= _inicio_del_mes())
            .one()
        )
    except SQLAlchemyError:
        return {"total": 0.0, "cantidad": 0}
    return {"total": float(total or 0), "cantidad": int(cantidad or 0)}


def productos_mas_vendidos(limite: int = 5) -> list:
    """Productos con más unidades vendidas en el mes en curso."""
    try:
        filas = (
            db.session.query(
                Producto.nombre,
                func.coalesce(func.sum(DetalleVenta.cantidad), 0).label("unidades"),
                func.coalesce(
                    func.sum(DetalleVenta.cantidad * DetalleVenta.precio_unitario), 0
                ).label("ingresos"),
            )
            .join(DetalleVenta, DetalleVenta.producto_id == Producto.id)
            .join(Venta, Venta.id == DetalleVenta.venta_id)
            .filter(Venta.fecha >= _inicio_del_mes())
            .group_by(Producto.id, Producto.nombre)
            .order_by(func.sum(DetalleVenta.cantidad).desc())
            .limit(limite)
            .all()
        )
    except SQLAlchemyError:
        return []
    return [
        {"nombre": nombre, "unidades": int(unidades), "ingresos": float(ingresos)}
        for nombre, unidades, ingresos in filas
    ]


def valor_total_inventario() -> dict:
    """Valor del inventario (precio * stock) y unidades totales en bodega."""
    try:
        valor, unidades, referencias = (
            db.session.query(
                func.coalesce(func.sum(Producto.precio * Producto.stock), 0),
                func.coalesce(func.sum(Producto.stock), 0),
                func.count(Producto.id),
            )
            .filter(Producto.activo.is_(True))
            .one()
        )
    except SQLAlchemyError:
        return {"valor": 0.0, "unidades": 0, "referencias": 0}
    return {
        "valor": float(valor or 0),
        "unidades": int(unidades or 0),
        "referencias": int(referencias or 0),
    }


def resumen_panel() -> dict:
    """Junta todos los indicadores que muestra el panel de inicio."""
    return {
        "ventas_mes": ventas_del_mes(),
        "mas_vendidos": productos_mas_vendidos(),
        "inventario": valor_total_inventario(),
    }

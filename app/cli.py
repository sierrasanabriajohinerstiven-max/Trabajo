"""Comandos de consola del proyecto.

Uso:
    flask datos-demo      carga proveedores, productos y ventas de ejemplo
    flask datos-demo --limpiar   borra los datos antes de cargarlos
"""
from datetime import timedelta

import click
from flask import Flask

from app.extensions import db
from app.facturas.models import Factura
from app.inventario.models import Producto
from app.proveedores.models import Proveedor
from app.utils import ahora_utc
from app.ventas.models import DetalleVenta, Venta

# (nombre, NIT, contacto, ciudad)
PROVEEDORES = [
    ("Distribuidora Norte S.A.S.", "900123456", "Ana Gómez", "Bogotá"),
    ("Alimentos del Valle", "800654321", "Carlos Ruiz", "Cali"),
    ("Aseo Total Ltda.", "901222333", "Marta Díaz", "Medellín"),
    ("Lácteos La Pradera", "900777888", "Jorge Peña", "Bucaramanga"),
    ("Panificadora El Trigal", "901444555", "Lucía Ramírez", "Bogotá"),
    ("Bebidas y Jugos S.A.", "800999111", "Andrés Molina", "Barranquilla"),
    ("Cárnicos San Jorge", "901666777", "Diana Torres", "Villavicencio"),
    ("Granos y Cereales del Sur", "900333222", "Felipe Cárdenas", "Pasto"),
    ("Higiene Personal Plus", "901888999", "Sandra Vargas", "Medellín"),
    ("Comercializadora El Ahorro", "800111222", "Óscar Beltrán", "Ibagué"),
]

# (nombre, sku, precio, stock, índice del proveedor)
# Varios quedan con stock <= 5 a propósito, para que el dashboard tenga
# productos en "por reponer".
PRODUCTOS = [
    ("Arroz Diana 500g", "ARR500", 3200, 120, 7),
    ("Aceite Girasol 1L", "ACE1000", 9800, 45, 1),
    ("Leche Entera 1L", "LEC1000", 4100, 3, 3),
    ("Panela Cuadrada 500g", "PAN500", 4500, 60, 1),
    ("Jabón Rey 300g", "JAB300", 2800, 2, 2),
    ("Detergente Polvo 900g", "DET900", 11500, 30, 2),
    ("Café Molido 250g", "CAF250", 8900, 5, 0),
    ("Azúcar Blanca 1kg", "AZU1000", 5200, 80, 7),
    ("Pan Tajado 500g", "PANTAJ500", 5600, 18, 4),
    ("Gaseosa Cola 1.5L", "GAS1500", 4700, 4, 5),
]

# Cada venta es una lista de líneas: (índice del producto, cantidad)
VENTAS = [
    [(0, 4), (2, 2), (7, 1)],
    [(1, 1), (5, 1)],
    [(0, 10), (3, 3)],
    [(6, 2), (4, 5)],
    [(8, 2), (9, 3)],
    [(0, 2), (1, 1), (7, 2)],
    [(2, 1), (8, 1)],
    [(3, 4), (5, 1), (9, 2)],
    [(6, 1), (4, 2), (0, 3)],
    [(7, 5), (1, 2), (8, 1)],
]


def _fecha_de_venta(indice: int):
    """Reparte las ventas hacia atrás en el tiempo, sin salirse del mes.

    Así el dashboard muestra cifras distintas en "ventas de hoy" y "ventas
    de este mes". El tope es el día 1 del mes en curso: si el comando se
    corre a principio de mes, las ventas se agrupan en los primeros días
    en vez de caer en el mes anterior (donde no las contaría el resumen).
    """
    ahora = ahora_utc()
    inicio_mes = ahora.replace(day=1, hour=0, minute=1, second=0, microsecond=0)
    return max(ahora - timedelta(hours=8 * indice), inicio_mes)


def registrar_comandos(app: Flask) -> None:
    """Engancha los comandos al objeto Flask (se llama desde create_app)."""

    @app.cli.command("datos-demo")
    @click.option(
        "--limpiar",
        is_flag=True,
        help="Borra proveedores, productos, ventas y facturas antes de cargar.",
    )
    def datos_demo(limpiar: bool) -> None:
        """Carga datos de ejemplo para ver el panel funcionando."""
        if limpiar:
            Factura.query.delete()
            DetalleVenta.query.delete()
            Venta.query.delete()
            Producto.query.delete()
            Proveedor.query.delete()
            db.session.commit()
            click.echo("Datos anteriores borrados.")

        if Producto.query.count():
            click.echo(
                "Ya hay productos cargados. Usa --limpiar si quieres reemplazarlos."
            )
            return

        proveedores = [
            Proveedor(nombre=n, nit=nit, contacto=c, ciudad=ciudad)
            for n, nit, c, ciudad in PROVEEDORES
        ]
        db.session.add_all(proveedores)
        db.session.flush()

        productos = [
            Producto(
                nombre=nombre,
                sku=sku,
                precio=precio,
                stock=stock,
                proveedor=proveedores[idx],
            )
            for nombre, sku, precio, stock, idx in PRODUCTOS
        ]
        db.session.add_all(productos)
        db.session.flush()

        for numero, lineas in enumerate(VENTAS, start=1):
            venta = Venta(
                fecha=_fecha_de_venta(numero - 1), cliente=f"Cliente {numero}"
            )
            venta.detalles = [
                DetalleVenta(
                    producto=productos[i],
                    cantidad=cantidad,
                    precio_unitario=productos[i].precio,
                )
                for i, cantidad in lineas
            ]
            venta.total = sum(d.subtotal for d in venta.detalles)
            db.session.add(venta)
            db.session.flush()

            db.session.add(
                Factura(
                    numero=f"FAC-{numero:04d}", venta=venta, total=venta.total
                )
            )

        db.session.commit()

        click.echo(
            f"Listo: {len(proveedores)} proveedores, {len(productos)} productos, "
            f"{len(VENTAS)} ventas y sus facturas."
        )

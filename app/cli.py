"""Comandos de consola del proyecto.

Uso:
    flask datos-demo      carga proveedores, productos y ventas de ejemplo
    flask datos-demo --limpiar   borra los datos antes de cargarlos
"""
import click
from flask import Flask

from app.extensions import db
from app.facturas.models import Factura
from app.inventario.models import Producto
from app.proveedores.models import Proveedor
from app.utils import ahora_utc
from app.ventas.models import DetalleVenta, Venta

PROVEEDORES = [
    ("Distribuidora Norte S.A.S.", "900123456", "Ana Gómez", "Bogotá"),
    ("Alimentos del Valle", "800654321", "Carlos Ruiz", "Cali"),
    ("Aseo Total Ltda.", "901222333", "Marta Díaz", "Medellín"),
]

# (nombre, sku, precio, stock, indice del proveedor)
PRODUCTOS = [
    ("Arroz Diana 500g", "ARR500", 3200, 120, 1),
    ("Aceite Girasol 1L", "ACE1000", 9800, 45, 1),
    ("Leche Entera 1L", "LEC1000", 4100, 3, 1),
    ("Panela Cuadrada 500g", "PAN500", 4500, 60, 1),
    ("Jabón Rey 300g", "JAB300", 2800, 2, 2),
    ("Detergente Polvo 900g", "DET900", 11500, 30, 2),
    ("Café Molido 250g", "CAF250", 8900, 5, 0),
    ("Azúcar Blanca 1kg", "AZU1000", 5200, 80, 0),
]

# (indice del producto, cantidad)
VENTAS = [
    [(0, 4), (2, 2), (7, 1)],
    [(1, 1), (5, 1)],
    [(0, 10), (3, 3)],
    [(6, 2), (4, 5)],
]


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
            venta = Venta(fecha=ahora_utc(), cliente=f"Cliente {numero}")
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

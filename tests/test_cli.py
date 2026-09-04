"""Pruebas del comando `flask datos-demo`."""
import pytest

from app import create_app
from app.cli import PRODUCTOS, PROVEEDORES, VENTAS
from app.config import Config
from app.extensions import db
from app.facturas.models import Factura
from app.inventario.models import Producto
from app.main.services import resumen_panel
from app.proveedores.models import Proveedor
from app.ventas.models import Venta


class ConfigPrueba(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SECRET_KEY = "prueba"
    TESTING = True


@pytest.fixture
def app():
    aplicacion = create_app(ConfigPrueba)
    with aplicacion.app_context():
        db.create_all()
        yield aplicacion
        db.session.remove()
        db.drop_all()


def test_carga_diez_de_cada_uno(app):
    app.test_cli_runner().invoke(args=["datos-demo"])

    assert Proveedor.query.count() == 10
    assert Producto.query.count() == 10
    assert Venta.query.count() == 10
    assert Factura.query.count() == 10


def test_los_datos_son_coherentes(app):
    app.test_cli_runner().invoke(args=["datos-demo"])

    # Cada producto quedó con su proveedor y cada venta con sus líneas.
    assert all(p.proveedor is not None for p in Producto.query.all())
    assert all(v.detalles for v in Venta.query.all())

    # El total de cada venta es la suma de sus líneas.
    for venta in Venta.query.all():
        assert venta.total == sum(d.subtotal for d in venta.detalles)

    # Las ventas caen dentro del mes en curso, para que el resumen las cuente.
    resumen = resumen_panel()
    assert resumen["ventas_mes"]["cantidad"] == 10
    assert resumen["ventas_hoy"]["cantidad"] >= 1

    # Hay productos con stock bajo, para que el dashboard no salga vacío.
    assert resumen["stock_bajo"]


def test_no_duplica_si_ya_hay_datos(app):
    app.test_cli_runner().invoke(args=["datos-demo"])
    resultado = app.test_cli_runner().invoke(args=["datos-demo"])

    assert "Ya hay productos cargados" in resultado.output
    assert Producto.query.count() == 10


def test_limpiar_reemplaza_los_datos(app):
    app.test_cli_runner().invoke(args=["datos-demo"])
    app.test_cli_runner().invoke(args=["datos-demo", "--limpiar"])

    assert Producto.query.count() == 10
    assert Venta.query.count() == 10


def test_los_datos_de_partida_tienen_diez_entradas():
    """Si alguien agrega o quita filas, que la prueba lo avise."""
    assert len(PROVEEDORES) == 10
    assert len(PRODUCTOS) == 10
    assert len(VENTAS) == 10

    # Los SKU no se repiten (la columna es única).
    skus = [sku for _, sku, _, _, _ in PRODUCTOS]
    assert len(set(skus)) == len(skus)

    # Los NIT tampoco.
    nits = [nit for _, nit, _, _ in PROVEEDORES]
    assert len(set(nits)) == len(nits)

    # Cada producto apunta a un proveedor que existe.
    assert all(0 <= idx < len(PROVEEDORES) for *_, idx in PRODUCTOS)

    # Cada línea de venta apunta a un producto que existe.
    for lineas in VENTAS:
        assert all(0 <= i < len(PRODUCTOS) and c > 0 for i, c in lineas)

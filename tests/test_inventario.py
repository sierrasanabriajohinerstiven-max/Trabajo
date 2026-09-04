"""Pruebas del módulo inventario. Responsable: Persona B."""
import pytest

from app import create_app
from app.config import Config
from app.extensions import db
from app.inventario.models import Producto
from app.proveedores.models import Proveedor
from app.utils import ahora_utc
from app.ventas.models import DetalleVenta, Venta


class ConfigPrueba(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SECRET_KEY = "prueba"
    WTF_CSRF_ENABLED = False
    TESTING = True


@pytest.fixture
def app():
    aplicacion = create_app(ConfigPrueba)
    with aplicacion.app_context():
        db.create_all()
        yield aplicacion
        db.session.remove()
        db.drop_all()


@pytest.fixture
def cliente(app):
    return app.test_client()


@pytest.fixture
def proveedor(app):
    p = Proveedor(nombre="Distribuidora Norte", nit="900123")
    db.session.add(p)
    db.session.commit()
    return p


def crear_producto(nombre="Arroz", sku="ARR1", precio=3500, stock=10, proveedor=None):
    producto = Producto(
        nombre=nombre, sku=sku, precio=precio, stock=stock, proveedor=proveedor
    )
    db.session.add(producto)
    db.session.commit()
    return producto


# --- Listado y búsqueda ---


def test_listado_vacio(cliente):
    respuesta = cliente.get("/inventario/")
    assert respuesta.status_code == 200
    assert "Todavía no hay productos" in respuesta.get_data(as_text=True)


def test_listado_muestra_productos_y_valor(cliente, proveedor):
    crear_producto("Arroz", "ARR1", 3500, 10, proveedor)
    crear_producto("Aceite", "ACE1", 8000, 4, proveedor)

    html = cliente.get("/inventario/").get_data(as_text=True)

    assert "Arroz" in html and "Aceite" in html
    # valor en bodega: 3500*10 + 8000*4 = 67.000
    assert "67,000.00" in html
    # el aceite tiene stock 4 (<= 5): se marca como stock bajo
    assert "inv-stock-bajo" in html


def test_busqueda_filtra_por_nombre_sku_y_proveedor(cliente, proveedor):
    crear_producto("Arroz", "ARR1", 3500, 10, proveedor)
    crear_producto("Jabón", "JAB9", 5000, 20, None)

    por_nombre = cliente.get("/inventario/?q=arroz").get_data(as_text=True)
    assert "Arroz" in por_nombre and "Jabón" not in por_nombre

    por_sku = cliente.get("/inventario/?q=JAB9").get_data(as_text=True)
    assert "Jabón" in por_sku and "Arroz" not in por_sku

    por_proveedor = cliente.get("/inventario/?q=Norte").get_data(as_text=True)
    assert "Arroz" in por_proveedor and "Jabón" not in por_proveedor


def test_filtro_por_estado(cliente):
    crear_producto("Bien surtido", "A1", 100, 50)
    inactivo = crear_producto("Descontinuado", "D1", 100, 50)
    inactivo.activo = False
    crear_producto("Casi agotado", "C1", 100, 2)
    db.session.commit()

    solo_activos = cliente.get("/inventario/?estado=activos").get_data(as_text=True)
    assert "Descontinuado" not in solo_activos

    solo_bajos = cliente.get("/inventario/?estado=stock_bajo").get_data(as_text=True)
    assert "Casi agotado" in solo_bajos and "Bien surtido" not in solo_bajos


# --- Alta ---


def test_crear_producto(cliente, proveedor):
    respuesta = cliente.post(
        "/inventario/nuevo",
        data={
            "nombre": "Panela",
            "sku": "pan-1",
            "precio": "4200.50",
            "stock": "30",
            "proveedor_id": str(proveedor.id),
            "activo": "y",
        },
        follow_redirects=True,
    )

    assert respuesta.status_code == 200
    producto = Producto.query.filter_by(nombre="Panela").one()
    assert producto.sku == "PAN-1"  # se normaliza a mayúsculas
    assert float(producto.precio) == 4200.50
    assert producto.proveedor_id == proveedor.id


def test_crear_sin_nombre_falla(cliente):
    respuesta = cliente.post(
        "/inventario/nuevo", data={"nombre": "", "precio": "100", "stock": "1"}
    )
    assert respuesta.status_code == 200
    assert "El nombre es obligatorio." in respuesta.get_data(as_text=True)
    assert Producto.query.count() == 0


def test_sku_duplicado_falla(cliente):
    crear_producto("Arroz", "ARR1")
    respuesta = cliente.post(
        "/inventario/nuevo",
        data={"nombre": "Otro", "sku": "ARR1", "precio": "100", "stock": "1"},
    )
    assert "Ya existe un producto con ese código." in respuesta.get_data(as_text=True)
    assert Producto.query.count() == 1


def test_precio_negativo_falla(cliente):
    respuesta = cliente.post(
        "/inventario/nuevo", data={"nombre": "X", "precio": "-5", "stock": "1"}
    )
    assert "no puede ser negativo" in respuesta.get_data(as_text=True)


# --- Edición ---


def test_editar_producto(cliente):
    producto = crear_producto("Arroz", "ARR1", 3500, 10)

    cliente.post(
        f"/inventario/{producto.id}/editar",
        data={
            "nombre": "Arroz premium",
            "sku": "ARR1",
            "precio": "4000",
            "stock": "25",
            "proveedor_id": "0",
            "activo": "y",
        },
        follow_redirects=True,
    )

    actualizado = db.session.get(Producto, producto.id)
    assert actualizado.nombre == "Arroz premium"
    assert actualizado.stock == 25
    assert actualizado.proveedor_id is None


def test_editar_conserva_su_propio_sku(cliente):
    """El SKU propio no debe chocar con la validación de unicidad."""
    producto = crear_producto("Arroz", "ARR1", 3500, 10)

    cliente.post(
        f"/inventario/{producto.id}/editar",
        data={
            "nombre": "Arroz",
            "sku": "ARR1",
            "precio": "3500",
            "stock": "11",
            "proveedor_id": "0",
            "activo": "y",
        },
        follow_redirects=True,
    )

    assert db.session.get(Producto, producto.id).stock == 11


# --- Borrado ---


def test_eliminar_producto(cliente):
    producto = crear_producto("Arroz", "ARR1")

    cliente.post(f"/inventario/{producto.id}/eliminar", follow_redirects=True)

    assert Producto.query.count() == 0


def test_no_elimina_producto_ya_vendido(cliente):
    """Borrarlo dejaría las ventas sin referencia: se bloquea."""
    producto = crear_producto("Arroz", "ARR1")
    venta = Venta(fecha=ahora_utc(), total=3500)
    venta.detalles = [DetalleVenta(producto=producto, cantidad=1, precio_unitario=3500)]
    db.session.add(venta)
    db.session.commit()

    respuesta = cliente.post(
        f"/inventario/{producto.id}/eliminar", follow_redirects=True
    )

    assert "No se puede eliminar" in respuesta.get_data(as_text=True)
    assert Producto.query.count() == 1


def test_eliminar_producto_inexistente_da_404(cliente):
    assert cliente.post("/inventario/999/eliminar").status_code == 404

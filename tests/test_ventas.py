"""Pruebas del módulo ventas. Responsable: Persona C."""
import pytest

from app import create_app
from app.config import Config
from app.extensions import db
from app.inventario.models import Producto
from app.models.usuario import Usuario
from app.ventas.models import DetalleVenta, Venta


class ConfigPrueba(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


@pytest.fixture
def app():
    app = create_app(ConfigPrueba)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def usuario_id(app):
    with app.app_context():
        usuario = Usuario(nombre="Test", email="test@example.com", password_hash="x")
        db.session.add(usuario)
        db.session.commit()
        return usuario.id


@pytest.fixture
def producto_id(app):
    with app.app_context():
        producto = Producto(nombre="Camiseta", precio=20, stock=10, activo=True)
        db.session.add(producto)
        db.session.commit()
        return producto.id


@pytest.fixture
def client(app, usuario_id):
    # Flask-Login guarda el id del usuario logueado en la sesión bajo la
    # clave "_user_id"; lo fijamos a mano para no depender del módulo auth,
    # que no es responsabilidad de ventas.
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(usuario_id)
    return client


def test_index_accesible_sin_login(app):
    # NOTA: el candado está quitado en todo el sistema mientras Persona A
    # implementa el login real (ver README y el TODO en routes.py).
    resp = app.test_client().get("/ventas/")
    assert resp.status_code == 200


def test_index_vacio(client):
    resp = client.get("/ventas/")
    assert resp.status_code == 200
    assert "no hay ventas" in resp.get_data(as_text=True)


def test_iniciar_venta(app, client, usuario_id):
    resp = client.post("/ventas/nueva", data={"cliente": "Ana"}, follow_redirects=True)
    assert resp.status_code == 200

    with app.app_context():
        ventas = Venta.query.all()
        assert len(ventas) == 1
        assert ventas[0].cliente == "Ana"
        assert ventas[0].usuario_id == usuario_id
        assert float(ventas[0].total) == 0.0


def test_iniciar_venta_sin_sesion_no_falla(app):
    # Sin login todavía no hay current_user; usuario_id debe quedar en None
    # en vez de reventar con un AttributeError.
    resp = app.test_client().post(
        "/ventas/nueva", data={"cliente": "Mostrador"}, follow_redirects=True
    )
    assert resp.status_code == 200

    with app.app_context():
        venta = Venta.query.first()
        assert venta.usuario_id is None


def test_agregar_linea_descuenta_stock_y_suma_total(app, client, usuario_id, producto_id):
    with app.app_context():
        venta = Venta(usuario_id=usuario_id)
        db.session.add(venta)
        db.session.commit()
        venta_id = venta.id

    resp = client.post(
        f"/ventas/{venta_id}/lineas",
        data={"producto_id": str(producto_id), "cantidad": "3"},
        follow_redirects=True,
    )
    assert resp.status_code == 200

    with app.app_context():
        venta = db.session.get(Venta, venta_id)
        producto = db.session.get(Producto, producto_id)
        assert len(venta.detalles) == 1
        assert venta.detalles[0].cantidad == 3
        assert float(venta.detalles[0].precio_unitario) == 20.0
        assert float(venta.total) == 60.0
        assert producto.stock == 7  # 10 - 3


def test_agregar_linea_rechaza_stock_insuficiente(app, client, usuario_id, producto_id):
    with app.app_context():
        venta = Venta(usuario_id=usuario_id)
        db.session.add(venta)
        db.session.commit()
        venta_id = venta.id

    resp = client.post(
        f"/ventas/{venta_id}/lineas",
        data={"producto_id": str(producto_id), "cantidad": "999"},
        follow_redirects=True,
    )
    assert resp.status_code == 200

    with app.app_context():
        venta = db.session.get(Venta, venta_id)
        producto = db.session.get(Producto, producto_id)
        assert len(venta.detalles) == 0
        assert float(venta.total) == 0.0
        assert producto.stock == 10  # sin cambios


def test_eliminar_venta_repone_stock(app, client, usuario_id, producto_id):
    with app.app_context():
        venta = Venta(usuario_id=usuario_id)
        db.session.add(venta)
        db.session.commit()
        linea = DetalleVenta(
            venta_id=venta.id, producto_id=producto_id, cantidad=2, precio_unitario=20
        )
        producto = db.session.get(Producto, producto_id)
        producto.stock -= 2
        venta.total = 40
        db.session.add(linea)
        db.session.commit()
        venta_id = venta.id

    resp = client.post(f"/ventas/{venta_id}/eliminar", follow_redirects=True)
    assert resp.status_code == 200

    with app.app_context():
        assert db.session.get(Venta, venta_id) is None
        producto = db.session.get(Producto, producto_id)
        assert producto.stock == 10  # repuesto

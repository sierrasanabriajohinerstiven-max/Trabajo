"""Pruebas del módulo proveedores. Responsable: Persona B."""
import pytest
from werkzeug.datastructures import MultiDict

from app import create_app
from app.config import Config
from app.extensions import db
from app.proveedores.forms import ProveedorForm
from app.inventario.models import Producto
from app.proveedores.models import Proveedor


class ConfigPruebas(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"  # base en memoria
    WTF_CSRF_ENABLED = False


@pytest.fixture
def app():
    aplicacion = create_app(ConfigPruebas)
    with aplicacion.app_context():
        db.create_all()
        yield aplicacion
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def proveedor(app):
    registro = Proveedor(nombre="Distribuidora Andina", nit="9001234567", ciudad="Bogotá")
    db.session.add(registro)
    db.session.commit()
    return registro


DATOS_VALIDOS = {
    "nombre": "Alimentos del Valle",
    "nit": "900.765.432-1",
    "contacto": "María Ruiz",
    "email": "compras@alimentosvalle.com",
    "telefono": "3005551234",
    "direccion": "Calle 10 #4-55",
    "ciudad": "Cali",
    "activo": "y",
    "notas": "Entrega los martes.",
}


# --- Modelo ---

def test_normalizar_nit_quita_puntos_y_guiones():
    assert Proveedor.normalizar_nit("900.765.432-1") == "9007654321"


def test_estado_legible(app):
    assert Proveedor(nombre="X", nit="1", activo=True).estado == "Activo"
    assert Proveedor(nombre="X", nit="2", activo=False).estado == "Inactivo"


def test_buscar_filtra_por_texto_y_estado(app):
    db.session.add_all([
        Proveedor(nombre="Andina", nit="1", ciudad="Bogotá", activo=True),
        Proveedor(nombre="Costeña", nit="2", ciudad="Barranquilla", activo=False),
    ])
    db.session.commit()

    assert [p.nombre for p in Proveedor.buscar(termino="andi").all()] == ["Andina"]
    assert [p.nombre for p in Proveedor.buscar(termino="barran").all()] == ["Costeña"]
    assert [p.nombre for p in Proveedor.buscar(estado="inactivos").all()] == ["Costeña"]
    assert len(Proveedor.buscar().all()) == 2


# --- Formulario ---

def test_formulario_rechaza_nit_duplicado(app, proveedor):
    form = ProveedorForm(MultiDict({"nombre": "Otra empresa", "nit": "900-123-4567"}))
    assert not form.validate()
    assert "Ya existe un proveedor con ese NIT." in form.nit.errors


def test_formulario_permite_conservar_el_nit_al_editar(app, proveedor):
    form = ProveedorForm(
        MultiDict({"nombre": proveedor.nombre, "nit": proveedor.nit}),
        proveedor_id=proveedor.id,
    )
    assert form.validate(), form.errors


def test_formulario_rechaza_email_invalido(app):
    form = ProveedorForm(MultiDict({"nombre": "X", "nit": "123", "email": "no-es-correo"}))
    assert not form.validate()
    assert form.email.errors


# --- Vistas ---

def test_listado_vacio(client):
    respuesta = client.get("/proveedores/")
    assert respuesta.status_code == 200
    assert "Todavía no hay proveedores" in respuesta.get_data(as_text=True)


def test_listado_muestra_proveedores(client, proveedor):
    texto = client.get("/proveedores/").get_data(as_text=True)
    assert "Distribuidora Andina" in texto
    assert "9001234567" in texto


def test_listado_busca_por_termino(client, proveedor):
    assert "Distribuidora Andina" in client.get("/proveedores/?q=andina").get_data(as_text=True)
    assert "Distribuidora Andina" not in client.get("/proveedores/?q=zzz").get_data(as_text=True)


def test_listado_filtra_por_estado(client, proveedor):
    texto = client.get("/proveedores/?estado=inactivos").get_data(as_text=True)
    assert "Distribuidora Andina" not in texto


def test_crear_proveedor(client, app):
    respuesta = client.post("/proveedores/nuevo", data=DATOS_VALIDOS, follow_redirects=True)
    assert respuesta.status_code == 200

    creado = Proveedor.query.filter_by(nombre="Alimentos del Valle").one()
    assert creado.nit == "9007654321"  # se guarda normalizado
    assert creado.activo is True
    assert "Alimentos del Valle" in respuesta.get_data(as_text=True)


def test_crear_proveedor_sin_nombre_no_guarda_nada(client, app):
    datos = dict(DATOS_VALIDOS, nombre="")
    respuesta = client.post("/proveedores/nuevo", data=datos)
    assert respuesta.status_code == 200
    assert Proveedor.query.count() == 0


def test_detalle(client, proveedor):
    texto = client.get(f"/proveedores/{proveedor.id}").get_data(as_text=True)
    assert "Distribuidora Andina" in texto
    assert "Bogotá" in texto


def test_detalle_inexistente_da_404(client):
    assert client.get("/proveedores/999").status_code == 404


def test_editar_proveedor(client, proveedor):
    datos = dict(DATOS_VALIDOS, nombre="Distribuidora Andina S.A.", nit=proveedor.nit)
    client.post(f"/proveedores/{proveedor.id}/editar", data=datos, follow_redirects=True)

    assert db.session.get(Proveedor, proveedor.id).nombre == "Distribuidora Andina S.A."


def test_cambiar_estado_alterna_activo(client, proveedor):
    client.post(f"/proveedores/{proveedor.id}/estado", follow_redirects=True)
    assert db.session.get(Proveedor, proveedor.id).activo is False

    client.post(f"/proveedores/{proveedor.id}/estado", follow_redirects=True)
    assert db.session.get(Proveedor, proveedor.id).activo is True


def test_eliminar_proveedor(client, proveedor):
    respuesta = client.post(f"/proveedores/{proveedor.id}/eliminar", follow_redirects=True)
    assert respuesta.status_code == 200
    assert Proveedor.query.count() == 0


def test_eliminar_solo_acepta_post(client, proveedor):
    assert client.get(f"/proveedores/{proveedor.id}/eliminar").status_code == 405


# --- Relación con inventario ---

def test_proveedor_lista_sus_productos(app, proveedor):
    db.session.add(Producto(nombre="Arroz 500g", sku="ARR-500", proveedor=proveedor))
    db.session.commit()

    assert [p.nombre for p in proveedor.productos] == ["Arroz 500g"]


def test_no_elimina_proveedor_con_productos(client, app, proveedor):
    db.session.add(Producto(nombre="Arroz 500g", proveedor=proveedor))
    db.session.commit()

    respuesta = client.post(
        f"/proveedores/{proveedor.id}/eliminar", follow_redirects=True
    )
    assert "No se puede eliminar" in respuesta.get_data(as_text=True)
    assert Proveedor.query.count() == 1


def test_detalle_muestra_los_productos(client, app, proveedor):
    db.session.add(Producto(nombre="Arroz 500g", sku="ARR-500", proveedor=proveedor))
    db.session.commit()

    texto = client.get(f"/proveedores/{proveedor.id}").get_data(as_text=True)
    assert "Arroz 500g" in texto
    assert "ARR-500" in texto

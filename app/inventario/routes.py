"""Rutas (vistas) del módulo inventario.

Control de stock: listar, buscar, crear, editar y eliminar productos.

Responsable: Persona B
"""
from flask import flash, redirect, render_template, request, url_for

from app.extensions import db
from app.inventario import bp
from app.inventario.forms import ProductoForm
from app.inventario.models import Producto
from app.proveedores.models import Proveedor

# NOTA: vistas temporalmente SIN @login_required mientras Persona A
# implementa el login. TODO (Persona A): volver a protegerlas.

SIN_PROVEEDOR = 0


def _cargar_proveedores(form: ProductoForm) -> None:
    """Llena el desplegable de proveedores con los que estén registrados."""
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    form.proveedor_id.choices = [(SIN_PROVEEDOR, "— Sin proveedor —")] + [
        (p.id, p.nombre) for p in proveedores
    ]


@bp.route("/")
def index():
    busqueda = (request.args.get("q") or "").strip()

    consulta = Producto.query
    if busqueda:
        patron = f"%{busqueda}%"
        consulta = consulta.filter(
            db.or_(Producto.nombre.ilike(patron), Producto.sku.ilike(patron))
        )

    productos = consulta.order_by(Producto.nombre).all()
    return render_template(
        "inventario/listado.html", productos=productos, busqueda=busqueda
    )


@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    form = ProductoForm()
    _cargar_proveedores(form)

    if form.validate_on_submit():
        producto = Producto()
        _volcar_form(form, producto)
        db.session.add(producto)
        db.session.commit()
        flash(f"Producto «{producto.nombre}» agregado.", "success")
        return redirect(url_for("inventario.index"))

    return render_template("inventario/formulario.html", form=form, producto=None)


@bp.route("/<int:producto_id>/editar", methods=["GET", "POST"])
def editar(producto_id: int):
    producto = db.get_or_404(Producto, producto_id)
    form = ProductoForm(obj=producto)
    _cargar_proveedores(form)

    if form.validate_on_submit():
        _volcar_form(form, producto)
        db.session.commit()
        flash(f"Producto «{producto.nombre}» actualizado.", "success")
        return redirect(url_for("inventario.index"))

    if request.method == "GET":
        form.proveedor_id.data = producto.proveedor_id or SIN_PROVEEDOR

    return render_template("inventario/formulario.html", form=form, producto=producto)


@bp.route("/<int:producto_id>/eliminar", methods=["POST"])
def eliminar(producto_id: int):
    producto = db.get_or_404(Producto, producto_id)
    nombre = producto.nombre
    db.session.delete(producto)
    db.session.commit()
    flash(f"Producto «{nombre}» eliminado.", "danger")
    return redirect(url_for("inventario.index"))


def _volcar_form(form: ProductoForm, producto: Producto) -> None:
    """Pasa los datos del formulario al modelo."""
    producto.nombre = form.nombre.data
    producto.sku = form.sku.data or None
    producto.descripcion = form.descripcion.data or None
    producto.precio = form.precio.data
    producto.stock = form.stock.data
    producto.activo = form.activo.data
    producto.proveedor_id = form.proveedor_id.data or None

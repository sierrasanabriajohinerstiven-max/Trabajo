"""Rutas (vistas) del módulo inventario.

Control de stock: altas, bajas y ajustes de inventario.

Endpoints:
    GET       /inventario/                  listado con búsqueda y filtro
    GET/POST  /inventario/nuevo             alta de producto
    GET/POST  /inventario/<id>/editar       edición
    POST      /inventario/<id>/eliminar     borrado definitivo

Responsable: Persona B
"""
from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import func

from app.extensions import db
from app.inventario import bp
from app.inventario.forms import EliminarProductoForm, ProductoForm
from app.inventario.models import STOCK_BAJO, Producto
from app.ventas.models import DetalleVenta

ESTADOS = (
    ("todos", "Todos"),
    ("activos", "Activos"),
    ("inactivos", "Inactivos"),
    ("stock_bajo", "Stock bajo"),
)

# NOTA: igual que el resto de secciones, estas vistas están temporalmente SIN
# @login_required mientras Persona A implementa el login.
# TODO (Persona A): volver a protegerlas.


@bp.route("/")
def index():
    termino = request.args.get("q", "", type=str).strip()
    estado = request.args.get("estado", "todos", type=str)
    if estado not in dict(ESTADOS):
        estado = "todos"

    productos = Producto.buscar(termino=termino, estado=estado).all()

    valor_total = db.session.query(
        func.coalesce(func.sum(Producto.precio * Producto.stock), 0)
    ).filter(Producto.activo.is_(True)).scalar()

    return render_template(
        "inventario/listado.html",
        productos=productos,
        termino=termino,
        estado=estado,
        estados=ESTADOS,
        total=Producto.query.count(),
        total_activos=Producto.query.filter_by(activo=True).count(),
        valor_total=float(valor_total or 0),
        stock_bajo=STOCK_BAJO,
        form_eliminar=EliminarProductoForm(),
    )


@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    form = ProductoForm()

    if form.validate_on_submit():
        producto = form.volcar_en(Producto())
        db.session.add(producto)
        db.session.commit()
        flash(f"Producto «{producto.nombre}» creado correctamente.", "exito")
        return redirect(url_for("inventario.index"))

    return render_template(
        "inventario/formulario.html", form=form, producto=None, titulo="Nuevo producto"
    )


@bp.route("/<int:producto_id>/editar", methods=["GET", "POST"])
def editar(producto_id: int):
    producto = db.get_or_404(Producto, producto_id)
    form = ProductoForm(obj=producto, producto_id=producto.id)

    if form.validate_on_submit():
        form.volcar_en(producto)
        db.session.commit()
        flash(f"Producto «{producto.nombre}» actualizado.", "exito")
        return redirect(url_for("inventario.index"))

    return render_template(
        "inventario/formulario.html",
        form=form,
        producto=producto,
        titulo=f"Editar: {producto.nombre}",
    )


@bp.route("/<int:producto_id>/eliminar", methods=["POST"])
def eliminar(producto_id: int):
    producto = db.get_or_404(Producto, producto_id)
    form = EliminarProductoForm()

    if not form.validate_on_submit():
        flash("No se pudo eliminar el producto.", "error")
        return redirect(url_for("inventario.index"))

    # Un producto ya vendido no se borra: dejaría las ventas sin referencia.
    # Se sugiere desactivarlo, que conserva el historial.
    veces_vendido = DetalleVenta.query.filter_by(producto_id=producto.id).count()
    if veces_vendido:
        flash(
            f"No se puede eliminar «{producto.nombre}»: aparece en "
            f"{veces_vendido} venta(s). Desactívalo si ya no lo vendes.",
            "error",
        )
        return redirect(url_for("inventario.index"))

    nombre = producto.nombre
    db.session.delete(producto)
    db.session.commit()
    flash(f"Producto «{nombre}» eliminado.", "exito")
    return redirect(url_for("inventario.index"))

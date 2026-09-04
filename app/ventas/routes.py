"""Rutas (vistas) del módulo ventas.

Una venta se abre vacía y se le van agregando líneas de producto
(DetalleVenta); cada línea agregada descuenta stock de ese Producto y suma
su importe al total de la venta. Cada venta debe poder generar una factura
(pendiente: módulo facturas).

Responsable: Persona C

Endpoints:
    GET       /ventas/                              listado
    GET/POST  /ventas/nueva                         abre una venta nueva
    GET       /ventas/<id>                          detalle: líneas + alta de línea
    POST      /ventas/<id>/lineas                   agrega un producto (descuenta stock)
    POST      /ventas/<id>/eliminar                 elimina la venta y repone el stock
"""
from flask import flash, redirect, render_template, url_for
from flask_login import current_user

from app.extensions import db
from app.inventario.models import Producto
from app.ventas import bp
from app.ventas.forms import DetalleVentaForm, EliminarForm, VentaForm
from app.ventas.models import DetalleVenta, Venta

# NOTA: vistas temporalmente SIN @login_required mientras Persona A
# implementa el login (ver README). TODO (Persona A): volver a protegerlas.


def _opciones_producto():
    """Productos activos para el <select>, con su stock a la vista."""
    productos = Producto.query.filter_by(activo=True).order_by(Producto.nombre).all()
    return [(p.id, f"{p.nombre} — stock: {p.stock} — $ {p.precio}") for p in productos]


@bp.route("/")
def index():
    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    return render_template("ventas/listado.html", ventas=ventas)


@bp.route("/nueva", methods=["GET", "POST"])
def nueva():
    form = VentaForm()

    if form.validate_on_submit():
        venta = Venta(
            cliente=(form.cliente.data or "").strip() or None,
            usuario_id=current_user.id if current_user.is_authenticated else None,
        )
        db.session.add(venta)
        db.session.commit()
        flash("Venta iniciada. Ahora agrega los productos vendidos.", "exito")
        return redirect(url_for("ventas.detalle", venta_id=venta.id))

    return render_template("ventas/nueva.html", form=form)


@bp.route("/<int:venta_id>")
def detalle(venta_id):
    venta = db.get_or_404(Venta, venta_id)
    form = DetalleVentaForm()
    form.producto_id.choices = _opciones_producto()
    return render_template(
        "ventas/detalle.html",
        venta=venta,
        form=form,
        form_eliminar=EliminarForm(),
    )


@bp.route("/<int:venta_id>/lineas", methods=["POST"])
def agregar_linea(venta_id):
    venta = db.get_or_404(Venta, venta_id)
    form = DetalleVentaForm()
    form.producto_id.choices = _opciones_producto()

    if not form.validate_on_submit():
        for errores in form.errors.values():
            for error in errores:
                flash(error, "error")
        return redirect(url_for("ventas.detalle", venta_id=venta.id))

    producto = db.get_or_404(Producto, form.producto_id.data)
    cantidad = form.cantidad.data

    # Decisión de negocio: no se permite vender más unidades de las que hay
    # en stock (se rechaza la línea con un error) en vez de dejarlo en
    # negativo. Si el equipo prefiere permitir "pedidos pendientes"
    # (backorder), este es el único punto que hay que cambiar.
    if cantidad > producto.stock:
        flash(
            f"Stock insuficiente de «{producto.nombre}»: quedan {producto.stock} unidades.",
            "error",
        )
        return redirect(url_for("ventas.detalle", venta_id=venta.id))

    linea = DetalleVenta(
        venta_id=venta.id,
        producto_id=producto.id,
        cantidad=cantidad,
        precio_unitario=producto.precio,
    )
    producto.stock -= cantidad
    venta.total = (venta.total or 0) + linea.precio_unitario * cantidad

    db.session.add(linea)
    db.session.commit()
    flash(f"«{producto.nombre}» agregado a la venta.", "exito")
    return redirect(url_for("ventas.detalle", venta_id=venta.id))


@bp.route("/<int:venta_id>/eliminar", methods=["POST"])
def eliminar(venta_id):
    venta = db.get_or_404(Venta, venta_id)
    form = EliminarForm()

    if not form.validate_on_submit():
        flash("No se pudo eliminar la venta.", "error")
        return redirect(url_for("ventas.detalle", venta_id=venta.id))

    # Anular una venta repone el stock de cada línea que la componía.
    for linea in venta.detalles:
        if linea.producto is not None:
            linea.producto.stock += linea.cantidad

    db.session.delete(venta)  # cascade="all, delete-orphan" borra sus líneas
    db.session.commit()
    flash("Venta eliminada y stock repuesto.", "info")
    return redirect(url_for("ventas.index"))

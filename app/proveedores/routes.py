"""Rutas (vistas) del módulo proveedores.

Alta y gestión de proveedores que abastecen el inventario.

Endpoints:
    GET       /proveedores/                  listado con búsqueda y filtro
    GET/POST  /proveedores/nuevo             alta de proveedor
    GET       /proveedores/<id>              ficha del proveedor
    GET/POST  /proveedores/<id>/editar       edición
    POST      /proveedores/<id>/estado       activar / desactivar
    POST      /proveedores/<id>/eliminar     borrado definitivo

Responsable: Persona B
"""
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.extensions import db
from app.proveedores import bp
from app.proveedores.forms import EliminarProveedorForm, ProveedorForm
from app.proveedores.models import Proveedor

ESTADOS = (
    ("todos", "Todos"),
    ("activos", "Activos"),
    ("inactivos", "Inactivos"),
)


@bp.route("/")
@login_required
def index():
    termino = request.args.get("q", "", type=str).strip()
    estado = request.args.get("estado", "todos", type=str)
    if estado not in dict(ESTADOS):
        estado = "todos"

    proveedores = Proveedor.buscar(termino=termino, estado=estado).all()

    return render_template(
        "proveedores/listado.html",
        proveedores=proveedores,
        termino=termino,
        estado=estado,
        estados=ESTADOS,
        total_activos=Proveedor.query.filter_by(activo=True).count(),
        total=Proveedor.query.count(),
        form_eliminar=EliminarProveedorForm(),
    )


@bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    form = ProveedorForm()

    if form.validate_on_submit():
        proveedor = form.volcar_en(Proveedor())
        db.session.add(proveedor)
        db.session.commit()
        flash(f"Proveedor «{proveedor.nombre}» creado correctamente.", "exito")
        return redirect(url_for("proveedores.detalle", proveedor_id=proveedor.id))

    return render_template(
        "proveedores/formulario.html", form=form, proveedor=None, titulo="Nuevo proveedor"
    )


@bp.route("/<int:proveedor_id>")
@login_required
def detalle(proveedor_id: int):
    proveedor = db.get_or_404(Proveedor, proveedor_id)
    return render_template(
        "proveedores/detalle.html",
        proveedor=proveedor,
        form_eliminar=EliminarProveedorForm(),
    )


@bp.route("/<int:proveedor_id>/editar", methods=["GET", "POST"])
@login_required
def editar(proveedor_id: int):
    proveedor = db.get_or_404(Proveedor, proveedor_id)
    form = ProveedorForm(obj=proveedor, proveedor_id=proveedor.id)

    if form.validate_on_submit():
        form.volcar_en(proveedor)
        db.session.commit()
        flash(f"Proveedor «{proveedor.nombre}» actualizado.", "exito")
        return redirect(url_for("proveedores.detalle", proveedor_id=proveedor.id))

    return render_template(
        "proveedores/formulario.html",
        form=form,
        proveedor=proveedor,
        titulo=f"Editar: {proveedor.nombre}",
    )


@bp.route("/<int:proveedor_id>/estado", methods=["POST"])
@login_required
def cambiar_estado(proveedor_id: int):
    """Activa o desactiva el proveedor sin borrar su historial."""
    proveedor = db.get_or_404(Proveedor, proveedor_id)
    form = EliminarProveedorForm()  # solo se usa para validar el token CSRF

    if not form.validate_on_submit():
        flash("No se pudo cambiar el estado del proveedor.", "error")
        return redirect(url_for("proveedores.detalle", proveedor_id=proveedor.id))

    proveedor.activo = not proveedor.activo
    db.session.commit()
    flash(f"Proveedor «{proveedor.nombre}» marcado como {proveedor.estado.lower()}.", "exito")
    return redirect(url_for("proveedores.detalle", proveedor_id=proveedor.id))


@bp.route("/<int:proveedor_id>/eliminar", methods=["POST"])
@login_required
def eliminar(proveedor_id: int):
    proveedor = db.get_or_404(Proveedor, proveedor_id)
    form = EliminarProveedorForm()

    if not form.validate_on_submit():
        flash("No se pudo eliminar el proveedor.", "error")
        return redirect(url_for("proveedores.detalle", proveedor_id=proveedor.id))

    # TODO (Persona B): cuando Producto tenga proveedor_id, impedir el borrado
    # si el proveedor todavía abastece productos y sugerir desactivarlo.
    nombre = proveedor.nombre
    db.session.delete(proveedor)
    db.session.commit()
    flash(f"Proveedor «{nombre}» eliminado.", "exito")
    return redirect(url_for("proveedores.index"))

"""
routes/producto.py — CRUD de productos.

Patrón estándar de CRUD (se replica en persona, empresa, cliente, vendedor,
rol, ruta). Usa ``current_app.api`` con tabla ``producto``. PK: ``codigo``.

Rutas:
- GET  /productos              → listado
- GET  /productos/nuevo        → formulario crear
- POST /productos/nuevo        → submit crear
- GET  /productos/editar/<pk>  → formulario editar
- POST /productos/editar/<pk>  → submit editar
- POST /productos/eliminar/<pk>→ borrar (con confirmación en template)
"""

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from services.api_service import ApiError

producto_bp = Blueprint("producto", __name__)
TABLA = "producto"
PK = "codigo"


@producto_bp.route("/productos")
def listar():
    try:
        items = current_app.api.listar(TABLA)
    except ApiError as exc:
        flash(f"No se pudo cargar el catálogo: {exc.mensaje}", "danger")
        items = []
    return render_template("pages/producto/listar.html", items=items)


@producto_bp.route("/productos/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "GET":
        return render_template("pages/producto/formulario.html", item={}, editar=False)

    datos = _leer_form(request)
    error = _validar(datos, es_crear=True)
    if error:
        flash(error, "warning")
        return render_template("pages/producto/formulario.html", item=datos, editar=False), 400
    try:
        current_app.api.crear(TABLA, datos)
        flash("Producto creado.", "success")
        return redirect(url_for("producto.listar"))
    except ApiError as exc:
        flash(f"No se pudo crear: {exc.mensaje}", "danger")
        return render_template("pages/producto/formulario.html", item=datos, editar=False), 400


@producto_bp.route("/productos/editar/<pk>", methods=["GET", "POST"])
def editar(pk):
    if request.method == "GET":
        try:
            item = current_app.api.consultar(TABLA, pk) or {}
        except ApiError as exc:
            flash(f"No se pudo cargar el producto: {exc.mensaje}", "danger")
            return redirect(url_for("producto.listar"))
        return render_template("pages/producto/formulario.html", item=item, editar=True)

    datos = _leer_form(request)
    error = _validar(datos, es_crear=False)
    if error:
        flash(error, "warning")
        return render_template("pages/producto/formulario.html", item=datos, editar=True), 400
    try:
        current_app.api.actualizar(TABLA, pk, datos)
        flash("Producto actualizado.", "success")
        return redirect(url_for("producto.listar"))
    except ApiError as exc:
        flash(f"No se pudo actualizar: {exc.mensaje}", "danger")
        return render_template("pages/producto/formulario.html", item=datos, editar=True), 400


@producto_bp.route("/productos/eliminar/<pk>", methods=["POST"])
def eliminar(pk):
    try:
        current_app.api.eliminar(TABLA, pk)
        flash("Producto eliminado.", "success")
    except ApiError as exc:
        # 409 típicamente indica FK que lo referencia.
        if exc.status_code == 409:
            flash("No se puede eliminar: el producto está siendo referenciado.", "warning")
        else:
            flash(f"No se pudo eliminar: {exc.mensaje}", "danger")
    return redirect(url_for("producto.listar"))


def _leer_form(req):
    return {
        "codigo": (req.form.get("codigo") or "").strip(),
        "nombre": (req.form.get("nombre") or "").strip(),
        "stock": int(req.form.get("stock") or 0),
        "valorunitario": float(req.form.get("valorunitario") or 0),
    }


def _validar(datos, es_crear: bool) -> str | None:
    if es_crear and not datos["codigo"]:
        return "El código es obligatorio."
    if not datos["nombre"]:
        return "El nombre es obligatorio."
    if datos["stock"] < 0:
        return "El stock no puede ser negativo."
    if datos["valorunitario"] < 0:
        return "El valor unitario no puede ser negativo."
    return None

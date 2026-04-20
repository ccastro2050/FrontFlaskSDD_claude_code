"""routes/rol.py — CRUD de roles. PK: ``id`` (auto)."""

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from services.api_service import ApiError

rol_bp = Blueprint("rol", __name__)
TABLA = "rol"


@rol_bp.route("/roles")
def listar():
    try:
        items = current_app.api.listar(TABLA)
    except ApiError as exc:
        flash(f"No se pudo cargar: {exc.mensaje}", "danger")
        items = []
    return render_template("pages/rol/listar.html", items=items)


@rol_bp.route("/roles/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "GET":
        return render_template("pages/rol/formulario.html", item={}, editar=False)
    datos = {"nombre": (request.form.get("nombre") or "").strip()}
    if not datos["nombre"]:
        flash("El nombre es obligatorio.", "warning")
        return render_template("pages/rol/formulario.html", item=datos, editar=False), 400
    try:
        current_app.api.crear(TABLA, datos)
        flash("Rol creado.", "success")
        return redirect(url_for("rol.listar"))
    except ApiError as exc:
        flash(f"No se pudo crear: {exc.mensaje}", "danger")
        return render_template("pages/rol/formulario.html", item=datos, editar=False), 400


@rol_bp.route("/roles/editar/<pk>", methods=["GET", "POST"])
def editar(pk):
    if request.method == "GET":
        try:
            item = current_app.api.consultar(TABLA, pk) or {}
        except ApiError as exc:
            flash(f"No se pudo cargar: {exc.mensaje}", "danger")
            return redirect(url_for("rol.listar"))
        return render_template("pages/rol/formulario.html", item=item, editar=True)

    datos = {"nombre": (request.form.get("nombre") or "").strip()}
    if not datos["nombre"]:
        flash("El nombre es obligatorio.", "warning")
        return render_template("pages/rol/formulario.html", item={"id": pk, **datos}, editar=True), 400
    try:
        current_app.api.actualizar(TABLA, pk, datos)
        flash("Rol actualizado.", "success")
        return redirect(url_for("rol.listar"))
    except ApiError as exc:
        flash(f"No se pudo actualizar: {exc.mensaje}", "danger")
        return render_template("pages/rol/formulario.html", item={"id": pk, **datos}, editar=True), 400


@rol_bp.route("/roles/eliminar/<pk>", methods=["POST"])
def eliminar(pk):
    try:
        current_app.api.eliminar(TABLA, pk)
        flash("Rol eliminado.", "success")
    except ApiError as exc:
        if exc.status_code in (400, 409):
            flash("No se puede eliminar: el rol está asignado a usuarios.", "warning")
        else:
            flash(f"No se pudo eliminar: {exc.mensaje}", "danger")
    return redirect(url_for("rol.listar"))

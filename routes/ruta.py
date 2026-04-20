"""routes/ruta.py — CRUD de rutas. PK: ``id`` (auto)."""

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from services.api_service import ApiError

ruta_bp = Blueprint("ruta", __name__)
TABLA = "ruta"


@ruta_bp.route("/rutas")
def listar():
    try:
        items = current_app.api.listar(TABLA)
    except ApiError as exc:
        flash(f"No se pudo cargar: {exc.mensaje}", "danger")
        items = []
    return render_template("pages/ruta/listar.html", items=items)


@ruta_bp.route("/rutas/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "GET":
        return render_template("pages/ruta/formulario.html", item={}, editar=False)
    datos = {
        "ruta": (request.form.get("ruta") or "").strip(),
        "descripcion": (request.form.get("descripcion") or "").strip(),
    }
    if not datos["ruta"] or not datos["descripcion"]:
        flash("Ruta y descripción son obligatorios.", "warning")
        return render_template("pages/ruta/formulario.html", item=datos, editar=False), 400
    try:
        current_app.api.crear(TABLA, datos)
        flash("Ruta creada.", "success")
        return redirect(url_for("ruta.listar"))
    except ApiError as exc:
        flash(f"No se pudo crear: {exc.mensaje}", "danger")
        return render_template("pages/ruta/formulario.html", item=datos, editar=False), 400


@ruta_bp.route("/rutas/editar/<pk>", methods=["GET", "POST"])
def editar(pk):
    if request.method == "GET":
        try:
            item = current_app.api.consultar(TABLA, pk) or {}
        except ApiError as exc:
            flash(f"No se pudo cargar: {exc.mensaje}", "danger")
            return redirect(url_for("ruta.listar"))
        return render_template("pages/ruta/formulario.html", item=item, editar=True)

    datos = {
        "ruta": (request.form.get("ruta") or "").strip(),
        "descripcion": (request.form.get("descripcion") or "").strip(),
    }
    if not datos["ruta"] or not datos["descripcion"]:
        flash("Ruta y descripción son obligatorios.", "warning")
        return render_template("pages/ruta/formulario.html", item={"id": pk, **datos}, editar=True), 400
    try:
        current_app.api.actualizar(TABLA, pk, datos)
        flash("Ruta actualizada.", "success")
        return redirect(url_for("ruta.listar"))
    except ApiError as exc:
        flash(f"No se pudo actualizar: {exc.mensaje}", "danger")
        return render_template("pages/ruta/formulario.html", item={"id": pk, **datos}, editar=True), 400


@ruta_bp.route("/rutas/eliminar/<pk>", methods=["POST"])
def eliminar(pk):
    try:
        current_app.api.eliminar(TABLA, pk)
        flash("Ruta eliminada.", "success")
    except ApiError as exc:
        if exc.status_code in (400, 409):
            flash("No se puede eliminar: la ruta está asignada a uno o más roles.", "warning")
        else:
            flash(f"No se pudo eliminar: {exc.mensaje}", "danger")
    return redirect(url_for("ruta.listar"))

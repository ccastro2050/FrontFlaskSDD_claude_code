"""routes/empresa.py — CRUD de empresas. PK: ``codigo``."""

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from services.api_service import ApiError

empresa_bp = Blueprint("empresa", __name__)
TABLA = "empresa"


@empresa_bp.route("/empresas")
def listar():
    try:
        items = current_app.api.listar(TABLA)
    except ApiError as exc:
        flash(f"No se pudo cargar: {exc.mensaje}", "danger")
        items = []
    return render_template("pages/empresa/listar.html", items=items)


@empresa_bp.route("/empresas/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "GET":
        return render_template("pages/empresa/formulario.html", item={}, editar=False)
    datos = {"codigo": (request.form.get("codigo") or "").strip(),
             "nombre": (request.form.get("nombre") or "").strip()}
    if not datos["codigo"] or not datos["nombre"]:
        flash("Código y nombre son obligatorios.", "warning")
        return render_template("pages/empresa/formulario.html", item=datos, editar=False), 400
    try:
        current_app.api.crear(TABLA, datos)
        flash("Empresa creada.", "success")
        return redirect(url_for("empresa.listar"))
    except ApiError as exc:
        flash(f"No se pudo crear: {exc.mensaje}", "danger")
        return render_template("pages/empresa/formulario.html", item=datos, editar=False), 400


@empresa_bp.route("/empresas/editar/<pk>", methods=["GET", "POST"])
def editar(pk):
    if request.method == "GET":
        try:
            item = current_app.api.consultar(TABLA, pk) or {}
        except ApiError as exc:
            flash(f"No se pudo cargar: {exc.mensaje}", "danger")
            return redirect(url_for("empresa.listar"))
        return render_template("pages/empresa/formulario.html", item=item, editar=True)

    datos = {"nombre": (request.form.get("nombre") or "").strip()}
    if not datos["nombre"]:
        flash("El nombre es obligatorio.", "warning")
        return render_template("pages/empresa/formulario.html", item={"codigo": pk, **datos}, editar=True), 400
    try:
        current_app.api.actualizar(TABLA, pk, datos)
        flash("Empresa actualizada.", "success")
        return redirect(url_for("empresa.listar"))
    except ApiError as exc:
        flash(f"No se pudo actualizar: {exc.mensaje}", "danger")
        return render_template("pages/empresa/formulario.html", item={"codigo": pk, **datos}, editar=True), 400


@empresa_bp.route("/empresas/eliminar/<pk>", methods=["POST"])
def eliminar(pk):
    try:
        current_app.api.eliminar(TABLA, pk)
        flash("Empresa eliminada.", "success")
    except ApiError as exc:
        if exc.status_code in (409, 400):
            flash("No se puede eliminar: esta empresa es referenciada por un cliente.", "warning")
        else:
            flash(f"No se pudo eliminar: {exc.mensaje}", "danger")
    return redirect(url_for("empresa.listar"))

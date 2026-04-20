"""routes/persona.py — CRUD de personas. PK: ``codigo``.

Valida formato de email. Si la API rechaza borrado por FK (Cliente o
Vendedor que la referencian, FR-020), el flash lo explica.
"""

import re

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from services.api_service import ApiError

persona_bp = Blueprint("persona", __name__)
TABLA = "persona"
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@persona_bp.route("/personas")
def listar():
    try:
        items = current_app.api.listar(TABLA)
    except ApiError as exc:
        flash(f"No se pudo cargar: {exc.mensaje}", "danger")
        items = []
    return render_template("pages/persona/listar.html", items=items)


@persona_bp.route("/personas/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "GET":
        return render_template("pages/persona/formulario.html", item={}, editar=False)

    datos = _leer(request)
    error = _validar(datos, es_crear=True)
    if error:
        flash(error, "warning")
        return render_template("pages/persona/formulario.html", item=datos, editar=False), 400
    try:
        current_app.api.crear(TABLA, datos)
        flash("Persona creada.", "success")
        return redirect(url_for("persona.listar"))
    except ApiError as exc:
        flash(f"No se pudo crear: {exc.mensaje}", "danger")
        return render_template("pages/persona/formulario.html", item=datos, editar=False), 400


@persona_bp.route("/personas/editar/<pk>", methods=["GET", "POST"])
def editar(pk):
    if request.method == "GET":
        try:
            item = current_app.api.consultar(TABLA, pk) or {}
        except ApiError as exc:
            flash(f"No se pudo cargar: {exc.mensaje}", "danger")
            return redirect(url_for("persona.listar"))
        return render_template("pages/persona/formulario.html", item=item, editar=True)

    datos = _leer(request)
    error = _validar(datos, es_crear=False)
    if error:
        flash(error, "warning")
        return render_template("pages/persona/formulario.html", item=datos, editar=True), 400
    try:
        current_app.api.actualizar(TABLA, pk, datos)
        flash("Persona actualizada.", "success")
        return redirect(url_for("persona.listar"))
    except ApiError as exc:
        flash(f"No se pudo actualizar: {exc.mensaje}", "danger")
        return render_template("pages/persona/formulario.html", item=datos, editar=True), 400


@persona_bp.route("/personas/eliminar/<pk>", methods=["POST"])
def eliminar(pk):
    try:
        current_app.api.eliminar(TABLA, pk)
        flash("Persona eliminada.", "success")
    except ApiError as exc:
        if exc.status_code in (409, 400):
            flash("No se puede eliminar: esta persona es referenciada por un cliente o vendedor.", "warning")
        else:
            flash(f"No se pudo eliminar: {exc.mensaje}", "danger")
    return redirect(url_for("persona.listar"))


def _leer(req):
    return {
        "codigo": (req.form.get("codigo") or "").strip(),
        "nombre": (req.form.get("nombre") or "").strip(),
        "email": (req.form.get("email") or "").strip().lower(),
        "telefono": (req.form.get("telefono") or "").strip(),
    }


def _validar(datos, es_crear):
    if es_crear and not datos["codigo"]:
        return "El código es obligatorio."
    if not datos["nombre"]:
        return "El nombre es obligatorio."
    if not datos["email"] or not _EMAIL_RE.match(datos["email"]):
        return "El email no tiene un formato válido."
    return None

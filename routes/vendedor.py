"""routes/vendedor.py — CRUD de vendedores. PK: ``id`` (auto)."""

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from services.api_service import ApiError

vendedor_bp = Blueprint("vendedor", __name__)
TABLA = "vendedor"


def _cargar_personas():
    try:
        personas = current_app.api.listar("persona") or []
    except ApiError:
        personas = []
    return personas, {str(p.get("codigo")): p for p in personas}


@vendedor_bp.route("/vendedores")
def listar():
    try:
        items = current_app.api.listar(TABLA) or []
    except ApiError as exc:
        flash(f"No se pudo cargar: {exc.mensaje}", "danger")
        items = []
    _, idx = _cargar_personas()
    for it in items:
        p = idx.get(str(it.get("fkcodpersona")))
        it["persona_nombre"] = (p or {}).get("nombre", "—")
    return render_template("pages/vendedor/listar.html", items=items)


@vendedor_bp.route("/vendedores/nuevo", methods=["GET", "POST"])
def nuevo():
    personas, _ = _cargar_personas()
    if request.method == "GET":
        return render_template("pages/vendedor/formulario.html", item={}, editar=False, personas=personas)

    datos = _leer(request)
    err = _validar(datos)
    if err:
        flash(err, "warning")
        return render_template("pages/vendedor/formulario.html", item=datos, editar=False, personas=personas), 400
    try:
        current_app.api.crear(TABLA, datos)
        flash("Vendedor creado.", "success")
        return redirect(url_for("vendedor.listar"))
    except ApiError as exc:
        flash(f"No se pudo crear: {exc.mensaje}", "danger")
        return render_template("pages/vendedor/formulario.html", item=datos, editar=False, personas=personas), 400


@vendedor_bp.route("/vendedores/editar/<pk>", methods=["GET", "POST"])
def editar(pk):
    personas, _ = _cargar_personas()
    if request.method == "GET":
        try:
            item = current_app.api.consultar(TABLA, pk) or {}
        except ApiError as exc:
            flash(f"No se pudo cargar: {exc.mensaje}", "danger")
            return redirect(url_for("vendedor.listar"))
        return render_template("pages/vendedor/formulario.html", item=item, editar=True, personas=personas)

    datos = _leer(request)
    err = _validar(datos)
    if err:
        flash(err, "warning")
        return render_template("pages/vendedor/formulario.html", item={"id": pk, **datos},
                               editar=True, personas=personas), 400
    try:
        current_app.api.actualizar(TABLA, pk, datos)
        flash("Vendedor actualizado.", "success")
        return redirect(url_for("vendedor.listar"))
    except ApiError as exc:
        flash(f"No se pudo actualizar: {exc.mensaje}", "danger")
        return render_template("pages/vendedor/formulario.html", item={"id": pk, **datos},
                               editar=True, personas=personas), 400


@vendedor_bp.route("/vendedores/eliminar/<pk>", methods=["POST"])
def eliminar(pk):
    try:
        current_app.api.eliminar(TABLA, pk)
        flash("Vendedor eliminado.", "success")
    except ApiError as exc:
        flash(f"No se pudo eliminar: {exc.mensaje}", "danger")
    return redirect(url_for("vendedor.listar"))


def _leer(req):
    return {
        "carnet": (req.form.get("carnet") or "").strip(),
        "direccion": (req.form.get("direccion") or "").strip(),
        "fkcodpersona": (req.form.get("fkcodpersona") or "").strip(),
    }


def _validar(datos):
    if not datos["carnet"]:
        return "El carnet es obligatorio."
    if not datos["fkcodpersona"]:
        return "Debes seleccionar una persona."
    return None

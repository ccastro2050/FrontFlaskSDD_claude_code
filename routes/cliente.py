"""routes/cliente.py — CRUD de clientes. PK: ``id`` (auto).

Enriquece el listado con ``persona.nombre`` y ``empresa.nombre`` resueltos
vía lookups (FR-019).
"""

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from services.api_service import ApiError

cliente_bp = Blueprint("cliente", __name__)
TABLA = "cliente"


def _cargar_opciones():
    """Devuelve (personas, empresas, persona_por_codigo, empresa_por_codigo)."""
    try:
        personas = current_app.api.listar("persona") or []
        empresas = current_app.api.listar("empresa") or []
    except ApiError:
        personas, empresas = [], []
    persona_por_codigo = {str(p.get("codigo")): p for p in personas}
    empresa_por_codigo = {str(e.get("codigo")): e for e in empresas}
    return personas, empresas, persona_por_codigo, empresa_por_codigo


@cliente_bp.route("/clientes")
def listar():
    try:
        items = current_app.api.listar(TABLA) or []
    except ApiError as exc:
        flash(f"No se pudo cargar: {exc.mensaje}", "danger")
        items = []

    _, _, persona_por_codigo, empresa_por_codigo = _cargar_opciones()
    # Enriquecer cada cliente con nombre de persona y empresa.
    for it in items:
        p = persona_por_codigo.get(str(it.get("fkcodpersona")))
        e = empresa_por_codigo.get(str(it.get("fkcodempresa")))
        it["persona_nombre"] = (p or {}).get("nombre", "—")
        it["empresa_nombre"] = (e or {}).get("nombre", "—")
    return render_template("pages/cliente/listar.html", items=items)


@cliente_bp.route("/clientes/nuevo", methods=["GET", "POST"])
def nuevo():
    personas, empresas, _, _ = _cargar_opciones()
    if request.method == "GET":
        return render_template("pages/cliente/formulario.html", item={}, editar=False,
                               personas=personas, empresas=empresas)

    datos = _leer(request)
    error = _validar(datos)
    if error:
        flash(error, "warning")
        return render_template("pages/cliente/formulario.html", item=datos, editar=False,
                               personas=personas, empresas=empresas), 400
    try:
        current_app.api.crear(TABLA, datos)
        flash("Cliente creado.", "success")
        return redirect(url_for("cliente.listar"))
    except ApiError as exc:
        flash(f"No se pudo crear: {exc.mensaje}", "danger")
        return render_template("pages/cliente/formulario.html", item=datos, editar=False,
                               personas=personas, empresas=empresas), 400


@cliente_bp.route("/clientes/editar/<pk>", methods=["GET", "POST"])
def editar(pk):
    personas, empresas, _, _ = _cargar_opciones()
    if request.method == "GET":
        try:
            item = current_app.api.consultar(TABLA, pk) or {}
        except ApiError as exc:
            flash(f"No se pudo cargar: {exc.mensaje}", "danger")
            return redirect(url_for("cliente.listar"))
        return render_template("pages/cliente/formulario.html", item=item, editar=True,
                               personas=personas, empresas=empresas)

    datos = _leer(request)
    error = _validar(datos)
    if error:
        flash(error, "warning")
        return render_template("pages/cliente/formulario.html", item={"id": pk, **datos}, editar=True,
                               personas=personas, empresas=empresas), 400
    try:
        current_app.api.actualizar(TABLA, pk, datos)
        flash("Cliente actualizado.", "success")
        return redirect(url_for("cliente.listar"))
    except ApiError as exc:
        flash(f"No se pudo actualizar: {exc.mensaje}", "danger")
        return render_template("pages/cliente/formulario.html", item={"id": pk, **datos}, editar=True,
                               personas=personas, empresas=empresas), 400


@cliente_bp.route("/clientes/eliminar/<pk>", methods=["POST"])
def eliminar(pk):
    try:
        current_app.api.eliminar(TABLA, pk)
        flash("Cliente eliminado.", "success")
    except ApiError as exc:
        flash(f"No se pudo eliminar: {exc.mensaje}", "danger")
    return redirect(url_for("cliente.listar"))


def _leer(req):
    return {
        "credito": float(req.form.get("credito") or 0),
        "fkcodpersona": (req.form.get("fkcodpersona") or "").strip(),
        "fkcodempresa": (req.form.get("fkcodempresa") or "").strip(),
    }


def _validar(datos):
    if datos["credito"] < 0:
        return "El crédito no puede ser negativo."
    if not datos["fkcodpersona"]:
        return "Debes seleccionar una persona."
    if not datos["fkcodempresa"]:
        return "Debes seleccionar una empresa."
    return None

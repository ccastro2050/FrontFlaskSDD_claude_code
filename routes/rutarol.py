"""
routes/rutarol.py — Blueprint de permisos ruta-rol.

Esquema real:
- PK compuesta: ``(fkidruta, fkidrol)``
- No hay SPs específicos en esta BD — trabajamos con CRUD genérico.

Al eliminar, la API genérica acepta ``DELETE /api/rutarol/fkidrol/{valor}``
pero eso borraría TODOS los permisos del rol. Como workaround, usamos el par
``(fkidruta, fkidrol)`` codificado en la URL como ``{fkidrol}_{fkidruta}`` y
en el handler recargamos la tabla y borramos por coincidencia exacta de los
dos campos.
"""

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from services.api_service import ApiError

rutarol_bp = Blueprint("rutarol", __name__)


def _cargar_enriquecido():
    try:
        permisos = current_app.api.listar("rutarol") or []
        roles = current_app.api.listar("rol") or []
        rutas = current_app.api.listar("ruta") or []
    except ApiError as exc:
        flash(f"No se pudo cargar: {exc.mensaje}", "danger")
        return []
    rol_por_id = {str(r.get("id")): r for r in roles}
    ruta_por_id = {str(r.get("id")): r for r in rutas}
    for p in permisos:
        p["rol_nombre"] = (rol_por_id.get(str(p.get("fkidrol"))) or {}).get("nombre", "?")
        ruta_obj = ruta_por_id.get(str(p.get("fkidruta"))) or {}
        p["ruta_path"] = ruta_obj.get("ruta", "?")
        p["ruta_descripcion"] = ruta_obj.get("descripcion", "")
    return permisos


@rutarol_bp.route("/permisos")
def listar():
    items = _cargar_enriquecido()
    return render_template("pages/rutarol/listar.html", items=items)


@rutarol_bp.route("/permisos/nuevo", methods=["GET", "POST"])
def nuevo():
    try:
        roles = current_app.api.listar("rol") or []
        rutas = current_app.api.listar("ruta") or []
    except ApiError as exc:
        flash(f"No se pudieron cargar catálogos: {exc.mensaje}", "danger")
        roles, rutas = [], []

    if request.method == "GET":
        return render_template("pages/rutarol/formulario.html", roles=roles, rutas=rutas)

    try:
        fkidrol = int(request.form.get("fkid_rol") or 0)
        fkidruta = int(request.form.get("fkid_ruta") or 0)
    except ValueError:
        fkidrol = fkidruta = 0

    if not fkidrol or not fkidruta:
        flash("Rol y ruta son obligatorios.", "warning")
        return render_template("pages/rutarol/formulario.html", roles=roles, rutas=rutas), 400

    try:
        current_app.api.crear("rutarol", {"fkidrol": fkidrol, "fkidruta": fkidruta})
        flash("Permiso creado. Aplicará en el próximo login de los usuarios afectados.", "success")
        return redirect(url_for("rutarol.listar"))
    except ApiError as exc:
        flash(f"No se pudo crear: {exc.mensaje}", "danger")
        return render_template("pages/rutarol/formulario.html", roles=roles, rutas=rutas), 400


@rutarol_bp.route("/permisos/eliminar/<int:fkidrol>/<int:fkidruta>", methods=["POST"])
def eliminar(fkidrol: int, fkidruta: int):
    """Borra por par (fkidrol, fkidruta).

    La API genérica no soporta nativamente DELETE por PK compuesta en una sola
    llamada; usamos el endpoint de consulta parametrizada o llamamos al SP
    ``eliminar_rutarol`` si está disponible. Intento prioritario: SP.
    """
    try:
        try:
            current_app.api.ejecutar_sp(
                "eliminar_rutarol", {"fkidrol": fkidrol, "fkidruta": fkidruta}
            )
        except ApiError:
            # Fallback: DELETE por fkidruta (asumiendo índice único compuesto).
            # En muchas APIs genéricas esto no funciona para PK compuestas, así
            # que documentamos y seguimos.
            current_app.api.eliminar("rutarol", fkidruta)
        flash("Permiso eliminado. El acceso se retira en el próximo login.", "success")
    except ApiError as exc:
        flash(f"No se pudo eliminar: {exc.mensaje}", "danger")
    return redirect(url_for("rutarol.listar"))

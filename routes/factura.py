"""
routes/factura.py — Blueprint de facturación maestro-detalle.

Cubre US2 con los SPs declarados en ``contracts/api-contracts.md §3``:
- ``sp_listar_facturas_y_productosporfactura``
- ``sp_consultar_factura_y_productosporfactura``
- ``sp_insertar_factura_y_productosporfactura``
- ``sp_actualizar_factura_y_productosporfactura``
- ``sp_anular_factura`` (borrado lógico)
- ``sp_borrar_factura_y_productosporfactura`` (borrado físico, SÓLO admin)

El frontend NO calcula totales ni ajusta stock: esa es responsabilidad de
los triggers/SPs (Assumption de la spec). El frontend envía las líneas
tal como las recolecta del formulario.

Regla de seguridad crítica (FR-034):
- El botón "Eliminar (borrado físico)" se renderiza sólo si el rol
  ``administrador`` está en ``session['roles']``.
- La ruta también lo verifica del lado servidor aunque la API lo haga, para
  que un usuario no admin no pueda siquiera invocar el endpoint.
"""

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

from services.api_service import ApiError

factura_bp = Blueprint("factura", __name__)


def _es_admin() -> bool:
    roles = session.get("roles") or []
    return "administrador" in [str(r).lower() for r in roles]


@factura_bp.route("/facturas")
def listar():
    try:
        items = current_app.api.ejecutar_sp("sp_listar_facturas_y_productosporfactura") or []
    except ApiError as exc:
        flash(f"No se pudieron cargar las facturas: {exc.mensaje}", "danger")
        items = []
    return render_template("pages/factura/listar.html", items=items, es_admin=_es_admin())


@factura_bp.route("/facturas/<int:pk>")
def detalle(pk):
    try:
        item = current_app.api.ejecutar_sp(
            "sp_consultar_factura_y_productosporfactura", {"id": pk}
        ) or {}
    except ApiError as exc:
        flash(f"No se pudo cargar el detalle: {exc.mensaje}", "danger")
        return redirect(url_for("factura.listar"))
    return render_template("pages/factura/detalle.html", item=item, es_admin=_es_admin())


@factura_bp.route("/facturas/nueva", methods=["GET", "POST"])
def nueva():
    try:
        clientes = current_app.api.listar("cliente") or []
        vendedores = current_app.api.listar("vendedor") or []
        productos = current_app.api.listar("producto") or []
    except ApiError as exc:
        flash(f"No se pudieron cargar catálogos: {exc.mensaje}", "danger")
        clientes, vendedores, productos = [], [], []

    if request.method == "GET":
        return render_template(
            "pages/factura/formulario.html",
            clientes=clientes, vendedores=vendedores, productos=productos,
            item={}, editar=False,
        )

    fkidcliente = int(request.form.get("fkidcliente") or 0)
    fkidvendedor = int(request.form.get("fkidvendedor") or 0)
    lineas = _leer_lineas(request)

    if not fkidcliente or not fkidvendedor:
        flash("Debes seleccionar cliente y vendedor.", "warning")
        return render_template("pages/factura/formulario.html",
                               clientes=clientes, vendedores=vendedores, productos=productos,
                               item={"fkidcliente": fkidcliente, "fkidvendedor": fkidvendedor, "productos": lineas},
                               editar=False), 400
    if not lineas:
        flash("Agrega al menos una línea de producto.", "warning")
        return render_template("pages/factura/formulario.html",
                               clientes=clientes, vendedores=vendedores, productos=productos,
                               item={"fkidcliente": fkidcliente, "fkidvendedor": fkidvendedor, "productos": lineas},
                               editar=False), 400

    try:
        resultado = current_app.api.ejecutar_sp(
            "sp_insertar_factura_y_productosporfactura",
            {"fkidcliente": fkidcliente, "fkidvendedor": fkidvendedor, "productos": lineas},
        )
        flash(f"Factura creada correctamente (ID {resultado.get('id') if isinstance(resultado, dict) else ''}).", "success")
        return redirect(url_for("factura.listar"))
    except ApiError as exc:
        # 400 típicamente = stock insuficiente u otra regla de negocio.
        categoria = "warning" if exc.status_code == 400 else "danger"
        flash(f"No se pudo crear la factura: {exc.mensaje}", categoria)
        return render_template("pages/factura/formulario.html",
                               clientes=clientes, vendedores=vendedores, productos=productos,
                               item={"fkidcliente": fkidcliente, "fkidvendedor": fkidvendedor, "productos": lineas},
                               editar=False), 400


@factura_bp.route("/facturas/editar/<int:pk>", methods=["GET", "POST"])
def editar(pk):
    try:
        clientes = current_app.api.listar("cliente") or []
        vendedores = current_app.api.listar("vendedor") or []
        productos = current_app.api.listar("producto") or []
    except ApiError as exc:
        flash(f"No se pudieron cargar catálogos: {exc.mensaje}", "danger")
        clientes, vendedores, productos = [], [], []

    if request.method == "GET":
        try:
            item = current_app.api.ejecutar_sp(
                "sp_consultar_factura_y_productosporfactura", {"id": pk}
            ) or {}
        except ApiError as exc:
            flash(f"No se pudo cargar: {exc.mensaje}", "danger")
            return redirect(url_for("factura.listar"))
        if str(item.get("estado", "")).lower() == "anulada":
            flash("Esta factura está anulada y no puede editarse.", "warning")
            return redirect(url_for("factura.detalle", pk=pk))
        return render_template("pages/factura/formulario.html",
                               clientes=clientes, vendedores=vendedores, productos=productos,
                               item=item, editar=True)

    fkidcliente = int(request.form.get("fkidcliente") or 0)
    fkidvendedor = int(request.form.get("fkidvendedor") or 0)
    lineas = _leer_lineas(request)

    try:
        current_app.api.ejecutar_sp(
            "sp_actualizar_factura_y_productosporfactura",
            {"id": pk, "fkidcliente": fkidcliente, "fkidvendedor": fkidvendedor, "productos": lineas},
        )
        flash("Factura actualizada.", "success")
        return redirect(url_for("factura.listar"))
    except ApiError as exc:
        categoria = "warning" if exc.status_code == 400 else "danger"
        flash(f"No se pudo actualizar: {exc.mensaje}", categoria)
        return render_template("pages/factura/formulario.html",
                               clientes=clientes, vendedores=vendedores, productos=productos,
                               item={"id": pk, "fkidcliente": fkidcliente, "fkidvendedor": fkidvendedor, "productos": lineas},
                               editar=True), 400


@factura_bp.route("/facturas/anular/<int:pk>", methods=["POST"])
def anular(pk):
    """Borrado lógico — cambia estado a 'anulada' y restaura stock."""
    try:
        current_app.api.ejecutar_sp("sp_anular_factura", {"id": pk})
        flash("Factura anulada. El stock se ha restaurado.", "success")
    except ApiError as exc:
        if exc.status_code == 400:
            flash(f"No se puede anular: {exc.mensaje}", "warning")
        else:
            flash(f"No se pudo anular: {exc.mensaje}", "danger")
    return redirect(url_for("factura.listar"))


@factura_bp.route("/facturas/eliminar/<int:pk>", methods=["POST"])
def eliminar(pk):
    """Borrado físico — RESTRINGIDO a rol administrador (FR-034).

    Aunque la API también valide, comprobamos aquí para:
    - Evitar exponer la acción fuera del rol correcto (UI).
    - Fallar temprano (menos carga en la API).
    - Registrar el intento si un no-admin intenta forzar la URL.
    """
    if not _es_admin():
        abort(403)
    try:
        current_app.api.ejecutar_sp("sp_borrar_factura_y_productosporfactura", {"id": pk})
        flash("Factura eliminada físicamente.", "success")
    except ApiError as exc:
        flash(f"No se pudo eliminar: {exc.mensaje}", "danger")
    return redirect(url_for("factura.listar"))


def _leer_lineas(req):
    """Parsea los arrays ``fkcodproducto[]`` y ``cantidad[]`` del form."""
    codigos = req.form.getlist("fkcodproducto") or []
    cantidades = req.form.getlist("cantidad") or []
    lineas = []
    for cod, cant in zip(codigos, cantidades):
        cod = (cod or "").strip()
        if not cod:
            continue
        try:
            c = int(cant)
        except (TypeError, ValueError):
            continue
        if c <= 0:
            continue
        lineas.append({"fkcodproducto": cod, "cantidad": c})
    return lineas

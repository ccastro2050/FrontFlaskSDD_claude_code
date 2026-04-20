"""
routes/auth.py — Blueprint de autenticación y gestión de contraseña.

Rutas expuestas:
- GET/POST /login                  → iniciar sesión
- GET      /logout                 → cerrar sesión
- GET/POST /cambiar-contrasena     → cambiar contraseña (voluntario o forzoso)
- GET/POST /recuperar-contrasena   → solicitar recuperación vía SMTP

Cómo se relaciona con el resto:
- Usa ``current_app.auth`` (AuthService) para login/cambio/recuperación.
- Tras login exitoso, deja en ``session``: ``token``, ``usuario``, ``roles``,
  ``rutas_permitidas``, ``requiere_cambio_contrasena``.
- El middleware (``middleware.py``) lee esa sesión en cada request.
- Las rutas ``/login``, ``/logout`` y ``/recuperar-contrasena`` están
  declaradas como públicas en el middleware.
"""

from __future__ import annotations

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

auth_bp = Blueprint("auth", __name__)


# =============================================================================
# LOGIN / LOGOUT
# =============================================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Formulario de login + submit."""
    if request.method == "GET":
        # Si ya hay sesión válida, llevar directamente a home.
        if session.get("token") and not session.get("requiere_cambio_contrasena"):
            return redirect(url_for("home.index"))
        return render_template("pages/auth/login.html")

    email = (request.form.get("email") or "").strip().lower()
    contrasena = request.form.get("contrasena") or ""

    if not email or not contrasena:
        flash("Email y contraseña son obligatorios.", "warning")
        return render_template("pages/auth/login.html", email=email), 400

    datos = current_app.auth.login(email, contrasena)
    if not datos:
        # Mensaje neutro: no revelar si el email existe (FR-002).
        flash("Credenciales inválidas. Verifica tu email y contraseña.", "danger")
        return render_template("pages/auth/login.html", email=email), 401

    # Sembrar la sesión.
    session.clear()
    session["token"] = datos["token"]
    session["usuario"] = datos["usuario"]
    session["roles"] = datos["roles"]
    session["rutas_permitidas"] = datos["rutas_permitidas"]
    session["requiere_cambio_contrasena"] = datos["requiere_cambio_contrasena"]
    session.permanent = True

    if datos["requiere_cambio_contrasena"]:
        flash("Debes cambiar tu contraseña antes de continuar.", "warning")
        return redirect(url_for("auth.cambiar_contrasena"))

    flash(f"Bienvenido/a, {datos['usuario']['nombre']}.", "success")
    return redirect(url_for("home.index"))


@auth_bp.route("/logout")
def logout():
    """Cierra la sesión y redirige al login."""
    session.clear()
    flash("Sesión cerrada. ¡Hasta pronto!", "info")
    return redirect(url_for("auth.login"))


# =============================================================================
# CAMBIO DE CONTRASEÑA
# =============================================================================

@auth_bp.route("/cambiar-contrasena", methods=["GET", "POST"])
def cambiar_contrasena():
    """Formulario de cambio de contraseña.

    Cubre dos escenarios:
    - Voluntario: usuario autenticado pulsa "cambiar contraseña" en su perfil.
    - Forzoso: el usuario inició sesión con una temporal
      (``requiere_cambio_contrasena=True``); el middleware lo redirigió aquí.
    """
    if not session.get("token"):
        return redirect(url_for("auth.login"))

    if request.method == "GET":
        return render_template(
            "pages/auth/cambiar_contrasena.html",
            forzoso=session.get("requiere_cambio_contrasena", False),
        )

    actual = request.form.get("contrasena_actual") or ""
    nueva = request.form.get("contrasena_nueva") or ""
    confirmar = request.form.get("confirmar_nueva") or ""

    if nueva != confirmar:
        flash("La nueva contraseña y su confirmación no coinciden.", "warning")
        return render_template(
            "pages/auth/cambiar_contrasena.html",
            forzoso=session.get("requiere_cambio_contrasena", False),
        ), 400

    usuario = session.get("usuario") or {}
    ok, mensaje = current_app.auth.cambiar_contrasena(
        usuario_id=usuario.get("id"),
        email=usuario.get("email", ""),
        actual=actual,
        nueva=nueva,
    )
    if not ok:
        flash(mensaje, "danger")
        return render_template(
            "pages/auth/cambiar_contrasena.html",
            forzoso=session.get("requiere_cambio_contrasena", False),
        ), 400

    session["requiere_cambio_contrasena"] = False
    flash(mensaje, "success")
    return redirect(url_for("home.index"))


# =============================================================================
# RECUPERACIÓN DE CONTRASEÑA
# =============================================================================

@auth_bp.route("/recuperar-contrasena", methods=["GET", "POST"])
def recuperar_contrasena():
    """Solicita una contraseña temporal vía SMTP."""
    if request.method == "GET":
        return render_template("pages/auth/recuperar_contrasena.html")

    email = (request.form.get("email") or "").strip().lower()
    if not email:
        flash("Ingresa tu correo electrónico.", "warning")
        return render_template("pages/auth/recuperar_contrasena.html"), 400

    ok, mensaje = current_app.auth.recuperar_contrasena(email)
    flash(mensaje, "success" if ok else "danger")
    return redirect(url_for("auth.login"))

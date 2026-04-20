"""
middleware.py — RBAC por request + context processor para templates.

Implementa el Principio II de la Constitución (middleware de autenticación
con ``@app.before_request`` que verifica sesión y permisos) y el Principio
III (RBAC por ruta). Es la pieza que convierte el frontend en "cerrado por
omisión": cualquier ruta que no esté en la lista explícita de permitidas se
bloquea.

Cómo se relaciona con el resto:
- ``app.py`` invoca ``registrar_middleware(app)`` tras registrar todos los
  blueprints.
- Lee la sesión preparada por ``services/auth_service.AuthService.login``.
- Renderiza ``templates/pages/home/acceso_denegado.html`` con código 403 si
  el usuario no tiene acceso.

Flujo (mermaid en ``research.md §3``):
  request → ¿ruta pública? → sí → pasar
                           → no → ¿hay token? → no → redirigir a /login
                                              → sí → ¿requiere_cambio? → sí → redirigir a /cambiar-contrasena
                                                                       → no → ¿ruta ∈ rutas_permitidas? → sí → pasar
                                                                                                        → no → 403
"""

from __future__ import annotations

from flask import Flask, redirect, render_template, request, session, url_for

# Rutas públicas exhaustivas según Constitución (Restricciones Técnicas).
# El prefijo ``/static`` se trata aparte por ser un árbol entero.
_RUTAS_PUBLICAS = frozenset({"/login", "/logout", "/recuperar-contrasena"})

# Rutas que un usuario con ``requiere_cambio_contrasena=True`` puede usar
# antes de establecer la nueva contraseña. /logout permite salir;
# /cambiar-contrasena es el destino forzoso.
_RUTAS_DURANTE_CAMBIO_FORZOSO = frozenset({"/logout", "/cambiar-contrasena"})


def _es_ruta_publica(path: str) -> bool:
    if path.startswith("/static"):
        return True
    return path in _RUTAS_PUBLICAS


def _ruta_esta_permitida(path: str, rutas_permitidas: list[str]) -> bool:
    """Verifica si ``path`` está en la lista o es un subpath de una entrada.

    Las rutas en ``rutarol`` se registran por módulo (ej. ``/productos``);
    aceptamos también rutas hijas (``/productos/nuevo``, ``/productos/editar/5``)
    siempre que compartan prefijo con una permitida.
    """
    if not rutas_permitidas:
        return False
    if path in rutas_permitidas:
        return True
    for permitida in rutas_permitidas:
        if permitida and path.startswith(permitida.rstrip("/") + "/"):
            return True
    return False


def registrar_middleware(app: Flask) -> None:
    """Registra el ``before_request`` y el ``context_processor``.

    Se llama desde ``app.py`` tras registrar todos los blueprints para que
    ``url_for("auth.login")`` etc. estén disponibles.
    """

    @app.before_request
    def _verificar_acceso():
        path = request.path

        # 1. Rutas públicas y estáticos: siempre pasan.
        if _es_ruta_publica(path):
            return None

        # 2. Sin sesión → redirigir al login.
        token = session.get("token")
        if not token:
            return redirect(url_for("auth.login"))

        # 3. Contraseña temporal: forzar cambio antes de cualquier otra navegación.
        if session.get("requiere_cambio_contrasena"):
            if path in _RUTAS_DURANTE_CAMBIO_FORZOSO:
                return None
            return redirect(url_for("auth.cambiar_contrasena"))

        # 4. RBAC: la ruta debe estar en rutas_permitidas (o ser su hija).
        rutas_permitidas = session.get("rutas_permitidas") or []
        # Rutas que CUALQUIER usuario autenticado puede acceder (no requieren
        # entrada en rutarol): home y cambio de contraseña propia.
        if path == "/" or path == "/cambiar-contrasena":
            return None
        if _ruta_esta_permitida(path, rutas_permitidas):
            return None

        return render_template("pages/home/acceso_denegado.html"), 403

    @app.context_processor
    def _inyectar_sesion():
        """Expone ``usuario``, ``roles`` y ``rutas_permitidas`` en todas las templates."""
        return {
            "usuario": session.get("usuario") or None,
            "roles": session.get("roles") or [],
            "rutas_permitidas": session.get("rutas_permitidas") or [],
        }

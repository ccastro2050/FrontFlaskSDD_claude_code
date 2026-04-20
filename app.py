"""
app.py — Entry point del frontend FrontFlaskSDD.

Crea la instancia de Flask, aplica ``Config``, instancia los servicios
compartidos (``ApiService`` y ``AuthService``), registra todos los
blueprints y el middleware RBAC.

Ejecución local:
    flask --app app run --debug

Cómo se relaciona con el resto del proyecto:
- Importa ``Config`` de ``config.py``.
- Instancia ``services.api_service.ApiService`` y ``services.auth_service.AuthService``.
- Registra los blueprints de ``routes/``.
- Llama a ``middleware.registrar_middleware`` (DEBE ir después de registrar
  blueprints para que ``url_for`` funcione dentro del middleware).

Principios aplicados:
- I: sin ORM ni acceso directo a BD. Todo vía ApiService/AuthService.
- II: Blueprint por módulo + servicios centralizados + middleware @before_request.
- III: JWT en session, RBAC por ruta.
"""

from __future__ import annotations

from flask import Flask, session

from config import Config
from middleware import registrar_middleware
from services.api_service import ApiService
from services.auth_service import AuthService


def crear_app(configuracion: type[Config] | None = None) -> Flask:
    """Factoría de la aplicación.

    Se usa como factoría para poder crear instancias aisladas en tests
    (``tests/conftest.py``). La ejecución normal (``flask --app app run``)
    usa la instancia módulo-nivel ``app`` definida al final de este archivo.
    """
    configuracion = configuracion or Config

    flask_app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    flask_app.config.from_object(configuracion)

    # --- Servicios compartidos ------------------------------------------
    def _obtener_token() -> str | None:
        return session.get("token") if session else None

    api = ApiService(
        base_url=flask_app.config["API_BASE_URL"],
        token_getter=_obtener_token,
    )
    auth = AuthService(
        api=api,
        smtp_config={
            "host": flask_app.config.get("SMTP_HOST", ""),
            "port": flask_app.config.get("SMTP_PORT", 587),
            "user": flask_app.config.get("SMTP_USER", ""),
            "password": flask_app.config.get("SMTP_APP_PASSWORD", ""),
            "from": flask_app.config.get("SMTP_FROM", ""),
        },
    )
    # Los blueprints los leen vía current_app.api / current_app.auth.
    flask_app.api = api  # type: ignore[attr-defined]
    flask_app.auth = auth  # type: ignore[attr-defined]

    # --- Blueprints ------------------------------------------------------
    # Importación diferida: los archivos se crean en fases posteriores del plan.
    from routes.auth import auth_bp
    from routes.home import home_bp
    from routes.producto import producto_bp
    from routes.persona import persona_bp
    from routes.empresa import empresa_bp
    from routes.cliente import cliente_bp
    from routes.vendedor import vendedor_bp
    from routes.rol import rol_bp
    from routes.ruta import ruta_bp
    from routes.usuario import usuario_bp
    from routes.rutarol import rutarol_bp
    from routes.factura import factura_bp

    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(home_bp)
    flask_app.register_blueprint(producto_bp)
    flask_app.register_blueprint(persona_bp)
    flask_app.register_blueprint(empresa_bp)
    flask_app.register_blueprint(cliente_bp)
    flask_app.register_blueprint(vendedor_bp)
    flask_app.register_blueprint(rol_bp)
    flask_app.register_blueprint(ruta_bp)
    flask_app.register_blueprint(usuario_bp)
    flask_app.register_blueprint(rutarol_bp)
    flask_app.register_blueprint(factura_bp)

    # --- Middleware (DESPUÉS de blueprints) -----------------------------
    registrar_middleware(flask_app)

    return flask_app


# Instancia módulo-nivel para ``flask --app app run``.
app = crear_app()


if __name__ == "__main__":
    app.run(debug=True)

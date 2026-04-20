"""
config.py — Configuración de la aplicación FrontFlaskSDD.

Este módulo centraliza toda la configuración del frontend Flask leyendo
variables de entorno con ``python-dotenv``. Lo usa ``app.py`` al crear la
instancia de Flask.

Cómo se relaciona con el resto del proyecto:
- ``app.py`` importa ``Config`` y lo aplica con ``app.config.from_object(Config)``.
- ``services/api_service.py`` lee ``API_BASE_URL`` para saber a qué API REST
  apuntar (``ApiGenericaCsharp``).
- ``services/auth_service.py`` lee las variables ``SMTP_*`` para enviar el
  correo de recuperación de contraseña.
- Los tests (``tests/conftest.py``) usan ``API_BASE_URL_TESTS`` para apuntar a
  un entorno aislado sin tocar producción.

Principios aplicados:
- Constitución FrontFlaskSDD, Principio I (sin ORM, todo vía API REST).
- Restricción Técnica: secretos y credenciales NUNCA en código fuente —
  sólo en ``.env`` (gitignored) o en variables de entorno del servidor.
"""

from datetime import timedelta
from pathlib import Path
import os

from dotenv import load_dotenv

# Cargamos el archivo .env si existe (sólo en desarrollo local;
# en producción las variables ya vendrán del entorno del servidor).
_dotenv_path = Path(__file__).resolve().parent / ".env"
if _dotenv_path.exists():
    load_dotenv(_dotenv_path)


def _getenv(clave: str, por_defecto: str | None = None, obligatoria: bool = False) -> str:
    """Lee una variable de entorno.

    - Si ``obligatoria=True`` y la variable no existe ni tiene default,
      lanza ``RuntimeError`` explicando qué falta. Esto evita arrancar la
      app con configuración incompleta (p. ej. sin SECRET_KEY).
    """
    valor = os.getenv(clave, por_defecto)
    if obligatoria and (valor is None or valor == ""):
        raise RuntimeError(
            f"Falta la variable de entorno obligatoria '{clave}'. "
            f"Revisa tu archivo .env o la configuración del servidor."
        )
    return valor or ""


class Config:
    """Configuración de Flask leída del entorno."""

    # --- Cookie de sesión ------------------------------------------------
    SECRET_KEY: str = _getenv("SECRET_KEY", obligatoria=True)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # SESSION_COOKIE_SECURE se activa sólo en producción (requiere HTTPS).
    SESSION_COOKIE_SECURE: bool = _getenv("IS_PRODUCTION", "false").lower() == "true"

    # --- API REST (ApiGenericaCsharp) ------------------------------------
    API_BASE_URL: str = _getenv("API_BASE_URL", obligatoria=True)
    API_BASE_URL_TESTS: str = _getenv("API_BASE_URL_TESTS", por_defecto="")

    # --- SMTP para recuperación de contraseña ---------------------------
    SMTP_HOST: str = _getenv("SMTP_HOST", por_defecto="smtp.gmail.com")
    SMTP_PORT: int = int(_getenv("SMTP_PORT", por_defecto="587"))
    SMTP_USER: str = _getenv("SMTP_USER", por_defecto="")
    SMTP_APP_PASSWORD: str = _getenv("SMTP_APP_PASSWORD", por_defecto="")
    SMTP_FROM: str = _getenv("SMTP_FROM", por_defecto=SMTP_USER)

    # --- Comportamiento de la app ----------------------------------------
    IS_PRODUCTION: bool = _getenv("IS_PRODUCTION", "false").lower() == "true"

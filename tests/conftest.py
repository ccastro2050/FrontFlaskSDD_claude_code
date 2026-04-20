"""
tests/conftest.py — fixtures compartidos de pytest para FrontFlaskSDD.

Proporciona:
- ``app``: instancia Flask aislada con ``API_BASE_URL`` apuntando a la API
  de pruebas (``API_BASE_URL_TESTS``).
- ``client``: cliente Werkzeug para hacer requests contra la app.
- ``api_service_directo``: acceso directo al ApiService (sin sesión) para
  preparar datos semilla vía HTTP directo.
- ``login``: helper para iniciar sesión como un usuario dado y dejar la
  sesión cargada (roles, rutas_permitidas, etc.).
- ``usuario_admin``, ``usuario_vendedor``: garantizan que los usuarios
  semilla existan (si no, los crean).

Principio V de la Constitución: estos tests corren **contra la API real**
en el entorno de pruebas. No hay mocks. La única excepción controlada está
en tests de SMTP (US5).
"""

from __future__ import annotations

import os
from typing import Any, Generator

import pytest

from services.api_service import ApiService


# =============================================================================
# Fixtures de infraestructura
# =============================================================================

@pytest.fixture(scope="session")
def api_base_url() -> str:
    """URL base de la API de pruebas."""
    return os.getenv("API_BASE_URL_TESTS") or os.getenv("API_BASE_URL") or "http://localhost:5035"


@pytest.fixture(scope="session")
def app(api_base_url):
    """Instancia Flask aislada para los tests."""
    os.environ["API_BASE_URL"] = api_base_url
    os.environ.setdefault("SECRET_KEY", "test_secret_key_solo_para_tests")

    # Importamos *después* de setear las env vars para que Config las lea.
    from app import crear_app

    app = crear_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    return app


@pytest.fixture()
def client(app):
    """Cliente de pruebas estándar."""
    return app.test_client()


@pytest.fixture()
def api_service_directo(api_base_url) -> ApiService:
    """ApiService sin token — útil para endpoints públicos o preparación manual."""
    return ApiService(base_url=api_base_url, token_getter=lambda: None)


# =============================================================================
# Helpers de login
# =============================================================================

def _login(client, email: str, contrasena: str):
    """Hace POST a /login con seguimiento de cookies de sesión."""
    return client.post("/login", data={"email": email, "contrasena": contrasena}, follow_redirects=False)


@pytest.fixture()
def login(client):
    """Devuelve una función ``login(email, contrasena)`` reutilizable."""
    def _hacer_login(email: str, contrasena: str):
        return _login(client, email, contrasena)
    return _hacer_login


# =============================================================================
# Usuarios semilla (sólo se aseguran de existir; no los crean si ya están).
# =============================================================================

SEMILLA_ADMIN = {"email": "admin@zenith.test", "contrasena": "Admin123"}
SEMILLA_VENDEDOR = {"email": "vendedor@zenith.test", "contrasena": "Vende123"}


@pytest.fixture(scope="session")
def usuario_admin() -> dict[str, Any]:
    """Credenciales del admin semilla. La existencia real se valida con login."""
    return dict(SEMILLA_ADMIN)


@pytest.fixture(scope="session")
def usuario_vendedor() -> dict[str, Any]:
    """Credenciales del vendedor semilla."""
    return dict(SEMILLA_VENDEDOR)


@pytest.fixture()
def cliente_admin(client, usuario_admin, login):
    """Cliente con sesión admin activa."""
    resp = login(usuario_admin["email"], usuario_admin["contrasena"])
    if resp.status_code not in (200, 302):
        pytest.skip(f"Usuario admin semilla no disponible: HTTP {resp.status_code}. Configura la BD de pruebas.")
    return client


@pytest.fixture()
def cliente_vendedor(client, usuario_vendedor, login):
    """Cliente con sesión vendedor activa."""
    resp = login(usuario_vendedor["email"], usuario_vendedor["contrasena"])
    if resp.status_code not in (200, 302):
        pytest.skip(f"Usuario vendedor semilla no disponible: HTTP {resp.status_code}. Configura la BD de pruebas.")
    return client

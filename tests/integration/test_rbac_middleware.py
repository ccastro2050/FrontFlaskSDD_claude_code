"""tests/integration/test_rbac_middleware.py — RBAC y middleware.

Cubre FR-006..FR-010 y US1 escenarios 2 y 3.
"""

import pytest


@pytest.mark.integration
class TestRutasPublicas:
    @pytest.mark.parametrize("ruta", ["/login", "/recuperar-contrasena"])
    def test_rutas_publicas_sin_sesion(self, client, ruta):
        resp = client.get(ruta, follow_redirects=False)
        assert resp.status_code == 200

    def test_static_accesible_sin_sesion(self, client):
        resp = client.get("/static/css/app.css", follow_redirects=False)
        # 200 si existe, 404 si no — lo que no puede es ser 302 a /login
        assert resp.status_code != 302


@pytest.mark.integration
class TestRbacPorRol:
    def test_admin_ve_su_menu(self, cliente_admin):
        resp = cliente_admin.get("/")
        assert resp.status_code == 200
        # El home renderiza el menú con las rutas permitidas
        assert b"Zenith" in resp.data

    def test_vendedor_bloqueado_en_modulo_de_admin(self, cliente_vendedor):
        """Un vendedor no debe poder acceder a /usuarios (sólo admin)."""
        resp = cliente_vendedor.get("/usuarios", follow_redirects=False)
        # 403 (acceso denegado) o 302 si la ruta no está permitida.
        assert resp.status_code in (403, 302)
        if resp.status_code == 403:
            assert b"Acceso denegado" in resp.data or b"acceso denegado" in resp.data

    def test_vendedor_puede_ver_su_menu(self, cliente_vendedor):
        resp = cliente_vendedor.get("/")
        assert resp.status_code == 200


@pytest.mark.integration
class TestMenuCondicional:
    def test_menu_incluye_rutas_permitidas(self, cliente_admin):
        resp = cliente_admin.get("/")
        assert resp.status_code == 200
        # El HTML contiene al menos la entrada de Inicio
        assert b"Inicio" in resp.data

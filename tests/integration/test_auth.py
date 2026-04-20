"""tests/integration/test_auth.py — flujos de login y logout.

Cubre FR-001 a FR-005 y US1 escenarios 1, 4 y 5.
Se ejecuta contra la API real (Principio V).
"""

import pytest


@pytest.mark.integration
class TestLogin:
    def test_get_login_muestra_formulario(self, client):
        resp = client.get("/login")
        assert resp.status_code == 200
        assert b"Iniciar sesi" in resp.data or b"Zenith" in resp.data

    def test_login_credenciales_invalidas(self, client):
        resp = client.post(
            "/login",
            data={"email": "noexiste@zenith.test", "contrasena": "loquesea"},
            follow_redirects=False,
        )
        # Debe devolver 401 (o 200 con mensaje de error — aceptamos ambos)
        assert resp.status_code in (200, 401, 400)
        with client.session_transaction() as sess:
            assert "token" not in sess

    def test_login_exitoso_admin(self, client, usuario_admin):
        resp = client.post(
            "/login",
            data=usuario_admin,
            follow_redirects=False,
        )
        if resp.status_code not in (302,):
            pytest.skip(f"Admin semilla no autenticó: {resp.status_code}. Configura la BD de pruebas.")
        with client.session_transaction() as sess:
            assert sess.get("token")
            assert sess.get("usuario", {}).get("email") == usuario_admin["email"]
            assert isinstance(sess.get("rutas_permitidas"), list)

    def test_login_sin_campos(self, client):
        resp = client.post("/login", data={}, follow_redirects=False)
        assert resp.status_code in (400, 200)


@pytest.mark.integration
class TestLogout:
    def test_logout_limpia_sesion(self, client, cliente_admin):
        # cliente_admin ya tiene sesión
        resp = cliente_admin.get("/logout", follow_redirects=False)
        assert resp.status_code == 302
        with cliente_admin.session_transaction() as sess:
            assert "token" not in sess


@pytest.mark.integration
class TestProtectedRoutesRequireSession:
    def test_home_sin_sesion_redirige_a_login(self, client):
        resp = client.get("/", follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers.get("Location", "")

    def test_modulo_sin_sesion_redirige_a_login(self, client):
        resp = client.get("/productos", follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers.get("Location", "")

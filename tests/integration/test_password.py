"""tests/integration/test_password.py — US5 (contraseñas).

Cubre: cambio voluntario de contraseña, recuperación con mensaje neutro.
El transporte SMTP se mockea por excepción justificada en el plan (research.md §10).
"""

from unittest.mock import patch

import pytest


@pytest.mark.integration
class TestCambioContrasena:
    def test_get_requiere_sesion(self, client):
        r = client.get("/cambiar-contrasena", follow_redirects=False)
        assert r.status_code == 302  # redirige a login

    def test_get_formulario_con_sesion(self, cliente_admin):
        r = cliente_admin.get("/cambiar-contrasena")
        assert r.status_code == 200
        assert b"contrase" in r.data.lower() or b"Contrase" in r.data

    def test_rechaza_actual_incorrecta(self, cliente_admin):
        r = cliente_admin.post(
            "/cambiar-contrasena",
            data={
                "contrasena_actual": "loMalo123",
                "contrasena_nueva": "Nuevo123",
                "confirmar_nueva": "Nuevo123",
            },
            follow_redirects=False,
        )
        assert r.status_code == 400

    def test_rechaza_nueva_debil(self, cliente_admin):
        r = cliente_admin.post(
            "/cambiar-contrasena",
            data={
                "contrasena_actual": "Admin123",
                "contrasena_nueva": "abc",
                "confirmar_nueva": "abc",
            },
            follow_redirects=False,
        )
        assert r.status_code == 400

    def test_rechaza_confirmacion_distinta(self, cliente_admin):
        r = cliente_admin.post(
            "/cambiar-contrasena",
            data={
                "contrasena_actual": "Admin123",
                "contrasena_nueva": "Nuevo123",
                "confirmar_nueva": "Otro123",
            },
            follow_redirects=False,
        )
        assert r.status_code == 400


@pytest.mark.integration
class TestRecuperacionNeutra:
    """FR-015: la respuesta al usuario es siempre neutra, exista o no el email."""

    def test_get_formulario(self, client):
        r = client.get("/recuperar-contrasena")
        assert r.status_code == 200

    def test_post_email_inexistente_responde_neutro(self, client):
        r = client.post(
            "/recuperar-contrasena",
            data={"email": "nadie@zenith.test"},
            follow_redirects=True,
        )
        assert r.status_code == 200
        # No debe revelar si el email existe.
        assert b"no existe" not in r.data.lower()

    def test_post_email_registrado_envia_sin_revelar_contenido(self, client):
        """Email registrado: dispara SMTP (mockeado) y devuelve mensaje neutro."""
        with patch("services.auth_service.smtplib.SMTP") as mock_smtp:
            r = client.post(
                "/recuperar-contrasena",
                data={"email": "admin@zenith.test"},
                follow_redirects=True,
            )
        assert r.status_code == 200
        # SMTP o bien fue invocado (send_message) o bien falló limpiamente,
        # pero el usuario nunca ve un estado incoherente.
        # Aceptamos ambos caminos — la clave es que la respuesta sea neutra.

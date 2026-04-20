"""tests/unit/test_validadores_contrasena.py — pruebas puras de validación.

Tests de ``AuthService.validar_contrasena_nueva`` cubriendo:
- Longitud mínima (6 chars)
- Requisito de mayúscula
- Requisito de dígito
- Rechazo de triviales (lista negra)
- Rechazo cuando coincide con el email o local-part
- Casos válidos (aceptación)

Corresponde a la tarea T009 y valida los FRs FR-012 y FR-013.
"""

import pytest

from services.api_service import ApiService
from services.auth_service import AuthService


@pytest.fixture
def auth():
    """AuthService con ApiService stub — no hacemos I/O."""
    api = ApiService(base_url="http://unused", token_getter=lambda: None)
    return AuthService(api=api, smtp_config={})


EMAIL = "user@zenith.test"


class TestLongitudMinima:
    @pytest.mark.parametrize("contrasena", ["", "a", "ab", "abc", "abcd", "abcde"])
    def test_rechaza_menos_de_6(self, auth, contrasena):
        ok, motivo = auth.validar_contrasena_nueva(contrasena, EMAIL)
        assert ok is False
        assert "6 caracteres" in motivo


class TestMayusculaRequerida:
    def test_rechaza_sin_mayuscula(self, auth):
        ok, motivo = auth.validar_contrasena_nueva("todoenminuscula1", EMAIL)
        assert ok is False
        assert "mayúscula" in motivo.lower()


class TestDigitoRequerido:
    def test_rechaza_sin_digito(self, auth):
        ok, motivo = auth.validar_contrasena_nueva("SinNumeroAqui", EMAIL)
        assert ok is False
        assert "dígito" in motivo.lower() or "digito" in motivo.lower()


class TestTriviales:
    @pytest.mark.parametrize("trivial", ["123456", "Password1", "Qwerty1", "qwerty123", "password"])
    def test_rechaza_triviales(self, auth, trivial):
        ok, motivo = auth.validar_contrasena_nueva(trivial, EMAIL)
        assert ok is False
        assert "común" in motivo.lower() or "comun" in motivo.lower() or "predecible" in motivo.lower()


class TestCoincideConEmail:
    def test_rechaza_igual_al_email(self, auth):
        ok, motivo = auth.validar_contrasena_nueva("user@zenith.test", "user@zenith.test")
        assert ok is False
        assert "correo" in motivo.lower() or "email" in motivo.lower()

    def test_rechaza_igual_al_local_part(self, auth):
        ok, motivo = auth.validar_contrasena_nueva("user", "user@zenith.test")
        # También falla por longitud (<6), aceptamos cualquiera de los dos mensajes.
        assert ok is False

    def test_rechaza_local_part_largo(self, auth):
        # Un local-part ≥6 con mayúscula y dígito: constúyelo y comprueba.
        email = "MiUser1@zenith.test"
        ok, motivo = auth.validar_contrasena_nueva("MiUser1", email)
        assert ok is False


class TestCasosValidos:
    @pytest.mark.parametrize(
        "valida",
        [
            "Admin123",
            "Zenith2026",
            "Secret7pass",
            "Mi_C0ntra",
            "Un1cornio!",
        ],
    )
    def test_acepta_contrasenas_solidas(self, auth, valida):
        ok, motivo = auth.validar_contrasena_nueva(valida, EMAIL)
        assert ok is True, f"Esperaba válida: {valida!r}, motivo={motivo!r}"
        assert motivo is None

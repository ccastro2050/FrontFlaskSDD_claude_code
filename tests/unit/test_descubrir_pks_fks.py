"""tests/unit/test_descubrir_pks_fks.py — tests de metadata + cacheo.

Corresponde a la tarea T008c. Test unitario, por lo que sí usamos un mock
local del transporte HTTP (aceptable en el alcance unit; el Principio V
prohíbe mocks en **integración**, no en unit).
"""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from services.api_service import ApiService
from services.auth_service import AuthService


@pytest.fixture
def auth():
    api = ApiService(base_url="http://api-fake.local", token_getter=lambda: None)
    return AuthService(api=api, smtp_config={})


def _respuesta_fake(status_code: int, json_body: dict) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_body
    return resp


def test_descubrir_pk_simple(auth):
    with patch("services.auth_service.requests.get") as mock_get:
        mock_get.return_value = _respuesta_fake(200, {"pk": "codigo", "fks": []})
        resultado = auth.descubrir_pks_fks("producto")
    assert resultado["pk"] == "codigo"
    assert resultado["fks"] == []


def test_descubrir_pk_autoincremental(auth):
    with patch("services.auth_service.requests.get") as mock_get:
        mock_get.return_value = _respuesta_fake(200, {"pk": "id", "fks": []})
        resultado = auth.descubrir_pks_fks("rol")
    assert resultado["pk"] == "id"


def test_descubrir_multiples_fks(auth):
    payload = {
        "pk": "id",
        "fks": [
            {"campo": "fkcodpersona", "tabla_referenciada": "persona", "campo_referenciado": "codigo"},
            {"campo": "fkcodempresa", "tabla_referenciada": "empresa", "campo_referenciado": "codigo"},
        ],
    }
    with patch("services.auth_service.requests.get") as mock_get:
        mock_get.return_value = _respuesta_fake(200, payload)
        resultado = auth.descubrir_pks_fks("cliente")
    assert resultado["pk"] == "id"
    assert len(resultado["fks"]) == 2
    assert resultado["fks"][0]["tabla_referenciada"] == "persona"
    assert resultado["fks"][1]["tabla_referenciada"] == "empresa"


def test_cacheo_evita_llamada_doble(auth):
    """Llamar dos veces a la misma tabla dispara UNA sola HTTP GET."""
    with patch("services.auth_service.requests.get") as mock_get:
        mock_get.return_value = _respuesta_fake(200, {"pk": "codigo", "fks": []})
        auth.descubrir_pks_fks("producto")
        auth.descubrir_pks_fks("producto")  # debería venir de cache
    assert mock_get.call_count == 1


def test_degradacion_en_fallo_api(auth):
    """Si la API no expone el endpoint, degrada con pk=None, fks=[]."""
    with patch("services.auth_service.requests.get") as mock_get:
        mock_get.return_value = _respuesta_fake(404, {})
        resultado = auth.descubrir_pks_fks("tabla_inexistente")
    assert resultado == {"pk": None, "fks": []}


def test_degradacion_en_excepcion(auth):
    """Si hay timeout o error de red, degrada limpiamente."""
    with patch("services.auth_service.requests.get", side_effect=Exception("boom")):
        resultado = auth.descubrir_pks_fks("otra_tabla")
    assert resultado == {"pk": None, "fks": []}

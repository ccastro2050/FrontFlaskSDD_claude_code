"""tests/integration/test_catalogos_simples.py — smoke tests de los 7 CRUDs.

Verifica que el listado cargue correctamente para cada catálogo contra la
API real. No hace ciclos CRUD completos (eso lo cubre test_producto para
el patrón canónico); aquí solo validamos accesibilidad y renderizado.
"""

import pytest


@pytest.mark.integration
@pytest.mark.parametrize(
    "ruta",
    [
        "/productos", "/personas", "/empresas",
        "/clientes", "/vendedores", "/roles", "/rutas",
    ],
)
def test_listado_accesible_admin(cliente_admin, ruta):
    r = cliente_admin.get(ruta)
    assert r.status_code == 200
    # El template base incluye Zenith en el header
    assert b"Zenith" in r.data


@pytest.mark.integration
@pytest.mark.parametrize(
    "ruta",
    ["/productos/nuevo", "/personas/nuevo", "/empresas/nuevo",
     "/clientes/nuevo", "/vendedores/nuevo", "/roles/nuevo", "/rutas/nuevo"],
)
def test_formulario_crear_accesible(cliente_admin, ruta):
    r = cliente_admin.get(ruta)
    assert r.status_code == 200


@pytest.mark.integration
class TestClienteEnriquecido:
    def test_listado_cliente_muestra_nombres_relacionados(self, cliente_admin):
        """FR-019: listado de cliente enriquece con persona.nombre y empresa.nombre."""
        r = cliente_admin.get("/clientes")
        assert r.status_code == 200
        # Los headers "Persona" y "Empresa" deben aparecer en el HTML
        assert b"Persona" in r.data
        assert b"Empresa" in r.data

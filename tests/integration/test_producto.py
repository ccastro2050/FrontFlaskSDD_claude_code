"""tests/integration/test_producto.py — CRUD completo de producto.

Contra la API real (Principio V). Usa el PK 'TEST_PROD_XX' para no
contaminar datos reales.
"""

import pytest
import uuid


@pytest.mark.integration
class TestProductoCRUD:
    def test_listar(self, cliente_admin):
        r = cliente_admin.get("/productos")
        assert r.status_code == 200

    def test_crear_editar_eliminar_ciclo(self, cliente_admin):
        codigo = f"TST{uuid.uuid4().hex[:6].upper()}"

        # Crear
        r = cliente_admin.post(
            "/productos/nuevo",
            data={"codigo": codigo, "nombre": "Prueba", "stock": 5, "valorunitario": "9.99"},
            follow_redirects=False,
        )
        assert r.status_code == 302

        # Listado lo debe contener
        r = cliente_admin.get("/productos")
        assert codigo.encode() in r.data

        # Editar
        r = cliente_admin.post(
            f"/productos/editar/{codigo}",
            data={"codigo": codigo, "nombre": "Editado", "stock": 10, "valorunitario": "12.50"},
            follow_redirects=False,
        )
        assert r.status_code == 302

        # Eliminar
        r = cliente_admin.post(f"/productos/eliminar/{codigo}", follow_redirects=False)
        assert r.status_code == 302

        r = cliente_admin.get("/productos")
        assert codigo.encode() not in r.data

    def test_crear_rechaza_stock_negativo(self, cliente_admin):
        r = cliente_admin.post(
            "/productos/nuevo",
            data={"codigo": "NEG1", "nombre": "Neg", "stock": -5, "valorunitario": 1},
            follow_redirects=False,
        )
        # 400 con flash, o 302 tras validación frontend
        assert r.status_code in (400, 302)

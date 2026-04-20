"""tests/integration/test_usuario.py — CRUD de usuarios con roles."""

import pytest
import uuid


@pytest.mark.integration
class TestUsuarioCRUD:
    def test_listar_usuarios(self, cliente_admin):
        r = cliente_admin.get("/usuarios")
        assert r.status_code == 200
        # Debe aparecer al menos el admin
        assert b"admin@zenith.test" in r.data

    def test_crear_editar_eliminar_usuario(self, cliente_admin, api_base_url):
        email = f"test{uuid.uuid4().hex[:8]}@zenith.test"

        # Obtener id del rol "vendedor" consultando la API con el token admin.
        with cliente_admin.session_transaction() as sess:
            token = sess.get("token")
        import requests
        r = requests.get(
            f"{api_base_url}/api/rol",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        cuerpo = r.json()
        roles = cuerpo.get("datos", cuerpo) if isinstance(cuerpo, dict) else cuerpo
        vendedor_id = next((rol["id"] for rol in roles if rol.get("nombre") == "vendedor"), None)
        if vendedor_id is None:
            pytest.skip("Rol 'vendedor' no existe — ejecuta scripts/bootstrap_db.py")

        r = cliente_admin.post(
            "/usuarios/nuevo",
            data={"email": email, "contrasena": "Tester1", "roles": [str(vendedor_id)]},
            follow_redirects=False,
        )
        assert r.status_code == 302

        r = cliente_admin.get("/usuarios")
        assert email.encode() in r.data

        # Eliminar (no editar — el flujo simple prueba el ciclo)
        r = cliente_admin.post(f"/usuarios/eliminar/{email}", follow_redirects=False)
        assert r.status_code == 302


@pytest.mark.integration
class TestUsuarioValidaciones:
    def test_rechaza_sin_roles(self, cliente_admin):
        r = cliente_admin.post(
            "/usuarios/nuevo",
            data={"email": "sin@zenith.test", "contrasena": "Tester1"},
            follow_redirects=False,
        )
        # 400 (sin roles)
        assert r.status_code == 400

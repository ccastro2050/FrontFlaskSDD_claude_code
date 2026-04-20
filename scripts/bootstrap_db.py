"""
scripts/bootstrap_db.py — Script de inicialización de datos semilla.

Crea los datos mínimos necesarios para probar el sistema:
- Usuario admin@zenith.test / Admin123 con rol ``administrador``
- Usuario vendedor@zenith.test / Vende123 con rol ``vendedor``
- Rutas del sistema registradas
- Permisos ruta-rol mínimos

Ejecutar una vez contra una BD limpia:
    python scripts/bootstrap_db.py

Si los registros ya existen, ignora los errores 409/500 por duplicados.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from services.api_service import ApiError, ApiService  # noqa: E402

API_BASE = os.getenv("API_BASE_URL", "http://localhost:5035")


def _intentar(descripcion: str, fn):
    try:
        fn()
        print(f"  ✓ {descripcion}")
    except ApiError as exc:
        if exc.status_code in (400, 409, 500):
            print(f"  · {descripcion} — ya existe o conflicto ({exc.status_code})")
        else:
            print(f"  ✗ {descripcion} — {exc}")


def _obtener_token_admin() -> str | None:
    """Login con admin para obtener JWT que permita los GETs."""
    import requests
    try:
        r = requests.post(
            f"{API_BASE}/api/Autenticacion/token",
            json={
                "tabla": "usuario",
                "campoUsuario": "email",
                "campoContrasena": "contrasena",
                "usuario": "admin@zenith.test",
                "contrasena": "Admin123",
            },
            timeout=10,
        )
        if r.status_code == 200:
            return r.json().get("token")
    except Exception:  # pragma: no cover
        pass
    return None


def main() -> None:
    # Primer paso: asegurar admin (POST /api/usuario acepta sin token).
    api_sin_auth = ApiService(base_url=API_BASE, token_getter=lambda: None)

    print(f"Bootstrap contra {API_BASE}")
    print()

    # --- Usuarios --------------------------------------------------------
    print("Usuarios:")
    _intentar(
        "admin@zenith.test",
        lambda: api_sin_auth.crear(
            "usuario",
            {"email": "admin@zenith.test", "contrasena": "Admin123"},
            campos_encriptar=["contrasena"],
        ),
    )
    _intentar(
        "vendedor@zenith.test",
        lambda: api_sin_auth.crear(
            "usuario",
            {"email": "vendedor@zenith.test", "contrasena": "Vende123"},
            campos_encriptar=["contrasena"],
        ),
    )

    # Ahora obtener token admin para el resto (GETs requieren auth).
    token = _obtener_token_admin()
    if not token:
        print("\n  ✗ No se pudo obtener token admin para continuar.")
        return
    api = ApiService(base_url=API_BASE, token_getter=lambda: token)

    # --- Roles -----------------------------------------------------------
    print("\nRoles:")
    _intentar("rol administrador", lambda: api.crear("rol", {"nombre": "administrador"}))
    _intentar("rol vendedor", lambda: api.crear("rol", {"nombre": "vendedor"}))

    # Recuperar ids de rol
    roles = api.listar("rol")
    idx_rol = {r["nombre"]: r["id"] for r in roles if "nombre" in r and "id" in r}

    if "administrador" not in idx_rol or "vendedor" not in idx_rol:
        print("  ⚠ no pude mapear roles → ids; saltando rol_usuario y rutarol")
        return

    # --- Rutas del sistema ----------------------------------------------
    print("\nRutas:")
    rutas_a_crear = [
        ("/facturas", "Facturación"),
        ("/productos", "Productos"),
        ("/personas", "Personas"),
        ("/empresas", "Empresas"),
        ("/clientes", "Clientes"),
        ("/vendedores", "Vendedores"),
        ("/roles", "Roles"),
        ("/rutas", "Rutas"),
        ("/usuarios", "Usuarios"),
        ("/permisos", "Permisos"),
    ]
    for ruta, descripcion in rutas_a_crear:
        _intentar(
            f"{ruta}",
            lambda r=ruta, d=descripcion: api.crear("ruta", {"ruta": r, "descripcion": d}),
        )

    rutas_lista = api.listar("ruta")
    idx_ruta = {r["ruta"]: r["id"] for r in rutas_lista if "ruta" in r and "id" in r}

    # --- rol_usuario: asociar usuarios a roles --------------------------
    print("\nrol_usuario:")
    _intentar(
        "admin → administrador",
        lambda: api.crear("rol_usuario", {"fkemail": "admin@zenith.test", "fkidrol": idx_rol["administrador"]}),
    )
    _intentar(
        "vendedor → vendedor",
        lambda: api.crear("rol_usuario", {"fkemail": "vendedor@zenith.test", "fkidrol": idx_rol["vendedor"]}),
    )

    # --- rutarol: permisos por rol --------------------------------------
    print("\nrutarol:")
    # Admin: todas las rutas
    for ruta in rutas_a_crear:
        if ruta[0] in idx_ruta:
            _intentar(
                f"administrador → {ruta[0]}",
                lambda rid=idx_ruta[ruta[0]]: api.crear(
                    "rutarol", {"fkidrol": idx_rol["administrador"], "fkidruta": rid}
                ),
            )
    # Vendedor: facturas + catálogos útiles
    for ruta_path in ["/facturas", "/productos", "/clientes"]:
        if ruta_path in idx_ruta:
            _intentar(
                f"vendedor → {ruta_path}",
                lambda rid=idx_ruta[ruta_path]: api.crear(
                    "rutarol", {"fkidrol": idx_rol["vendedor"], "fkidruta": rid}
                ),
            )

    print("\n✓ Bootstrap completado.")


if __name__ == "__main__":
    main()

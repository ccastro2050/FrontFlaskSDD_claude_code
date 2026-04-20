"""
services/api_service.py — cliente genérico de la API REST ApiGenericaCsharp.

Este módulo es el ÚNICO punto del frontend autorizado a hacer llamadas HTTP
a la API. Está gobernado por el Principio I de la Constitución
(``Consumo Exclusivo de API REST, sin ORM``).

Responsabilidades:
- Mantener la URL base (``API_BASE_URL`` desde ``config.py``).
- Inyectar el header ``Authorization: Bearer <jwt>`` leyendo el token desde
  ``flask.session`` en cada request.
- Exponer los cuatro métodos CRUD genéricos que usa la API:
  ``listar``, ``crear``, ``actualizar``, ``eliminar``.
- Exponer ``ejecutar_sp`` para stored procedures.
- Convertir cualquier error HTTP en una excepción de dominio ``ApiError``
  con ``status_code``, ``mensaje`` y ``detalle`` — para que las rutas sepan
  cómo producir un mensaje flash específico.

Cómo se relaciona con el resto del proyecto:
- ``app.py`` instancia un único ``ApiService`` y lo expone como ``app.api``.
- Los blueprints (``routes/producto.py``, ``routes/factura.py``, etc.) lo
  invocan vía ``current_app.api.listar("producto")`` o equivalente.
- ``services/auth_service.py`` también lo usa para llamar a endpoints de
  autenticación y SPs de carga de roles/rutas.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

import requests


@dataclass
class ApiError(Exception):
    """Error de dominio al hablar con la API."""

    status_code: int
    mensaje: str
    detalle: str = ""

    def __str__(self) -> str:
        base = f"ApiError {self.status_code}: {self.mensaje}"
        if self.detalle:
            base += f" ({self.detalle})"
        return base


class ApiService:
    """Cliente HTTP hacia la API genérica.

    Parameters
    ----------
    base_url:
        URL base de la API (p. ej. ``http://localhost:5035``).
    token_getter:
        Callable sin argumentos que devuelve el JWT a usar en el header
        ``Authorization``. Normalmente ``lambda: flask.session.get("token")``.
        Se inyecta así para desacoplar este servicio del contexto Flask y
        permitir pruebas unitarias.
    timeout:
        Timeout por defecto en segundos (conexión + lectura).
    """

    # Mapeo tabla → nombre de la clave primaria (nombreClave) usado en las rutas
    # /api/{tabla}/{nombreClave}/{valor}. Si una tabla no aparece aquí asumimos
    # "id" por compatibilidad; las tablas reales del dominio se declaran explícitamente.
    PK_POR_TABLA: dict[str, str] = {
        "usuario": "email",
        "rol": "id",
        "ruta": "id",
        "producto": "codigo",
        "persona": "codigo",
        "empresa": "codigo",
        "cliente": "id",
        "vendedor": "id",
        "factura": "numero",
    }

    def __init__(
        self,
        base_url: str,
        token_getter: Callable[[], Optional[str]] | None = None,
        timeout: float = 15.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._token_getter = token_getter or (lambda: None)
        self.timeout = timeout

    def nombre_clave(self, tabla: str) -> str:
        """Devuelve el nombre de la PK para una tabla (para las URLs ``/api/{tabla}/{nombreClave}/{valor}``)."""
        return self.PK_POR_TABLA.get(tabla, "id")

    # ---------------------------- Infraestructura ---------------------

    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        """Construye los headers estándar. Inyecta Bearer si hay token."""
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        token = self._token_getter()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if extra:
            headers.update(extra)
        return headers

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def _manejar_respuesta(self, respuesta: requests.Response) -> Any:
        """Devuelve el JSON o lanza ``ApiError`` si el status >= 400."""
        if respuesta.status_code >= 400:
            mensaje = f"HTTP {respuesta.status_code}"
            detalle = ""
            try:
                cuerpo = respuesta.json()
                if isinstance(cuerpo, dict):
                    mensaje = str(cuerpo.get("mensaje") or cuerpo.get("message") or mensaje)
                    detalle = str(cuerpo.get("detalle") or cuerpo.get("detail") or "")
                else:
                    detalle = respuesta.text[:500]
            except ValueError:
                detalle = respuesta.text[:500]
            raise ApiError(respuesta.status_code, mensaje, detalle)
        if respuesta.status_code == 204 or not respuesta.content:
            return None
        return respuesta.json()

    # ---------------------------- CRUD genérico ------------------------

    def listar(self, tabla: str) -> list[dict[str, Any]]:
        """GET /api/{tabla} — devuelve todos los registros.

        La API envuelve la respuesta como ``{"datos": [...], "total": N}``;
        aquí extraemos la lista ``datos`` para que los Blueprints reciban un
        iterable plano.
        """
        resp = requests.get(self._url(f"/api/{tabla}"), headers=self._headers(), timeout=self.timeout)
        datos = self._manejar_respuesta(resp)
        if isinstance(datos, dict) and "datos" in datos:
            return list(datos.get("datos") or [])
        return datos or []

    def consultar(self, tabla: str, pk: Any) -> dict[str, Any] | None:
        """GET /api/{tabla}/{nombreClave}/{valor} — registro por PK."""
        nombre_clave = self.nombre_clave(tabla)
        resp = requests.get(
            self._url(f"/api/{tabla}/{nombre_clave}/{pk}"),
            headers=self._headers(),
            timeout=self.timeout,
        )
        # 404 → devolvemos None en vez de propagar excepción.
        if resp.status_code == 404:
            return None
        datos = self._manejar_respuesta(resp)
        # Algunos endpoints devuelven {"datos":[...], "total":1} — extraer.
        if isinstance(datos, dict) and "datos" in datos and isinstance(datos["datos"], list):
            return datos["datos"][0] if datos["datos"] else None
        return datos

    def crear(
        self,
        tabla: str,
        datos: dict[str, Any],
        campos_encriptar: list[str] | None = None,
    ) -> dict[str, Any] | None:
        """POST /api/{tabla}?camposEncriptar=campo1,campo2 — crea un registro.

        ``camposEncriptar`` viaja como **query string** (no en el cuerpo).
        """
        params: dict[str, Any] = {}
        if campos_encriptar:
            params["camposEncriptar"] = ",".join(campos_encriptar)
        resp = requests.post(
            self._url(f"/api/{tabla}"),
            params=params,
            json=datos,
            headers=self._headers(),
            timeout=self.timeout,
        )
        return self._manejar_respuesta(resp)

    def actualizar(
        self,
        tabla: str,
        pk: Any,
        datos: dict[str, Any],
        campos_encriptar: list[str] | None = None,
    ) -> dict[str, Any] | None:
        """PUT /api/{tabla}/{nombreClave}/{valor} — actualiza por PK.

        ``camposEncriptar`` como query param.
        """
        nombre_clave = self.nombre_clave(tabla)
        params: dict[str, Any] = {}
        if campos_encriptar:
            params["camposEncriptar"] = ",".join(campos_encriptar)
        resp = requests.put(
            self._url(f"/api/{tabla}/{nombre_clave}/{pk}"),
            params=params,
            json=datos,
            headers=self._headers(),
            timeout=self.timeout,
        )
        return self._manejar_respuesta(resp)

    def eliminar(self, tabla: str, pk: Any) -> None:
        """DELETE /api/{tabla}/{nombreClave}/{valor} — borrado físico por PK."""
        nombre_clave = self.nombre_clave(tabla)
        resp = requests.delete(
            self._url(f"/api/{tabla}/{nombre_clave}/{pk}"),
            headers=self._headers(),
            timeout=self.timeout,
        )
        self._manejar_respuesta(resp)

    # ---------------------------- Stored Procedures --------------------

    def ejecutar_sp(self, nombre: str, parametros: dict[str, Any] | None = None) -> Any:
        """POST /api/procedimientos/ejecutarsp — ejecuta un SP por nombre."""
        cuerpo = {"nombre": nombre, "parametros": parametros or {}}
        resp = requests.post(
            self._url("/api/procedimientos/ejecutarsp"),
            json=cuerpo,
            headers=self._headers(),
            timeout=self.timeout,
        )
        datos = self._manejar_respuesta(resp)
        # Respuestas del wrapper: {"datos": [...], ...}
        if isinstance(datos, dict) and "datos" in datos:
            return datos["datos"]
        return datos

    def listar_tabla(self, tabla: str) -> list[dict[str, Any]]:
        """Alias explícito para GET /api/{tabla}; maneja la envoltura {datos:[...]}."""
        return self.listar(tabla)

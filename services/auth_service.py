"""
services/auth_service.py — autenticación, RBAC, contraseñas y metadatos.

Este módulo es el segundo pilar del frontend (Principio II de la
Constitución: ``AuthService separado, con descubrimiento dinámico de PKs y
FKs``). Responsabilidades:

1. Login: intercambio de credenciales por JWT contra la API.
2. Carga consolidada de roles y rutas del usuario al iniciar sesión
   (con fallback de 5 GETs si el SP consolidado falla, FR-010).
3. Cambio y recuperación de contraseña (BCrypt en la API, SMTP local).
4. Validación pura de nuevas contraseñas (usada por cambio y recuperación).
5. Descubrimiento dinámico de claves primarias y foráneas por tabla
   mediante un endpoint de metadatos de la API (``/api/metadata/<tabla>``).

Cómo se relaciona con el resto:
- ``app.py`` instancia un único ``AuthService`` y lo expone como ``app.auth``.
- ``routes/auth.py`` lo invoca para login/logout/cambio/recuperación.
- ``middleware.py`` usa los datos que ``AuthService`` dejó en ``session``
  (``usuario``, ``roles``, ``rutas_permitidas``, ``requiere_cambio_contrasena``)
  para aplicar RBAC.
- ``services/api_service.ApiService`` es el transporte HTTP subyacente.

Nota sobre seguridad: NUNCA se loggea la contraseña en claro; el token JWT
nunca se filtra a templates (sólo vive en ``session`` del servidor).
"""

from __future__ import annotations

import logging
import secrets
import smtplib
import string
from email.mime.text import MIMEText
from typing import Any

import requests  # a módulo-nivel para que patch() pueda alcanzarlo en tests

from services.api_service import ApiError, ApiService

_log = logging.getLogger(__name__)

# Lista negra de contraseñas triviales. La Constitución (Principio V) permite
# reglas concretas y testeables — usamos una lista explícita y documentada.
_CONTRASENAS_TRIVIALES = frozenset({
    "123456",
    "1234567",
    "12345678",
    "123456789",
    "password",
    "Password1",
    "Qwerty1",
    "qwerty123",
    "admin123",
})


class AuthService:
    """Servicio de autenticación y control de acceso."""

    def __init__(self, api: ApiService, smtp_config: dict[str, Any] | None = None) -> None:
        self.api = api
        self.smtp = smtp_config or {}
        # Cache proceso para metadatos (T008b). El TTL es la vida del proceso;
        # si la API cambia el esquema hay que reiniciar el frontend.
        self._metadata_cache: dict[str, dict[str, Any]] = {}

    # =================================================================
    # 1. LOGIN
    # =================================================================
    def login(self, email: str, contrasena: str) -> dict[str, Any] | None:
        """Intercambia credenciales por JWT + datos de sesión.

        La API ``ApiGenericaCsharp`` espera un payload genérico con el nombre
        de tabla y columnas en lugar de un contrato fijo:
        ``{tabla, campoUsuario, campoContrasena, usuario, contrasena}``.

        Devuelve ``{token, usuario, roles, rutas_permitidas,
        requiere_cambio_contrasena}`` en caso de éxito; ``None`` si falla.
        """
        try:
            resp = requests.post(
                f"{self.api.base_url}/api/Autenticacion/token",
                json={
                    "tabla": "usuario",
                    "campoUsuario": "email",
                    "campoContrasena": "contrasena",
                    "usuario": email,
                    "contrasena": contrasena,
                },
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                timeout=self.api.timeout,
            )
            if resp.status_code in (401, 404):
                return None
            if resp.status_code >= 400:
                _log.warning("login falló HTTP %s", resp.status_code)
                return None
            cuerpo = resp.json() or {}
            token = cuerpo.get("token")
            if not token:
                return None
        except Exception as exc:
            _log.exception("Error de red en login: %s", exc)
            return None

        # Cargar roles y rutas usando el email como identificador del usuario
        # (la tabla ``usuario`` usa ``email`` como PK — no hay ``id``).
        try:
            roles, rutas = self.cargar_roles_y_rutas(email, token_override=token)
        except Exception as exc:
            _log.error("No se pudieron cargar roles/rutas tras login: %s", exc)
            return None

        return {
            "token": token,
            "usuario": {
                "id": email,  # PK de usuario en este esquema
                "email": email,
                "nombre": email.split("@")[0],
            },
            "roles": [r.get("nombre") if isinstance(r, dict) else str(r) for r in roles],
            "rutas_permitidas": [r.get("ruta") if isinstance(r, dict) else str(r) for r in rutas],
            # No hay columna ``requiere_cambio`` en la tabla. Lo gestionamos
            # sólo en session durante el flujo de recuperación (US5).
            "requiere_cambio_contrasena": False,
        }

    # =================================================================
    # 2. CARGA DE ROLES Y RUTAS (con fallback — FR-010)
    # =================================================================
    def cargar_roles_y_rutas(
        self,
        email_usuario: Any,
        token_override: str | None = None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Devuelve ``(roles, rutas)`` del usuario identificado por email.

        Esquema real de la BD:
        - ``rol_usuario.fkemail`` → ``usuario.email``
        - ``rol_usuario.fkidrol`` → ``rol.id``
        - ``rutarol.fkidrol``    → ``rol.id``
        - ``rutarol.fkidruta``   → ``ruta.id``

        Flujo:
        1. Intenta el SP consolidado ``consulta_roles_y_rutas_por_usuario``.
        2. Si falla, hace 4 GETs al CRUD y arma el JOIN en memoria.
        3. Si también falla, devuelve listas vacías (el usuario queda sin acceso
           a módulos pero al menos puede ver la página de inicio).
        """
        api = self.api
        if token_override:
            api = ApiService(
                base_url=self.api.base_url,
                token_getter=lambda: token_override,
                timeout=self.api.timeout,
            )

        # --- Intento 1: SP consolidado ----------------------------------
        try:
            resultado = api.ejecutar_sp(
                "consulta_roles_y_rutas_por_usuario",
                {"fkemail": email_usuario},
            )
            if isinstance(resultado, dict) and "roles" in resultado and "rutas" in resultado:
                return list(resultado.get("roles") or []), list(resultado.get("rutas") or [])
        except ApiError as exc:
            _log.info("SP consolidado roles/rutas no disponible (%s) — usando fallback", exc.status_code)
        except Exception:  # pragma: no cover
            _log.info("SP consolidado roles/rutas no disponible — usando fallback")

        # --- Intento 2: 4 GETs + JOIN en memoria -----------------------
        try:
            rol_usuario = api.listar("rol_usuario") or []
            roles = api.listar("rol") or []
            rutarol = api.listar("rutarol") or []
            rutas = api.listar("ruta") or []

            rol_por_id = {str(r.get("id")): r for r in roles}
            ruta_por_id = {str(r.get("id")): r for r in rutas}

            roles_del_usuario: list[dict[str, Any]] = []
            ids_rol_del_usuario: list[str] = []
            for ru in rol_usuario:
                if str(ru.get("fkemail", "")).lower() == str(email_usuario).lower():
                    rid = str(ru.get("fkidrol"))
                    ids_rol_del_usuario.append(rid)
                    if rid in rol_por_id:
                        roles_del_usuario.append(rol_por_id[rid])

            rutas_del_usuario: list[dict[str, Any]] = []
            ids_ruta_vistos: set[str] = set()
            for rr in rutarol:
                if str(rr.get("fkidrol")) in ids_rol_del_usuario:
                    rid = str(rr.get("fkidruta"))
                    if rid in ruta_por_id and rid not in ids_ruta_vistos:
                        rutas_del_usuario.append(ruta_por_id[rid])
                        ids_ruta_vistos.add(rid)

            return roles_del_usuario, rutas_del_usuario
        except ApiError as exc:
            _log.error("Fallback de roles/rutas también falló: %s", exc)
            return [], []

    # =================================================================
    # 3. CAMBIO DE CONTRASEÑA
    # =================================================================
    def cambiar_contrasena(
        self,
        usuario_id: Any,
        email: str,
        actual: str,
        nueva: str,
    ) -> tuple[bool, str]:
        """Cambia la contraseña verificando la actual.

        Devuelve ``(ok, mensaje)``. No loggea nunca la contraseña plana.
        """
        # 1. Re-autenticar para verificar la contraseña actual.
        resp = requests.post(
            f"{self.api.base_url}/api/autenticacion/token",
            json={"email": email, "contrasena": actual},
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=self.api.timeout,
        )
        if resp.status_code != 200:
            return False, "La contraseña actual es incorrecta."

        # 2. Validar la nueva.
        ok, motivo = self.validar_contrasena_nueva(nueva, email)
        if not ok:
            return False, motivo or "La nueva contraseña no cumple las reglas."

        # 3. Actualizar vía API con cifrado.
        try:
            self.api.actualizar(
                "usuario",
                usuario_id,
                {"contrasena": nueva, "requiere_cambio": False},
                campos_encriptar=["contrasena"],
            )
            return True, "Contraseña actualizada correctamente."
        except ApiError as exc:
            _log.error("Fallo al actualizar contraseña: %s", exc)
            return False, "No se pudo actualizar la contraseña. Intenta más tarde."

    # =================================================================
    # 4. RECUPERACIÓN DE CONTRASEÑA (SMTP)
    # =================================================================
    def recuperar_contrasena(self, email: str) -> tuple[bool, str]:
        """Genera una contraseña temporal y la envía por SMTP.

        SIEMPRE devuelve un mensaje neutro al usuario (FR-015).
        """
        mensaje_neutro = (
            "Si el correo está registrado, recibirás un mensaje con las "
            "instrucciones para iniciar sesión."
        )

        # Buscar el usuario (sin revelar si existe).
        try:
            usuarios = self.api.listar("usuario") or []
        except ApiError:
            # Error interno: no revelar existencia.
            return True, mensaje_neutro

        usuario = next((u for u in usuarios if str(u.get("email", "")).lower() == email.lower()), None)
        if not usuario:
            return True, mensaje_neutro

        temporal = self._generar_contrasena_temporal()
        try:
            self.api.actualizar(
                "usuario",
                usuario["id"],
                {"contrasena": temporal, "requiere_cambio": True},
                campos_encriptar=["contrasena"],
            )
        except ApiError as exc:
            _log.error("Fallo al persistir contraseña temporal: %s", exc)
            return False, "No se pudo procesar la solicitud. Intenta más tarde."

        try:
            self._enviar_email_recuperacion(email, temporal)
        except Exception as exc:
            # Rollback del flag requiere_cambio para no dejar al usuario en estado incoherente.
            _log.error("Fallo SMTP al enviar recuperación: %s", exc)
            try:
                self.api.actualizar("usuario", usuario["id"], {"requiere_cambio": False})
            except ApiError:
                pass
            return False, "No se pudo enviar el correo de recuperación. Intenta más tarde."

        return True, mensaje_neutro

    def _generar_contrasena_temporal(self) -> str:
        """Genera 12 caracteres con al menos una mayúscula y un dígito."""
        alfabeto = string.ascii_letters + string.digits
        while True:
            temp = "".join(secrets.choice(alfabeto) for _ in range(12))
            if any(c.isupper() for c in temp) and any(c.isdigit() for c in temp):
                return temp

    def _enviar_email_recuperacion(self, destinatario: str, temporal: str) -> None:
        if not self.smtp.get("host") or not self.smtp.get("user"):
            raise RuntimeError("SMTP no configurado")

        cuerpo = (
            "Hola,\n\n"
            "Se solicitó un restablecimiento de contraseña para tu cuenta en el "
            "sistema Zenith. Tu contraseña temporal es:\n\n"
            f"    {temporal}\n\n"
            "Al iniciar sesión con ella se te pedirá establecer una nueva antes "
            "de poder continuar.\n\n"
            "Si no solicitaste este cambio, ignora este mensaje.\n\n"
            "— Zenith"
        )
        msg = MIMEText(cuerpo, _charset="utf-8")
        msg["Subject"] = "Recuperación de contraseña — Zenith"
        msg["From"] = self.smtp.get("from") or self.smtp["user"]
        msg["To"] = destinatario

        with smtplib.SMTP(self.smtp["host"], int(self.smtp.get("port", 587))) as s:
            s.starttls()
            s.login(self.smtp["user"], self.smtp["password"])
            s.send_message(msg)

    # =================================================================
    # 5. VALIDACIÓN DE CONTRASEÑA (función pura)
    # =================================================================
    def validar_contrasena_nueva(self, contrasena: str, email: str) -> tuple[bool, str | None]:
        """Reglas: ≥6 chars, ≥1 mayúscula, ≥1 dígito, no trivial, no = email.

        Orden: evaluamos primero las reglas con mensajes MÁS específicos
        (triviales, coincide con correo) para no ocultarlas bajo un genérico
        "falta mayúscula" cuando el usuario puso "password" o su propio correo.
        """
        if not isinstance(contrasena, str) or len(contrasena) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres."
        # 1) Triviales: mensaje más informativo primero.
        if contrasena in _CONTRASENAS_TRIVIALES:
            return False, "La contraseña es demasiado común. Elige una menos predecible."
        # 2) Coincide con correo.
        email_normalizado = (email or "").lower()
        local = email_normalizado.split("@", 1)[0] if "@" in email_normalizado else email_normalizado
        if contrasena.lower() == email_normalizado or (local and contrasena.lower() == local):
            return False, "La contraseña no puede coincidir con tu correo."
        # 3) Reglas compositivas.
        if not any(c.isupper() for c in contrasena):
            return False, "La contraseña debe incluir al menos una letra mayúscula."
        if not any(c.isdigit() for c in contrasena):
            return False, "La contraseña debe incluir al menos un dígito."
        return True, None

    # =================================================================
    # 6. DESCUBRIMIENTO DINÁMICO DE PKs Y FKs (T008b)
    # =================================================================
    def descubrir_pks_fks(self, tabla: str) -> dict[str, Any]:
        """Consulta los metadatos de la tabla en la API.

        Devuelve ``{"pk": str, "fks": [{"campo", "tabla_referenciada",
        "campo_referenciado"}, ...]}``. Cachea el resultado en memoria por
        proceso para evitar N+1 (T008c prueba el cacheo).

        Convención del endpoint: ``GET /api/metadata/<tabla>``. Si la API no
        lo expone todavía, devuelve un diccionario con ``pk=None`` y
        ``fks=[]`` sin reventar — el frontend degrada limpiamente y los
        Blueprints pueden seguir usando PKs conocidas.
        """
        if tabla in self._metadata_cache:
            return self._metadata_cache[tabla]

        try:
            # Usamos requests directo para no inflar ApiService con rutas no-CRUD.
            resp = requests.get(
                f"{self.api.base_url}/api/metadata/{tabla}",
                headers={"Accept": "application/json"},
                timeout=self.api.timeout,
            )
            if resp.status_code == 200:
                datos = resp.json() or {}
                resultado = {
                    "pk": datos.get("pk"),
                    "fks": list(datos.get("fks") or []),
                }
            else:
                resultado = {"pk": None, "fks": []}
        except Exception as exc:
            _log.debug("descubrir_pks_fks falló para %s: %s", tabla, exc)
            resultado = {"pk": None, "fks": []}

        self._metadata_cache[tabla] = resultado
        return resultado

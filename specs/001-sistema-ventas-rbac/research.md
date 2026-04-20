# Phase 0 Research — Sistema de Ventas con RBAC y Facturación

**Feature**: 001-sistema-ventas-rbac
**Fecha**: 2026-04-19

El `spec.md` no dejó marcadores `[NEEDS CLARIFICATION]` y la Constitución fija el stack. Este documento consolida decisiones técnicas puntuales dentro del marco ya aprobado (no hay espacio para cambiar de stack) y recoge buenas prácticas específicas para la integración con `ApiGenericaCsharp`.

## 1. Integración con la API REST `ApiGenericaCsharp`

- **Decisión**: Toda llamada HTTP pasa por una única instancia de `ApiService` que: (a) mantiene la URL base leída de `API_BASE_URL`, (b) inyecta automáticamente el header `Authorization: Bearer <token>` tomándolo de `flask.session`, (c) expone cuatro métodos genéricos `listar(tabla)`, `crear(tabla, datos, campos_encriptar=None)`, `actualizar(tabla, pk, datos, campos_encriptar=None)`, `eliminar(tabla, pk)` + `ejecutar_sp(nombre_sp, parametros)`, y (d) convierte cualquier `HTTPError` en una excepción de dominio `ApiError` con `status_code`, `mensaje` y `detalle`.
- **Rationale**: Centralizar satisface el Principio I (todo va por un único punto), permite capturar auditoría y reintentos en un solo lugar, y evita que los Blueprints conozcan detalles HTTP.
- **Alternativas consideradas**:
  - *Cliente HTTP por Blueprint*: descartado — duplica código de autenticación y no se alinea con el Principio II (servicio genérico centralizado).
  - *Librería auto-generada desde Swagger*: descartado — introduce dependencia pesada innecesaria y oculta el contrato simple ya expuesto por la API genérica.

## 2. Manejo de sesión y JWT

- **Decisión**: Guardar el JWT en `flask.session["token"]` cifrada por `SECRET_KEY` (cookie firmada); también `session["usuario"]`, `session["roles"]`, `session["rutas_permitidas"]` y `session["requiere_cambio_contrasena"]`. Timeout de inactividad 30 minutos (`PERMANENT_SESSION_LIFETIME`).
- **Rationale**: Flask `session` ya está cifrada por defecto y es el mecanismo más sencillo para SSR. Cumple Principio III (JWT en session, no expuesto a templates) y evita almacenar tokens en `localStorage` (no hay JS framework).
- **Alternativas consideradas**:
  - *Server-side session con Redis*: descartado — añade dependencia de infraestructura no justificada para la escala prevista.
  - *Guardar token en cookie HTTP-only aparte*: descartado — duplica canales; la cookie de sesión ya cubre el requisito.

## 3. Control RBAC en middleware

- **Decisión**: Un único handler `@app.before_request` que, por cada petición, ejecuta este árbol:

```mermaid
flowchart TD
    A[request] --> B{¿ruta pública<br/>o /static?}
    B -->|sí| Z[dejar pasar]
    B -->|no| C{¿hay<br/>session['token']?}
    C -->|no| D[redirigir a /login]
    C -->|sí| E{¿requiere_cambio_<br/>contrasena?}
    E -->|sí y ruta != /cambiar-contrasena| F[redirigir a /cambiar-contrasena]
    E -->|no| G{¿request.path ∈<br/>rutas_permitidas?}
    G -->|sí| Z
    G -->|no| H[render acceso_denegado 403]
```

- **Rationale**: Un solo punto de entrada hace la política testeable (FR-006 a FR-010 son verificables en `tests/integration/test_rbac_middleware.py`). El patrón coincide literalmente con la Constitución (Principio II).
- **Alternativas consideradas**:
  - *Decorador por ruta*: descartado — fácil olvidar uno; RBAC por omisión es más seguro.
  - *Flask-Login*: descartado — añade una capa innecesaria sobre `session` y no cubre RBAC dinámico por BD.

## 4. Carga de roles y rutas tras login

- **Decisión**: Llamar a `ConsultasController` de la API (una sola consulta SQL con 5 JOINs) vía `api_service.ejecutar_sp("consulta_roles_y_rutas_por_usuario", {...})`. Si falla (HTTP ≥500 o timeout), ejecutar fallback: 5 `GET` separados al CRUD genérico (`usuario`, `rol_usuario`, `rol`, `rutarol`, `ruta`) y hacer el JOIN en memoria. Si también falla, rechazar login con mensaje operativo.
- **Rationale**: Cubre FR-010 (mecanismo de respaldo). Un único `SELECT` consolidado es más eficiente y evita condición de carrera entre lecturas sueltas.
- **Alternativas consideradas**:
  - *Sólo fallback N GETs*: descartado — más lento y frágil en el caso feliz.
  - *Sólo consulta consolidada sin fallback*: descartado — violaría FR-010.

## 5. Validación de contraseñas

- **Decisión**: Función pura `validar_contrasena_nueva(contrasena, email)` en `services/auth_service.py` que aplica: longitud ≥6, ≥1 mayúscula, ≥1 dígito, no igual al email ni al local-part, no en lista corta de triviales (`"123456"`, `"Password1"`, `"Qwerty1"`...). Devuelve `(ok: bool, motivo: str | None)`. Se prueba en `tests/unit/test_validadores_contrasena.py`.
- **Rationale**: Cumple FR-012 con una función trivialmente testeable y con mensajes concretos (SC-010, minimizar genéricos).
- **Alternativas consideradas**: `zxcvbn` — descartado; dependencia adicional no justificada dado que la Constitución impone stack mínimo.

## 6. Recuperación de contraseña por SMTP

- **Decisión**: `AuthService.recuperar_contrasena(email)` genera contraseña temporal (12 caracteres, con mayúsculas/números), llama a la API para persistirla con flag "requiere cambio" y la envía por SMTP Gmail (TLS en 587) usando `smtplib` de la stdlib. Credenciales en `SMTP_USER`/`SMTP_APP_PASSWORD` (App Password de Google). Respuesta al usuario siempre genérica (FR-015). Fallo SMTP hace rollback del flag "requiere cambio" y devuelve error operativo.
- **Rationale**: `smtplib` es stdlib — cero dependencias adicionales. La secuencia "persistir → enviar → confirmar" evita el estado incoherente del edge case documentado.
- **Alternativas consideradas**: `Flask-Mail` — descartado por ser una dependencia innecesaria para un único flujo de envío.

## 7. Estructura de Blueprints y CRUDs simples

- **Decisión**: Para los 7 CRUDs simples, cada Blueprint expone 5 rutas estándar: `GET /<modulo>` (listar), `GET /<modulo>/nuevo` (form crear), `POST /<modulo>/nuevo` (crear), `GET /<modulo>/editar/<pk>` (form editar + POST), `POST /<modulo>/eliminar/<pk>`. Todas delegan en `api_service.listar/crear/actualizar/eliminar` con la tabla correspondiente.
- **Rationale**: Consistencia de URLs, consistencia en templates (misma macro `tabla_crud.html` y `form_campo.html` para todos). Satisface Principio II (patrón Blueprint) y reduce superficie de error.
- **Alternativas consideradas**: Un solo Blueprint parametrizado — descartado porque dificulta el RBAC por ruta (cada módulo necesita su propia ruta registrada en `rutarol`).

## 8. Facturas maestro-detalle en el formulario

- **Decisión**: Formulario SSR con filas dinámicas generadas con JavaScript vanilla **mínimo** (añadir/eliminar fila, recalcular subtotal en la UI para feedback visual, pero **el cálculo final lo hace el SP** en la API). Envío como `multipart/form-data` con arrays `producto_codigo[]`, `cantidad[]`. El servicio Python empaca un JSON con la lista y llama a `sp_insertar_factura_y_productosporfactura`.
- **Rationale**: JS vanilla ≠ framework JS; la Constitución prohíbe React/Vue/Angular/Svelte/htmx/Alpine/Webpack, pero permite JS vanilla mínimo integrado en `base.html`. Los cálculos canónicos los realizan los triggers/SP (Assumption "Reglas de negocio…").
- **Alternativas consideradas**:
  - *Totalmente server-side con un POST por fila*: descartado — experiencia de usuario pobre y latencia excesiva.
  - *htmx*: descartado — requeriría amendment de la Constitución.

## 9. Hoja de estilos Zenith

- **Decisión**: Un único `static/css/app.css` con bloque `:root` que define variables para colores, tipografía, bordes y sombras, luego overrides dirigidos a variables y clases de Bootstrap 5.3 (por ejemplo `--bs-primary`, `.btn-primary`, `.table thead`). Cargar Bootstrap CSS, Bootstrap Icons, Inter y JetBrains Mono desde CDN con `integrity` SRI. El CSS referencia el `Manual_de_Marca_Zenith.md` para valores.
- **Rationale**: Cumple Principio IV (CSS custom properties, override explícito de Bootstrap, un solo archivo).
- **Alternativas consideradas**: *Sass preprocesado* — descartado, añadiría build step prohibido por la Constitución.

## 10. Testing de integración sin mocks

- **Decisión**: `conftest.py` levanta un cliente Flask con configuración `TESTING=True` y `API_BASE_URL` apuntando a un entorno de pruebas de `ApiGenericaCsharp` (variable de entorno `API_BASE_URL_TESTS`). Fixture `usuario_admin` / `usuario_vendedor` hace login real y devuelve cliente autenticado. Cada test limpia su propio estado mediante SPs o endpoints DELETE cuando aplica. Los datos semilla para los tests se documentan en `quickstart.md`.
- **Rationale**: Cumple Principio V (integración real, sin mocks). Detecta incompatibilidades reales de contrato API.
- **Alternativas consideradas**: *Mock de `ApiService`* — descartado por violación directa del principio.

## 11. Gestión de errores visibles al usuario

- **Decisión**: `ApiError` y validaciones locales se capturan en un errorhandler global y se convierten en `flash(mensaje, categoria)`. Categorías: `success`, `danger` (error), `warning`, `info` — cada una con su `borde-izquierdo-4px-<color>` en `app.css`. Errores HTTP 401 del API → logout + flash "Sesión expirada". 403 → render `acceso_denegado.html`. 5xx → flash genérico + log en stderr.
- **Rationale**: Cubre FR-035 y SC-010 (≤1% mensajes genéricos).
- **Alternativas consideradas**: Excepciones crudas → no accionables para el usuario; descartado.

## 12. Configuración y secretos

- **Decisión**: `config.py` lee de entorno con `python-dotenv` en desarrollo. Variables obligatorias:
  - `SECRET_KEY` (cookie session)
  - `API_BASE_URL` (p. ej. `https://api.zenith.local`)
  - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_APP_PASSWORD`, `SMTP_FROM`
  - (Testing) `API_BASE_URL_TESTS`
  `.env` **no** se commitea; `.env.example` sí.
- **Rationale**: Cumple Restricciones Técnicas (secretos fuera del código). `python-dotenv` es dependencia justificada por necesidad explícita.
- **Alternativas consideradas**: `Dynaconf` — overkill para este proyecto.

## 13. Serialización de fechas y números

- **Decisión**: El frontend formatea fechas (`dd/mm/yyyy`) y números (`$1,234.56`) con `babel.numbers` **solo si fuera necesario**; primera iteración usa filtros Jinja personalizados en español con `locale='es_ES'`. No se añade `Babel` si los filtros simples bastan.
- **Rationale**: Minimizar dependencias (Principio de stack fijo).
- **Alternativas consideradas**: `Flask-Babel` — reservar para cuando haya i18n real.

## Síntesis

Todas las decisiones caben dentro del stack ratificado por la Constitución v1.0.0. No se requiere ningún amendment. Ninguna decisión introduce una dependencia externa adicional que no estuviera ya prevista (`requests`, `python-dotenv`). La próxima fase (data-model + contracts) puede proceder sin bloqueos.

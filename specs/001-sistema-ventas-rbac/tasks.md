---
description: "Task list for feature 001-sistema-ventas-rbac"
---

# Tasks: Sistema de Ventas con RBAC y Facturación

**Input**: Design documents from `specs/001-sistema-ventas-rbac/`
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/api-contracts.md`, `quickstart.md`

**Tests**: INCLUIDOS — la Constitución (Principio V) exige tests `pytest` de integración real contra la API para cada Blueprint. Los tests unitarios se limitan a funciones puras (validaciones).

**Organization**: Tareas agrupadas por historia de usuario (US1–US5) para permitir entrega incremental.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivo distinto, sin dependencias pendientes)
- **[Story]**: Historia de usuario a la que pertenece (US1–US5)
- Todas las tareas incluyen ruta de archivo exacta

## Path Conventions

Proyecto único Flask (raíz del repo). Rutas relativas al working directory: `routes/`, `services/`, `templates/`, `static/`, `tests/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicializar el esqueleto del proyecto, dependencias y configuración base.

- [ ] T001 Crear la estructura de directorios del proyecto conforme al plan: `services/`, `routes/`, `templates/layout/`, `templates/components/`, `templates/pages/`, `static/css/`, `static/img/`, `tests/integration/`, `tests/unit/`
- [ ] T002 Crear `requirements.txt` en la raíz con: `Flask==3.*`, `requests`, `python-dotenv`, `pytest`, `pytest-flask`, fijando versiones compatibles con Python 3.12
- [ ] T003 [P] Crear `.env.example` en la raíz con las variables: `SECRET_KEY`, `API_BASE_URL`, `API_BASE_URL_TESTS`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_APP_PASSWORD`, `SMTP_FROM`
- [ ] T004 [P] Actualizar `.gitignore` en la raíz para incluir `.venv/`, `.env`, `__pycache__/`, `.pytest_cache/`, `*.pyc`
- [ ] T005 [P] Crear `pytest.ini` o sección `[tool.pytest.ini_options]` en `pyproject.toml` con `testpaths = ["tests"]`, `pythonpath = ["."]` y marcador `integration`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Servicios compartidos, layout Zenith, middleware y fixtures que todas las historias necesitan.

**⚠️ CRITICAL**: Ninguna historia (US1–US5) puede comenzar hasta que esta fase esté completa.

- [ ] T006 Crear `config.py` en la raíz que cargue variables de entorno con `python-dotenv` y exponga una clase `Config` con `SECRET_KEY`, `API_BASE_URL`, `PERMANENT_SESSION_LIFETIME=timedelta(minutes=30)`, `SESSION_COOKIE_HTTPONLY=True`, `SMTP_*`
- [ ] T007 Crear `services/__init__.py` vacío y `services/api_service.py` con la clase `ApiService` (métodos: `__init__(base_url, session_getter)`, `_headers()`, `listar(tabla)`, `crear(tabla, datos, campos_encriptar=None)`, `actualizar(tabla, pk, datos, campos_encriptar=None)`, `eliminar(tabla, pk)`, `ejecutar_sp(nombre, parametros)`) y la excepción de dominio `ApiError(status_code, mensaje, detalle)` conforme a `contracts/api-contracts.md` §4
- [ ] T008 Crear `services/auth_service.py` con la clase `AuthService` (métodos: `login(email, contrasena)`, `cargar_roles_y_rutas(usuario_id)` con fallback según research.md §4, `cambiar_contrasena(id, actual, nueva)`, `recuperar_contrasena(email)`, `validar_contrasena_nueva(contrasena, email)` como función pura). El método `descubrir_pks_fks(tabla)` se implementa en T008b (no queda como placeholder).
- [ ] T008b Implementar `AuthService.descubrir_pks_fks(tabla)` en `services/auth_service.py`: consulta el endpoint de metadatos de la API (p. ej. `GET /api/metadata/<tabla>`, según convención de `ApiGenericaCsharp`); devuelve `{"pk": str, "fks": [{"campo": str, "tabla_referenciada": str, "campo_referenciado": str}, ...]}`. Cachea el resultado en memoria por proceso para evitar N+1. Cumple el Principio II (descubrimiento dinámico de PKs/FKs).
- [ ] T008c [P] Escribir `tests/unit/test_descubrir_pks_fks.py` con casos: tabla con PK simple (p. ej. `producto.codigo`); tabla con PK autoincremental (`cliente.id`); tabla con múltiples FKs (`cliente` → `persona` y `empresa`); cacheo: llamar dos veces y comprobar que sólo hay una llamada HTTP (usando un `ApiService` con contador inyectado — mock local válido por ser test **unitario**, no de integración).
- [ ] T009 [P] Crear `tests/unit/test_validadores_contrasena.py` con pruebas exhaustivas de `validar_contrasena_nueva`: longitud mínima, mayúscula requerida, dígito requerido, rechazo de triviales (`"123456"`, `"Password1"`), rechazo cuando coincide con el email o su local-part
- [ ] T010 Crear `middleware.py` en la raíz con la función `registrar_middleware(app)` que añade `@app.before_request` implementando el flujo del research.md §3 (rutas públicas → sesión → `requiere_cambio_contrasena` → `rutas_permitidas`) y un `@app.context_processor` que inyecta `usuario`, `roles`, `rutas_permitidas`
- [ ] T011 Crear `app.py` en la raíz que instancia `Flask`, aplica `Config`, inicializa `ApiService` y `AuthService` como atributos de `app`, registra el middleware y expone un bloque `if __name__ == "__main__": app.run()`. Los blueprints se registran aquí pero aún no existen (importación condicional).
- [ ] T012 [P] Crear `static/css/app.css` con el bloque `:root` completo de variables Zenith (colores primario `#0A2647`, secundario `#E8AA2E`, acento `#144272`, tipografías Inter y JetBrains Mono, radios, sombras) y overrides de Bootstrap 5.3 (`--bs-primary`, `--bs-secondary`, `.btn-primary`, `.table thead`, `.alert-*` con borde izquierdo 4px)
- [ ] T013 [P] Crear `templates/layout/base.html` con estructura Bootstrap 5.3 (sidebar + topbar con nombre de usuario y botón logout + área de flashes + bloque `content`), incluyendo `<link>` a Bootstrap, Bootstrap Icons, Google Fonts (Inter, JetBrains Mono) y `static/css/app.css`
- [ ] T014 [P] Crear `templates/layout/login_layout.html` con fondo gradiente `#0A2647 → #144272` y tarjeta blanca centrada según Principio IV, incluyendo `app.css`
- [ ] T015 [P] Crear `templates/layout/nav_menu.html` con el mapeo `ruta → (icono bi-*, etiqueta)` y la lógica Jinja que renderiza cada ítem sólo si `ruta in rutas_permitidas`
- [ ] T016 [P] Crear `templates/components/flash.html` con macro `{% macro render_flashes() %}` que recorre `get_flashed_messages(with_categories=true)` y renderiza alertas Bootstrap dismissible con borde izquierdo 4px por estado
- [ ] T017 [P] Crear `templates/components/tabla_crud.html` con macro que recibe `(columnas, filas, url_editar, url_eliminar)` y renderiza una tabla Bootstrap con estilo Zenith
- [ ] T018 [P] Crear `templates/components/form_campo.html` con macro que renderiza etiqueta + input Bootstrap + mensaje de error
- [ ] T019 [P] Crear `templates/components/confirm_modal.html` con macro reutilizable para modales de confirmación (usado por "eliminar" y "anular")
- [ ] T020 [P] Crear `templates/pages/home/acceso_denegado.html` extendiendo `base.html`, mostrando mensaje 403 con botón "volver al inicio"
- [ ] T021 Crear `tests/conftest.py` con fixtures: `app` (instancia Flask con `TESTING=True` y `API_BASE_URL=API_BASE_URL_TESTS`), `client` (test client), `api_service` (instancia directa para preparar datos), `login` helper `(client, email, contrasena)` que hace POST a `/login` y deja la sesión cargada, `usuario_admin`, `usuario_vendedor`, `usuario_invitado` (fixtures que garantizan existencia de usuarios semilla)

**Checkpoint**: Fundaciones listas. US1–US5 pueden iniciar (sujetas a dependencias declaradas abajo).

---

## Phase 3: User Story 1 — Acceso autenticado con RBAC (Priority: P1) 🎯 MVP

**Goal**: Un usuario puede iniciar sesión, ver un menú filtrado por su rol, ser bloqueado al intentar rutas no autorizadas y cerrar sesión.

**Independent Test**: Con dos usuarios semilla (`admin@zenith.test`, `vendedor@zenith.test`) probar login exitoso de ambos; verificar menús distintos; acceder por URL a ruta no permitida y recibir 403; verificar logout + redirección a `/login`.

### Tests for User Story 1

> Los tests se escriben primero y deben FALLAR antes de implementar.

- [ ] T022 [P] [US1] Escribir `tests/integration/test_auth.py` con casos: login exitoso (200 redirect a `/`), login credenciales inválidas (flash error, sin sesión), logout (`session.clear()` + redirect), login con `requiere_cambio=true` fuerza `/cambiar-contrasena`
- [ ] T023 [P] [US1] Escribir `tests/integration/test_rbac_middleware.py` con casos: acceso anónimo a `/` → 302 `/login`; acceso de `vendedor` a `/usuarios` → 403 render `acceso_denegado.html`; acceso de `vendedor` a `/facturas` → 200; menu renderizado sólo con rutas permitidas (grep en HTML)

### Implementation for User Story 1

- [ ] T024 [US1] Implementar `AuthService.login(email, contrasena)` en `services/auth_service.py`: llama a `POST /api/autenticacion/token`, guarda token en `session`, invoca `cargar_roles_y_rutas`, setea `session['usuario']`, `session['roles']`, `session['rutas_permitidas']`, `session['requiere_cambio_contrasena']`; maneja `ApiError(401)` devolviendo `None` para que la ruta muestre flash neutro
- [ ] T025 [US1] Implementar `AuthService.cargar_roles_y_rutas(usuario_id)` en `services/auth_service.py` con la consulta consolidada al SP `consulta_roles_y_rutas_por_usuario` (vía `api_service.ejecutar_sp`) y el fallback de 5 GETs descrito en `contracts/api-contracts.md` §5; abortar con excepción si ambos fallan
- [ ] T026 [US1] Crear `routes/__init__.py` vacío y `routes/auth.py` con Blueprint `auth_bp` que expone `GET /login`, `POST /login`, `GET /logout`; incluir docstring tutorial explicando el flujo de autenticación y cómo se relaciona con `AuthService` y el middleware
- [ ] T027 [US1] Crear `templates/pages/auth/login.html` extendiendo `login_layout.html`, con formulario email + contraseña + botón dorado 100% ancho + enlace "¿olvidaste tu contraseña?" (el destino real se implementa en US5, por ahora puede apuntar a `/recuperar-contrasena` aunque aún no exista — marcar con comentario Jinja)
- [ ] T028 [US1] Crear `routes/home.py` con Blueprint `home_bp` que expone `GET /` (renderiza `templates/pages/home/index.html`). Crear `templates/pages/home/index.html` con saludo al usuario y accesos rápidos según rutas permitidas
- [ ] T029 [US1] En `middleware.py`, activar la lógica RBAC completa (research.md §3): rutas públicas exactamente `["/login", "/logout", "/recuperar-contrasena"]` + prefijo `/static`; desde `session.get("token")` disparar redirección o render 403 según corresponda; usar `render_template("pages/home/acceso_denegado.html"), 403`
- [ ] T030 [US1] En `app.py`, registrar `auth_bp` y `home_bp`; confirmar que `registrar_middleware(app)` está después del registro
- [ ] T031 [US1] Verificar que el context processor inyecta `usuario`, `roles`, `rutas_permitidas` en todas las templates y que `base.html` muestra `usuario.email` y `nav_menu.html` usa `rutas_permitidas`
- [ ] T032 [US1] Ejecutar `pytest tests/integration/test_auth.py tests/integration/test_rbac_middleware.py -v` y validar que todos los escenarios del FR-001..FR-010 pasan

**Checkpoint**: US1 completa. El MVP ya es desplegable — los usuarios autenticados ven su menú y están bloqueados de rutas no autorizadas.

---

## Phase 4: User Story 2 — Facturación maestro-detalle con anulación lógica (Priority: P2)

**Goal**: Usuarios autorizados pueden listar, consultar, crear, editar y anular facturas; administradores adicionalmente pueden borrarlas físicamente.

**Independent Test**: Crear factura con 3 líneas, verificar que el stock baja y la factura aparece "activa"; anularla y verificar que el stock vuelve al valor previo y la factura queda "anulada" pero visible; con rol `administrador`, borrarla físicamente y comprobar que desaparece; con rol `vendedor`, el botón de borrado físico no está.

### Tests for User Story 2

- [ ] T033 [P] [US2] Escribir `tests/integration/test_factura.py` con fixtures de datos semilla (empresa, persona, cliente, vendedor, productos con stock >=5) y casos: crear factura con 2 líneas (verifica `sp_insertar_factura_y_productosporfactura` devuelve `id` y stock disminuye); consultar detalle (cliente, vendedor, líneas); editar factura (reemplaza líneas, recalcula total); anular factura activa (estado `anulada`, stock restaurado); intento anular ya anulada (400 + flash); admin puede borrar físicamente (sp_borrar), vendedor no ve el botón; crear factura con cantidad > stock falla sin alterar datos

### Implementation for User Story 2

- [ ] T034 [US2] Crear `routes/factura.py` con Blueprint `factura_bp` que expone: `GET /facturas` (listar), `GET /facturas/<id>` (detalle), `GET /facturas/nueva`, `POST /facturas/nueva`, `GET /facturas/editar/<id>`, `POST /facturas/editar/<id>`, `POST /facturas/anular/<id>`, `POST /facturas/eliminar/<id>` (sólo admin). Docstring tutorial explicando el flujo maestro-detalle y la anulación lógica.
- [ ] T035 [US2] Crear `templates/pages/factura/listar.html` con tabla que muestra id, fecha, cliente, vendedor, total, estado (`activa`/`anulada`) y acciones condicionadas por rol (anular si activa; eliminar si admin)
- [ ] T036 [US2] Crear `templates/pages/factura/formulario.html` con selects de cliente y vendedor (alimentados desde `GET /api/cliente` y `GET /api/vendedor`), tabla editable de líneas (producto select + cantidad input) con JS vanilla mínimo (añadir/eliminar fila, actualizar subtotal visual); submit envía arrays `fkcodproducto[]` y `cantidad[]`
- [ ] T037 [US2] Crear `templates/pages/factura/detalle.html` mostrando cabecera (cliente, vendedor, fecha, estado, total) y tabla de líneas con `producto`, `cantidad`, `valorunitario`, `subtotal` (fuente: `sp_consultar_factura_y_productosporfactura`)
- [ ] T038 [US2] En `routes/factura.py`, implementar los handlers usando `api_service.ejecutar_sp` con los SPs del contrato (§3): `sp_listar_facturas_y_productosporfactura`, `sp_consultar_factura_y_productosporfactura`, `sp_insertar_factura_y_productosporfactura`, `sp_actualizar_factura_y_productosporfactura`, `sp_anular_factura`, `sp_borrar_factura_y_productosporfactura`; capturar `ApiError` → flash con categoría correcta
- [ ] T039 [US2] En el handler de eliminar físico, verificar `'administrador' in session['roles']` antes de llamar al SP; si no, `abort(403)`. Documentar con comentario tutorial por qué la comprobación ocurre también en frontend aunque la API la valide.
- [ ] T040 [US2] Registrar `factura_bp` en `app.py`; insertar en el catálogo estático de `nav_menu.html` la entrada "Facturas" con icono `bi-receipt` (según Manual de Marca) vinculada a `/facturas`
- [ ] T041 [US2] Ejecutar `pytest tests/integration/test_factura.py -v` y validar que FR-025..FR-034 y SC-003, SC-004, SC-005, SC-009 se cumplen

**Checkpoint**: US2 completa. El valor de negocio principal (facturación) está operativo.

---

## Phase 5: User Story 3 — Mantenimiento de catálogos (Priority: P3)

**Goal**: Siete CRUDs simples (Producto, Persona, Empresa, Cliente, Vendedor, Rol, Ruta) con listado, creación, edición y eliminación con confirmación.

**Independent Test**: Por cada catálogo, recorrer el ciclo listar → crear → editar → eliminar y verificar persistencia; para Cliente/Vendedor verificar que el listado muestra datos enriquecidos de Persona/Empresa.

### Tests for User Story 3

- [ ] T042 [P] [US3] Escribir `tests/integration/test_producto.py` con ciclo CRUD completo + validación de `stock ≥ 0` y `valorunitario ≥ 0`
- [ ] T043 [P] [US3] Escribir `tests/integration/test_persona.py` con ciclo CRUD + validación formato email + caso "persona referenciada por cliente no se puede eliminar" (FR-020, espera 409/mensaje)
- [ ] T044 [P] [US3] Escribir `tests/integration/test_empresa.py` con ciclo CRUD
- [ ] T045 [P] [US3] Escribir `tests/integration/test_cliente.py` con ciclo CRUD + verificación de que el listado muestra `persona.nombre` y `empresa.nombre`
- [ ] T046 [P] [US3] Escribir `tests/integration/test_vendedor.py` con ciclo CRUD + verificación de enriquecimiento con `persona.nombre`
- [ ] T047 [P] [US3] Escribir `tests/integration/test_rol.py` con ciclo CRUD
- [ ] T048 [P] [US3] Escribir `tests/integration/test_ruta.py` con ciclo CRUD

### Implementation for User Story 3

- [ ] T049 [P] [US3] Crear `routes/producto.py` con Blueprint `producto_bp` (listar/nuevo/editar/eliminar) usando `api_service.listar/crear/actualizar/eliminar("producto")` y plantillas `templates/pages/producto/listar.html` y `templates/pages/producto/formulario.html` (reutilizar macros `tabla_crud.html` y `form_campo.html`)
- [ ] T050 [P] [US3] Crear `routes/persona.py` + `templates/pages/persona/listar.html` + `templates/pages/persona/formulario.html` (validar email en el form con patrón HTML5 + validación server-side)
- [ ] T051 [P] [US3] Crear `routes/empresa.py` + `templates/pages/empresa/listar.html` + `templates/pages/empresa/formulario.html`
- [ ] T052 [P] [US3] Crear `routes/cliente.py` + `templates/pages/cliente/listar.html` + `templates/pages/cliente/formulario.html`: el listado enriquece cruzando con `api_service.listar("persona")` y `api_service.listar("empresa")` y muestra `persona.nombre` + `empresa.nombre` en lugar de los IDs
- [ ] T053 [P] [US3] Crear `routes/vendedor.py` + `templates/pages/vendedor/listar.html` + `templates/pages/vendedor/formulario.html` con enriquecimiento desde `persona`
- [ ] T054 [P] [US3] Crear `routes/rol.py` + `templates/pages/rol/listar.html` + `templates/pages/rol/formulario.html`
- [ ] T055 [P] [US3] Crear `routes/ruta.py` + `templates/pages/ruta/listar.html` + `templates/pages/ruta/formulario.html`
- [ ] T056 [US3] Registrar los 7 blueprints en `app.py` y añadir al catálogo de `templates/layout/nav_menu.html` las entradas con icono Bootstrap Icons según el Manual de Marca (producto→`bi-box-seam`, persona→`bi-person`, empresa→`bi-building`, cliente→`bi-person-badge`, vendedor→`bi-person-workspace`, rol→`bi-people`, ruta→`bi-signpost-split`)
- [ ] T057 [US3] Ejecutar `pytest tests/integration/test_producto.py tests/integration/test_persona.py tests/integration/test_empresa.py tests/integration/test_cliente.py tests/integration/test_vendedor.py tests/integration/test_rol.py tests/integration/test_ruta.py -v` y validar FR-016..FR-020

**Checkpoint**: Catálogos operativos. La facturación de US2 queda habilitada con datos reales.

---

## Phase 6: User Story 4 — Administración de usuarios y permisos (Priority: P4)

**Goal**: Administrador puede CRUD-ear usuarios con asignación de roles vía SPs y administrar permisos ruta-rol; los cambios aplican al siguiente login del usuario afectado.

**Independent Test**: Crear un usuario con rol `vendedor`; iniciar sesión con esa cuenta y confirmar que ve el menú de `vendedor`. Actualizar sus roles sin cambiar contraseña, reiniciar sesión, confirmar menú actualizado. Añadir una ruta a un rol; reiniciar sesión y confirmar acceso. Eliminar el permiso y confirmar pérdida de acceso.

### Tests for User Story 4

- [ ] T058 [P] [US4] Escribir `tests/integration/test_usuario.py` con casos: listar usuarios con roles (SP `listar_usuarios_con_roles`); crear usuario con roles (con `camposEncriptar=["contrasena"]`); consultar detalle; actualizar completo; actualizar sólo roles sin tocar contraseña (SP `actualizar_roles_usuario`); eliminar usuario; tras eliminar, no puede iniciar sesión
- [ ] T059 [P] [US4] Escribir `tests/integration/test_rutarol.py` con casos: listar permisos; crear permiso y verificar que un usuario del rol gana acceso al siguiente login; eliminar permiso y verificar pérdida de acceso

### Implementation for User Story 4

- [ ] T060 [US4] Crear `routes/usuario.py` con Blueprint `usuario_bp` exponiendo listar/consultar/nuevo/editar/actualizar-roles/eliminar, todos vía `api_service.ejecutar_sp`: `listar_usuarios_con_roles`, `consultar_usuario_con_roles`, `crear_usuario_con_roles`, `actualizar_usuario_con_roles`, `actualizar_roles_usuario`, `eliminar_usuario_con_roles`
- [ ] T061 [US4] Crear `templates/pages/usuario/listar.html` mostrando email, flag `requiere_cambio` y lista de roles; botones "editar" y "eliminar"
- [ ] T062 [US4] Crear `templates/pages/usuario/formulario.html` con: email, contraseña (opcional en edición; si vacía usa SP `actualizar_roles_usuario`), multi-select de roles (alimentado con `api_service.listar("rol")`); campo contraseña se valida con `validar_contrasena_nueva` en server-side
- [ ] T063 [US4] Crear `routes/rutarol.py` con Blueprint `rutarol_bp` (listar/crear/eliminar) vía SPs `listar_rutarol`, `crear_rutarol`, `eliminar_rutarol`
- [ ] T064 [US4] Crear `templates/pages/rutarol/listar.html` con tabla de permisos (rol, ruta, descripción) y botón eliminar con confirmación; `templates/pages/rutarol/formulario.html` con selects de rol y ruta
- [ ] T065 [US4] Registrar `usuario_bp` y `rutarol_bp` en `app.py`; añadir al `nav_menu.html` las entradas "Usuarios" (`bi-person-gear`) y "Permisos" (`bi-shield-lock`)
- [ ] T066 [US4] Ejecutar `pytest tests/integration/test_usuario.py tests/integration/test_rutarol.py -v` y validar FR-021..FR-024 y SC-008

**Checkpoint**: Sistema autoadministrable por administradores.

---

## Phase 7: User Story 5 — Gestión de contraseña por el propio usuario (Priority: P5)

**Goal**: Usuario cambia su propia contraseña y puede recuperarla por email con flujo de cambio obligatorio al siguiente login.

**Independent Test**: Cambiar contraseña desde sesión activa y comprobar que la anterior deja de servir. Pedir recuperación con email válido y recibir correo. Iniciar sesión con la temporal y ser redirigido a `/cambiar-contrasena` sin poder navegar a otras rutas.

### Tests for User Story 5

- [ ] T067 [P] [US5] Escribir `tests/integration/test_password.py` con casos: cambio exitoso (actual correcta + nueva válida); rechazo si actual incorrecta; rechazo si nueva no cumple reglas (por cada regla un caso); recuperación con email existente dispara envío SMTP (usar servidor SMTP de pruebas o monkeypatch mínimo del transporte, documentando que esto es excepción puntual al principio de "sin mocks" justificada por no enviar emails reales en CI); recuperación con email no existente responde mensaje neutro idéntico; login con temporal redirige a `/cambiar-contrasena` y bloquea todo lo demás

### Implementation for User Story 5

- [ ] T068 [US5] Implementar `AuthService.cambiar_contrasena(usuario_id, actual, nueva)` en `services/auth_service.py`: verifica actual re-autenticando contra `/api/autenticacion/token`, aplica `validar_contrasena_nueva(nueva, email)`, llama `actualizar("usuario", id, {"contrasena": nueva, "requiere_cambio": False}, camposEncriptar=["contrasena"])`; limpia flag en `session`
- [ ] T069 [US5] Implementar `AuthService.recuperar_contrasena(email)` en `services/auth_service.py`: busca usuario por email; si existe, genera temporal aleatoria (12 chars con mayús+número), actualiza usuario con `requiere_cambio=True` y la nueva contraseña encriptada; envía email con `smtplib`; en caso de fallo SMTP hace rollback (restaurar `requiere_cambio` anterior); **respuesta al usuario siempre neutra** (FR-015)
- [ ] T070 [US5] Añadir a `routes/auth.py` las rutas `GET /cambiar-contrasena`, `POST /cambiar-contrasena`, `GET /recuperar-contrasena`, `POST /recuperar-contrasena`; la ruta de cambio forzoso verifica `session['requiere_cambio_contrasena']` y, una vez completado, redirige a `/`
- [ ] T071 [US5] Crear `templates/pages/auth/cambiar_contrasena.html` extendiendo `base.html` (o `login_layout.html` si es por temporal) con form de `contrasena_actual`, `contrasena_nueva`, `confirmar_nueva`; y `templates/pages/auth/recuperar_contrasena.html` extendiendo `login_layout.html`
- [ ] T072 [US5] Verificar que la ruta `/recuperar-contrasena` está en la lista de rutas públicas del middleware (T029) y no requiere sesión
- [ ] T073 [US5] Ejecutar `pytest tests/integration/test_password.py -v` y validar FR-011..FR-015, SC-006, SC-007

**Checkpoint**: Autoservicio de contraseña operativo.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Refinamientos transversales, documentación final y endurecimiento.

- [ ] T074 [P] Añadir diagramas Mermaid al `README.md` (raíz): vista general de arquitectura Frontend→API, flujo de login/RBAC, flujo de creación de factura. Incluir tabla de rutas públicas vs privadas.
- [ ] T075 [P] Añadir docstring extenso tipo tutorial al inicio de `app.py`, `middleware.py`, `services/api_service.py`, `services/auth_service.py` explicando responsabilidades y cómo se relacionan (conforme Principio V)
- [ ] T076 [P] Revisar `static/css/app.css` contra `Manual_de_Marca_Zenith.md`: verificar todas las variables `:root`, override de `--bs-primary`, tipografías Inter/JetBrains Mono aplicadas a las clases adecuadas, estilos de alertas con borde izquierdo 4px por estado
- [ ] T077 [P] Añadir a `tests/conftest.py` un marcador de limpieza que, al finalizar la suite, elimina cualquier dato semilla creado para evitar contaminación entre corridas
- [ ] T078 Añadir `tests/integration/test_no_plaintext.py` con tres casos que cubren SC-006 (contraseñas irrecuperables): (a) **No-log**: inspeccionar `caplog` durante login, cambio y recuperación de contraseña — la contraseña plana nunca aparece en ningún `LogRecord`; (b) **No-response**: tras crear un usuario con contraseña `"TestPwd123"`, llamar `api_service.listar("usuario")` y `api_service.ejecutar_sp("consultar_usuario_con_roles", {"id": ...})` y afirmar que ningún campo de la respuesta contiene la cadena `"TestPwd123"` ni se devuelve `contrasena` con valor en claro (aceptado: ausente, `null`, o hash BCrypt `$2a$`/`$2b$`); (c) **No-template**: renderizar `templates/pages/usuario/listar.html` y `usuario/formulario.html` con datos de prueba y verificar que el HTML resultante no contiene la contraseña plana.
- [ ] T079 Ejecutar `pytest -v` completo y verificar que los 10 criterios de éxito (SC-001 a SC-010) tienen al menos un test que los valida; documentar el mapeo FR↔test en `specs/001-sistema-ventas-rbac/quickstart.md` sección nueva "Cobertura"
- [ ] T080 Endurecer headers de seguridad: en `app.py` establecer `SESSION_COOKIE_SECURE=True` (en producción), `SESSION_COOKIE_SAMESITE="Lax"`, `SESSION_COOKIE_HTTPONLY=True`; documentar en `quickstart.md` cómo activar HTTPS en despliegue
- [ ] T081 [P] Crear `tests/integration/test_performance.py` con dos casos marcados `@pytest.mark.performance` (exclusibles en CI con `pytest -m "not performance"`): **SC-002 (login ≤5s)** — medir con `time.perf_counter()` el tiempo end-to-end de `client.post("/login", data={...})`, repetir 5 corridas, reportar p50/p95, `assert elapsed_p95 < 5.0`; **SC-004 (factura ≤3s con 10 líneas)** — preparar 10 productos con stock, emitir `POST /facturas/nueva` con 10 líneas, repetir 5 corridas, `assert elapsed_p95 < 3.0`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias.
- **Foundational (Phase 2)**: depende de Setup. BLOQUEA todas las historias.
- **US1 (Phase 3, P1)**: depende de Foundational. MVP.
- **US2 (Phase 4, P2)**: depende de Foundational + **US1** (el middleware RBAC y la sesión son prerrequisito del acceso a `/facturas`).
- **US3 (Phase 5, P3)**: depende de Foundational + **US1** (auth). Independiente de US2 (aunque US2 se beneficia de tener productos/clientes creados vía US3 en la práctica — ver nota operativa).
- **US4 (Phase 6, P4)**: depende de Foundational + **US1**. Depende conceptualmente de US3 (rol y ruta deben existir como catálogo), pero en tiempo de desarrollo puede avanzar en paralelo porque el SP `crear_usuario_con_roles` solo necesita IDs preexistentes.
- **US5 (Phase 7, P5)**: depende de Foundational + **US1** (comparte `routes/auth.py`).
- **Polish (Phase 8)**: depende de todas las historias deseadas.

### Nota operativa sobre US2 vs US3

US2 y US3 son independientes en código (archivos distintos) y pueden programarse en paralelo. Sin embargo, los tests de integración de US2 necesitan datos de cliente, vendedor y producto. Los fixtures de `conftest.py` los crean vía llamadas `POST` — no dependen de la UI de US3 estando terminada.

### Within Each User Story

- Los tests se escriben antes y **deben fallar**; luego la implementación.
- Servicios antes que routes; routes antes que templates; templates antes de integrar el blueprint en `nav_menu.html` y `app.py`.

### Parallel Opportunities

- **Phase 1**: T003, T004, T005 en paralelo tras T001/T002.
- **Phase 2**: T008c, T009 (unit tests, archivos propios), T012–T020 (CSS + templates layout/components, archivos distintos) en paralelo tras T006–T008b y T010–T011. T021 depende de que T006–T011 existan.
- **Phase 3 (US1)**: T022 y T023 (tests) en paralelo antes de implementar.
- **Phase 5 (US3)**: T042–T048 (7 tests) en paralelo; T049–T055 (7 blueprints + templates) en paralelo.
- **Phase 6 (US4)**: T058 y T059 en paralelo.
- **Phase 8**: T074–T077 en paralelo.

---

## Parallel Example: User Story 3 (todos los CRUDs)

```bash
# Tests en paralelo
Task: "Escribir tests/integration/test_producto.py con ciclo CRUD"
Task: "Escribir tests/integration/test_persona.py con ciclo CRUD + validación email"
Task: "Escribir tests/integration/test_empresa.py con ciclo CRUD"
Task: "Escribir tests/integration/test_cliente.py con enriquecimiento persona+empresa"
Task: "Escribir tests/integration/test_vendedor.py con enriquecimiento persona"
Task: "Escribir tests/integration/test_rol.py con ciclo CRUD"
Task: "Escribir tests/integration/test_ruta.py con ciclo CRUD"

# Blueprints en paralelo (archivos distintos)
Task: "Crear routes/producto.py + templates/pages/producto/*"
Task: "Crear routes/persona.py + templates/pages/persona/*"
Task: "Crear routes/empresa.py + templates/pages/empresa/*"
Task: "Crear routes/cliente.py + templates/pages/cliente/* con enriquecimiento"
Task: "Crear routes/vendedor.py + templates/pages/vendedor/* con enriquecimiento"
Task: "Crear routes/rol.py + templates/pages/rol/*"
Task: "Crear routes/ruta.py + templates/pages/ruta/*"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Completar Phase 1 (Setup).
2. Completar Phase 2 (Foundational) — CRÍTICO.
3. Completar Phase 3 (US1).
4. **PARAR Y VALIDAR**: login, RBAC y menú dinámico funcionan end-to-end.
5. Desplegar en staging y demostrar.

### Incremental Delivery

1. MVP (US1) → demo.
2. + US2 (facturación) → demo; ya cubre el valor de negocio central.
3. + US3 (catálogos) → demo; operativo para producción con admin manual.
4. + US4 (admin usuarios/permisos) → demo; autoadministrable.
5. + US5 (autoservicio contraseña) → demo; reduce carga de soporte.
6. Polish → GA.

### Parallel Team Strategy

Con dos o más desarrolladores tras Phase 2:

- Dev A: US1 (bloquea al resto, priorizar).
- Tras US1 mergeada:
  - Dev A: US2 (facturación, mayor complejidad de dominio).
  - Dev B: US3 (CRUDs, trabajo altamente paralelizable).
  - Dev C (si existe): US4 y después US5.

---

## Notes

- Tareas marcadas [P] tocan archivos distintos y no tienen dependencias pendientes.
- El label [Story] mapea cada tarea a su historia para trazabilidad con la spec.
- Los tests de integración corren contra la API real (Principio V); la excepción mínima en T067 (transporte SMTP) se documenta explícitamente y se limita al canal de correo.
- Commitear al terminar cada tarea o grupo lógico facilita bisect si aparece regresión.
- Detenerse en cada Checkpoint para validar la historia de forma independiente antes de seguir.

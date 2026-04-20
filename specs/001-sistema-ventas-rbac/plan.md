# Implementation Plan: Sistema de Ventas con RBAC y Facturación

**Branch**: `001-sistema-ventas-rbac` | **Date**: 2026-04-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-sistema-ventas-rbac/spec.md`

## Summary

Frontend web server-side para el sistema Zenith que autentica contra la API REST externa `ApiGenericaCsharp` (JWT), aplica control de acceso por rol (RBAC) vía middleware, y expone siete CRUDs simples, administración de usuarios y permisos (stored procedures) y un flujo maestro-detalle de facturas con anulación lógica y borrado físico restringido al administrador. Enfoque técnico: Flask 3.x + Jinja2 + Bootstrap 5.3 sin framework JS; toda la persistencia se delega a la API REST mediante dos servicios centralizados (`ApiService` para CRUD + stored procedures, `AuthService` para autenticación y descubrimiento dinámico de PKs/FKs); una única hoja de estilos con la identidad Zenith. Pruebas con `pytest` como integración real contra la API (sin mocks).

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: Flask 3.x, Jinja2 (incluido en Flask), `requests`, `python-dotenv`, Bootstrap 5.3 y Bootstrap Icons (CDN o estáticos), Inter + JetBrains Mono (Google Fonts)
**Storage**: N/A — persistencia delegada 100% a la API REST externa `ApiGenericaCsharp` (C# .NET 9 + Dapper). El frontend **no** incorpora drivers de base de datos.
**Testing**: `pytest` + `pytest-flask` para integración real contra la API de pruebas (sin mocks, Principio V)
**Target Platform**: Servidor web (Linux o Windows) ejecutando Flask detrás de un WSGI (gunicorn/waitress); cliente navegador moderno (Chrome/Edge/Firefox últimas dos versiones)
**Project Type**: Aplicación web con frontend SSR (estructura de proyecto único estilo Flask clásico)
**Performance Goals**:
- Login end-to-end ≤ 5s (SC-002)
- Creación de factura con ≤10 líneas ≤ 3s desde "guardar" (SC-004)
- Listado de cualquier CRUD con ≤500 registros ≤ 2s
**Constraints**:
- Sin ORM, sin cliente de BD (Principio I + Restricciones Técnicas)
- Sin framework JavaScript (Principio II)
- Identidad visual Zenith obligatoria vía CSS custom properties en `static/css/app.css` (Principio IV)
- Código, comentarios y mensajes en español (Principio V)
- Tests de integración reales contra la API (sin mocks) (Principio V)
- Rutas públicas fijas: `/login`, `/logout`, `/recuperar-contrasena`, `/static`
**Scale/Scope**: Herramienta administrativa interna; ~10–50 usuarios concurrentes; 7 CRUDs + 3 módulos vía SPs + auth + layout; ~30 rutas privadas protegidas por RBAC.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Referencia: `.specify/memory/constitution.md` v1.0.0.

| Principio / Restricción | Cumplimiento del plan | Evidencia |
|-------------------------|-----------------------|-----------|
| I. Consumo Exclusivo de API REST (sin ORM) | ✅ | Stack explícitamente sin ORM/driver; dependencias solo `requests`, Flask, dotenv. `ApiService` centraliza CRUD y `ejecutar_sp`. |
| II. Arquitectura Blueprint + Servicios Genéricos | ✅ | Estructura `routes/<blueprint>.py` (uno por módulo) + `services/api_service.py` + `services/auth_service.py` + `middleware.py` con `@app.before_request` y context processor. |
| III. Seguridad JWT + RBAC + Borrado Lógico | ✅ | JWT guardado en `session` Flask; middleware verifica `rutas_permitidas` cada request; facturas usan `sp_anular_factura` (estado) y `sp_borrar_factura_y_productosporfactura` se restringe a rol admin. |
| IV. Identidad Visual Zenith (No Bootstrap por Defecto) | ✅ | Un solo `static/css/app.css` con `:root` que sobrescribe colores Bootstrap por los de marca Zenith (Azul `#0A2647`, Dorado `#E8AA2E`, Azul Medio `#144272`) + Inter + JetBrains Mono + Bootstrap Icons. |
| V. Código en Español + SSR + Docs Tutorial | ✅ | Nombres, comentarios y mensajes flash en español (`snake_case`); SSR con Jinja2 sin JS framework; docstrings extensos en cada módulo; `quickstart.md` incluye diagrama Mermaid. |
| Stack fijo (restricción técnica) | ✅ | Solo Python 3.12 + Flask 3.x + Jinja2 + Bootstrap 5.3 + `requests` + `python-dotenv` (dependencia necesaria para cargar configuración). |
| Sin ORM ni drivers de BD | ✅ | `requirements.txt` planificado no incluye SQLAlchemy, psycopg2, pymysql, pyodbc. |
| Sin frontend frameworks | ✅ | No se añade React/Vue/Angular/Svelte/htmx/Alpine/Webpack/Vite. |
| Rutas públicas cerradas | ✅ | Lista exacta: `/login`, `/logout`, `/recuperar-contrasena`, `/static`. |
| Borrado lógico de facturas | ✅ | Anulación vía SP con cambio de estado; borrado físico (DELETE) sólo visible al rol `administrador`. |
| Testing con pytest + integración real | ✅ | `tests/integration/` con suite por Blueprint; `conftest.py` prepara cliente Flask + fixture de API base URL apuntando a entorno de pruebas. |
| Documentación tutorial + Mermaid | ✅ | Cada archivo Python lleva docstring inicial; `quickstart.md` y `research.md` incluyen diagramas Mermaid de flujos clave. |

**Resultado**: PASS — ninguna violación detectada. La sección Complexity Tracking queda vacía.

## Project Structure

### Documentation (this feature)

```text
specs/001-sistema-ventas-rbac/
├── plan.md              # Este archivo (/speckit.plan output)
├── research.md          # Fase 0 (/speckit.plan output)
├── data-model.md        # Fase 1 (/speckit.plan output)
├── quickstart.md        # Fase 1 (/speckit.plan output)
├── contracts/
│   └── api-contracts.md # Consumer contracts contra la API REST
├── checklists/
│   └── requirements.md  # Spec quality checklist (ya existe)
└── tasks.md             # Fase 2 (lo produce /speckit.tasks — NO aquí)
```

### Source Code (repository root)

Estructura única de proyecto Flask clásico (no monorepo, no app factory anidado). Todo bajo la raíz del repositorio conforme a los paths que indica la Constitución (`routes/`, `templates/pages|layout|components`, `static/css/app.css`).

```text
app.py                   # Entry point: crea Flask app, registra blueprints, middleware, context processor
config.py                # Lectura de variables de entorno (SECRET_KEY, API_BASE_URL, SMTP_*)
middleware.py            # @app.before_request (RBAC) + context_processor (usuario/roles/rutas)

services/
├── __init__.py
├── api_service.py       # CRUD genérico (listar, crear, actualizar, eliminar) + ejecutar_sp
└── auth_service.py      # Login, refresh token, cambio y recuperación de contraseña, carga de roles/rutas,
                         # descubrimiento dinámico de PKs/FKs

routes/
├── __init__.py
├── auth.py              # /login, /logout, /cambiar-contrasena, /recuperar-contrasena
├── home.py              # /
├── producto.py          # CRUD producto
├── persona.py           # CRUD persona
├── empresa.py           # CRUD empresa
├── cliente.py           # CRUD cliente
├── vendedor.py          # CRUD vendedor
├── rol.py               # CRUD rol
├── ruta.py              # CRUD ruta
├── usuario.py           # Usuarios con roles (SPs)
├── rutarol.py           # Permisos ruta-rol (SPs)
└── factura.py           # Facturas maestro-detalle (SPs)

templates/
├── layout/
│   ├── base.html        # Layout Bootstrap 5 + sidebar + topbar + flashes
│   ├── nav_menu.html    # Menú lateral condicional (sólo rutas permitidas)
│   └── login_layout.html# Layout gradiente para login y recuperación
├── components/
│   ├── flash.html       # Macro para mensajes flash (borde 4px por estado)
│   ├── tabla_crud.html  # Macro de tabla CRUD estándar
│   ├── form_campo.html  # Macro de campo de formulario con label + error
│   └── confirm_modal.html
└── pages/
    ├── auth/            # login.html, cambiar_contrasena.html, recuperar_contrasena.html
    ├── home/            # index.html, acceso_denegado.html
    ├── producto/        # listar.html, formulario.html
    ├── persona/         # listar.html, formulario.html
    ├── empresa/         # listar.html, formulario.html
    ├── cliente/         # listar.html, formulario.html
    ├── vendedor/        # listar.html, formulario.html
    ├── rol/             # listar.html, formulario.html
    ├── ruta/            # listar.html, formulario.html
    ├── usuario/         # listar.html, formulario.html
    ├── rutarol/         # listar.html, formulario.html
    └── factura/         # listar.html, formulario.html, detalle.html

static/
├── css/
│   └── app.css          # Único CSS personalizado con :root Zenith
└── img/
    └── logo_zenith.svg

tests/
├── conftest.py          # Fixtures: client Flask, login helper, API base URL de pruebas
├── integration/
│   ├── test_auth.py
│   ├── test_rbac_middleware.py
│   ├── test_producto.py
│   ├── test_persona.py
│   ├── test_empresa.py
│   ├── test_cliente.py
│   ├── test_vendedor.py
│   ├── test_rol.py
│   ├── test_ruta.py
│   ├── test_usuario.py
│   ├── test_rutarol.py
│   └── test_factura.py
└── unit/
    └── test_validadores_contrasena.py

.env.example             # Plantilla de variables sensibles
requirements.txt         # Dependencias fijadas al stack aprobado por la constitución
README.md                # Overview del proyecto (ya existe parcialmente)
```

**Structure Decision**: Proyecto único (no web-app con backend+frontend) porque **el backend REST ya es un proyecto independiente** (`ApiGenericaCsharp`) y este repositorio contiene sólo el frontend Flask SSR. Se mantiene el layout plano que la Constitución prescribe (`routes/`, `templates/pages|layout|components`, `static/css/app.css` único), sin factoría `app/` anidada para preservar la simplicidad educativa.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No aplica — Constitution Check pasó sin violaciones.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (vacío)   | (vacío)    | (vacío)                             |

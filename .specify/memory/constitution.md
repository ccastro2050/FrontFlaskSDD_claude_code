<!--
SYNC IMPACT REPORT
==================
Version change: 0.0.0 (template) → 1.0.0 (initial ratification)
Bump rationale: MAJOR — first concrete adoption of the constitution replacing all placeholder tokens; establishes the full governance charter for FrontFlaskSDD.

Modified principles:
  - [PRINCIPLE_1_NAME] → I. Consumo Exclusivo de API REST (sin ORM)
  - [PRINCIPLE_2_NAME] → II. Arquitectura Blueprint + Servicios Genéricos
  - [PRINCIPLE_3_NAME] → III. Seguridad JWT + RBAC + Borrado Lógico
  - [PRINCIPLE_4_NAME] → IV. Identidad Visual Zenith (No Bootstrap por Defecto)
  - [PRINCIPLE_5_NAME] → V. Código en Español, Server-Side Rendering y Documentación Tutorial

Added sections:
  - Restricciones Técnicas y de Seguridad (Section 2)
  - Flujo de Desarrollo y Calidad (Section 3)

Removed sections: None (all template placeholders resolved).

Templates requiring updates:
  - ✅ .specify/templates/plan-template.md — Constitution Check gate references this constitution; no structural change required (placeholder gate remains compatible).
  - ✅ .specify/templates/spec-template.md — No mandatory new sections required; compatible as-is.
  - ✅ .specify/templates/tasks-template.md — Testing and structure guidance remains compatible; Blueprints + pytest map cleanly to existing phases.
  - ⚠ README.md / docs/quickstart.md — Not present or not reviewed; verify alignment manually if added.
  - ⚠ Manual_de_Marca_Zenith.md — Referenced from Principle IV; ensure the file exists in repo root.

Deferred items / TODOs:
  - TODO(RATIFICATION_DATE): Assumed today (2026-04-19) as the original ratification date since no prior constitution history was found. Adjust if an earlier adoption date applies.
-->

# FrontFlaskSDD Constitution

## Core Principles

### I. Consumo Exclusivo de API REST (sin ORM)

El frontend **NO DEBE** acceder directamente a base de datos ni usar ningún ORM. Toda lectura, escritura y ejecución de lógica persistente **DEBE** realizarse vía HTTP contra la API REST genérica en C# .NET 9 + Dapper (repositorio: `https://github.com/ccastro2050/ApiGenericaCsharp`), usando `requests` con JWT Bearer token. Las operaciones CRUD (listar, crear, actualizar, eliminar) **DEBEN** canalizarse por el servicio genérico `ApiService`; los stored procedures **DEBEN** invocarse mediante el método `ejecutar_sp` del mismo servicio. La API es agnóstica de motor (SQL Server, PostgreSQL, MySQL/MariaDB con el mismo código), y el frontend **NO DEBE** asumir ni codificar dependencias de un motor específico.

**Rationale**: Centralizar el acceso a datos en un único contrato HTTP elimina acoplamiento con el esquema, permite intercambiar motor de base de datos sin tocar el frontend, y mantiene una única superficie de autorización y auditoría.

### II. Arquitectura Blueprint + Servicios Genéricos

Cada módulo funcional del frontend **DEBE** implementarse como un Flask Blueprint independiente en su propio archivo bajo `routes/`. La lógica transversal **DEBE** centralizarse en: (a) `ApiService` para CRUD y stored procedures; (b) `AuthService` separado, con descubrimiento dinámico de PKs y FKs; (c) un middleware `@app.before_request` que verifica sesión y permisos; y (d) un context processor que inyecta `usuario`, `roles` y `rutas_permitidas` en todas las templates. Las templates **DEBEN** organizarse en `templates/pages/`, `templates/layout/` y `templates/components/`, con un único CSS personalizado en `static/css/app.css`. **NO DEBE** introducirse ningún framework JavaScript (React, Vue, etc.): todo el renderizado es server-side con Jinja2.

**Rationale**: La modularidad por Blueprint aísla responsabilidades, los servicios genéricos evitan duplicación de código HTTP/auth, y SSR mantiene el proyecto simple y coherente con su propósito educativo.

### III. Seguridad JWT + RBAC + Borrado Lógico

La autenticación **DEBE** basarse en JWT: el frontend obtiene el token desde la API y lo almacena en `session` de Flask, protegida por `secret_key`. El control de acceso **DEBE** ser RBAC: las rutas permitidas por rol se consultan a la BD (vía API) y se verifican en **cada** request mediante el middleware. Las contraseñas **DEBEN** encriptarse con BCrypt (gestionado por la API mediante `camposEncriptar`). Las rutas públicas son exclusivamente: `/login`, `/logout`, `/recuperar-contrasena`, `/static`. La recuperación de contraseña **DEBE** operar vía SMTP (Gmail) con contraseña temporal. Las facturas **NO DEBEN** eliminarse físicamente desde flujos de usuario: se anulan mediante borrado lógico con campo `estado` (`'activa'`/`'anulada'`). El `DELETE` físico **DEBE** restringirse al rol administrador.

**Rationale**: Separar autenticación (JWT) de autorización (RBAC) por ruta garantiza defensa en profundidad; el borrado lógico preserva auditabilidad fiscal y contable, un requisito no negociable para documentos financieros.

### IV. Identidad Visual Zenith (No Bootstrap por Defecto)

Toda superficie visual **DEBE** cumplir el `Manual_de_Marca_Zenith.md`. Los colores de marca — Azul Zenith `#0A2647` (primario: sidebar, encabezados de tabla, fondo login), Dorado Zenith `#E8AA2E` (secundario: botones primarios, hover de menú, links activos, focus de inputs) y Azul Medio `#144272` (acento: hover sidebar, bordes activos) — junto con tipografías (Inter para títulos/cuerpo; JetBrains Mono para códigos de producto, números de factura y precios), bordes y sombras, **DEBEN** declararse como CSS custom properties en `:root` dentro de `static/css/app.css`. Los colores por defecto de Bootstrap 5.3 **DEBEN** sobrescribirse con variables Zenith — **NO DEBE** usarse la paleta por defecto. Los iconos **DEBEN** ser Bootstrap Icons (`bi bi-*`) con el icono asignado por módulo según el manual. Los flash messages **DEBEN** renderizarse con borde izquierdo de 4px y color por estado (verde éxito, rojo error, ámbar advertencia, azul info). El login **DEBE** usar fondo gradiente `#0A2647 → #144272`, tarjeta blanca centrada y botón dorado al 100% de ancho.

**Rationale**: Una identidad visual consistente y centralizada en variables CSS evita drift de marca, simplifica cambios globales y diferencia el producto de un template Bootstrap genérico.

### V. Código en Español, Server-Side Rendering y Documentación Tutorial

Todo el código de aplicación **DEBE** usar español para nombres de variables, funciones, comentarios y mensajes flash, siguiendo `snake_case` para Python. La pila **DEBE** ser Python 3.12 + Flask 3.x + Jinja2 + Bootstrap 5.3, sin frameworks JS. Los tests **DEBEN** escribirse con `pytest`, ejecutarse como integración contra la API real (sin mocks), y cada Blueprint **DEBE** tener tests de sus rutas principales. Cada archivo Python **DEBE** incluir docstring inicial que explique qué hace y cómo se relaciona con otros archivos; los comentarios internos **DEBEN** ser extensos, tipo tutorial, dado el carácter educativo del proyecto. La documentación Markdown **DEBE** incluir diagramas Mermaid cuando represente flujos, relaciones o arquitectura.

**Rationale**: El idioma español alinea el código con el dominio y el público objetivo; los tests de integración reales evitan la falsa confianza de mocks divergentes; la documentación tutorial es parte del producto, no un accesorio.

## Restricciones Técnicas y de Seguridad

- **Stack fijo**: Python 3.12, Flask 3.x, Jinja2, Bootstrap 5.3, `requests`. Cualquier dependencia adicional **DEBE** justificarse por necesidad explícita y no duplicar capacidades ya cubiertas por `ApiService` o `AuthService`.
- **Sin ORM ni drivers de BD**: Queda prohibido importar SQLAlchemy, psycopg2, pymysql, pyodbc u otros clientes de base de datos en el frontend.
- **Sin frontend frameworks**: Queda prohibido React, Vue, Angular, Svelte, htmx (salvo aprobación explícita en amendment), Alpine.js y cualquier build step tipo Webpack/Vite para componentes dinámicos.
- **Rutas públicas cerradas**: El conjunto `/login`, `/logout`, `/recuperar-contrasena`, `/static` es exhaustivo. Cualquier ruta nueva pública **DEBE** registrarse explícitamente mediante amendment.
- **Tokens y secretos**: El JWT **NUNCA** debe exponerse en templates ni en logs; `SECRET_KEY`, credenciales SMTP y URL base de la API **DEBEN** cargarse desde variables de entorno, nunca hard-coded.
- **Borrado lógico**: Para entidades financieras (facturas y similares), la UI **NO DEBE** exponer acciones de borrado físico salvo a roles administradores explícitamente autorizados por la configuración RBAC.
- **Scripts de BD equivalentes**: La API mantiene 3 scripts de base de datos (`bdfacturas_sqlserver.sql`, `bdfacturas_postgres.sql`, `bdfacturas_mysql_mariadb.sql`) en la carpeta `script_bd/` del repositorio. Los tres **DEBEN** ser funcionalmente equivalentes: mismas tablas, mismos datos semilla, mismos 16 stored procedures (con nombres idénticos), mismos triggers. Cualquier cambio en la estructura de datos o en un SP **DEBE** replicarse en los 3 scripts para mantener la paridad multi-motor.

## Flujo de Desarrollo y Calidad

- **Estructura obligatoria**: `routes/` (un archivo por Blueprint), `templates/pages/`, `templates/layout/`, `templates/components/`, `static/css/app.css` (único), servicios compartidos en un módulo dedicado (`services/` o equivalente).
- **Revisión de cambios**: Todo cambio que toque `ApiService`, `AuthService`, el middleware `before_request` o `app.css` **DEBE** ser revisado por su impacto transversal (afecta a todos los módulos).
- **Pruebas antes del merge**: Cada Blueprint nuevo o modificado **DEBE** incluir o actualizar sus pytest de integración contra la API real. Un build sin cobertura de las rutas principales del Blueprint tocado **NO DEBE** mergearse.
- **Cumplimiento visual**: Cambios en UI **DEBEN** verificarse contra el `Manual_de_Marca_Zenith.md`; PRs que introduzcan colores literales fuera de `:root` o componentes Bootstrap sin tematizar **DEBEN** rechazarse.
- **Documentación viva**: Toda función o módulo nuevo llega con docstring; todo flujo no trivial llega con diagrama Mermaid en el Markdown correspondiente.
- **Complejidad justificada**: Desviaciones de estos principios (nueva dependencia pesada, ruta pública adicional, excepción al borrado lógico) **DEBEN** documentarse en la sección Complexity Tracking del plan y aprobarse explícitamente.

## Governance

Esta constitución prevalece sobre cualquier otra práctica, convención o preferencia individual dentro del proyecto FrontFlaskSDD. Toda enmienda **DEBE** (a) documentarse en un PR dedicado que modifique `.specify/memory/constitution.md`; (b) incluir justificación de por qué el principio o restricción cambia; (c) actualizar `CONSTITUTION_VERSION` según semver (MAJOR para remociones/redefiniciones incompatibles, MINOR para adiciones materiales, PATCH para aclaraciones o correcciones); y (d) propagar los cambios a las plantillas dependientes (`plan-template.md`, `spec-template.md`, `tasks-template.md`) y a cualquier documento guía afectado.

Todo PR y revisión **DEBE** verificar cumplimiento de los principios I–V antes de aprobar. La complejidad añadida **DEBE** justificarse explícitamente contra alternativas más simples; no basta con "conviene" o "queda más rápido". Para guía operativa de desarrollo en tiempo de ejecución, los agentes y contribuidores **DEBEN** remitirse a `CLAUDE.md` en la raíz del proyecto y al `Manual_de_Marca_Zenith.md` para decisiones visuales.

**Version**: 1.0.0 | **Ratified**: 2026-04-19 | **Last Amended**: 2026-04-19

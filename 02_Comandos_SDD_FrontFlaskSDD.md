# Comandos SDD para el Proyecto FrontFlaskSDD

> **Autor:** Carlos Arturo Castro Castro
> **Fecha:** Abril 2026
> **Proposito:** Prompts exactos para generar la documentacion SDD del proyecto FrontFlaskSDD.
> Cada prompt esta disenado para ejecutarse en multiples IAs y comparar resultados.

---

## Tabla de Contenidos

- [1. Que es un Desarrollador con IA](#1-que-es-un-desarrollador-con-ia)
- [2. Que hacer cuando el resultado NO cumple las expectativas](#2-que-hacer-cuando-el-resultado-no-cumple-las-expectativas)
- [3. Objetivo](#3-objetivo)
- [4. Contexto del Proyecto](#4-contexto-del-proyecto)
- [5. FASE 0: /constitution](#5-fase-0-constitution)
- [6. FASE 1: /specify](#6-fase-1-specify)
- [7. FASE 2: /clarify](#7-fase-2-clarify)
- [8. FASE 3: /plan](#8-fase-3-plan)
- [9. FASE 4: /tasks](#9-fase-4-tasks)
- [10. FASE 5: /analyze](#10-fase-5-analyze)
- [11. FASE 6: /checklist](#11-fase-6-checklist)
- [12. FASE 7: /implement](#12-fase-7-implement)
- [13. Tabla Resumen de Ejecucion](#13-tabla-resumen-de-ejecucion)
- [14. Protocolo de Comparacion entre IAs](#14-protocolo-de-comparacion-entre-ias)
- [15. Notas y Tips](#15-notas-y-tips)
- [16. Referencias](#16-referencias)

---

## 1. Que es un Desarrollador con IA

### El nuevo rol: de escribir codigo a supervisar agentes

El rol del desarrollador esta cambiando fundamentalmente. Segun [Fortune (2026)](https://fortune.com/2026/03/31/fortune-com-2026-03-26-ai-agents-vibe-coding-developer-skills-supervisor-class/), estamos ante el surgimiento de la **"Clase Supervisora"** — desarrolladores cuyo valor principal ya no es escribir codigo linea por linea, sino **orquestar agentes de IA, revisar sus resultados y tomar decisiones de diseno**.

> *"La IA produce volumen. Los humanos aseguran calidad."*
> — [DEV Community, AI-Assisted Development in 2026](https://dev.to/austinwdigital/ai-assisted-development-in-2026-best-practices-real-risks-and-the-new-bar-for-engineers-3fom)

### Antes vs Ahora

```mermaid
graph LR
    subgraph Antes["Desarrollador Tradicional"]
        direction TB
        AT1["Memorizar sintaxis"]
        AT2["Escribir cada linea de codigo"]
        AT3["Debuggear manualmente"]
        AT4["Documentar al final"]
    end

    subgraph Ahora["Desarrollador con IA"]
        direction TB
        AI1["Definir especificaciones claras"]
        AI2["Dirigir al agente con prompts precisos"]
        AI3["Revisar y corregir la salida de la IA"]
        AI4["Documentar ANTES de codificar (SDD)"]
    end

    style Antes fill:#94a3b8,stroke:#64748b,color:#fff
    style Ahora fill:#3b82f6,stroke:#1d4ed8,color:#fff
```

### Las 5 competencias del Desarrollador con IA

Segun multiples fuentes ([MindStudio](https://www.mindstudio.ai/blog/how-ai-is-changing-what-it-means-to-be-a-developer), [Pragmatic Engineer](https://newsletter.pragmaticengineer.com/p/ai-tooling-2026), [Shift Asia](https://shiftasia.com/column/ai-in-software-development-the-rise-of-the-ai-augmented-developer/)), el desarrollador con IA necesita 5 competencias clave:

| # | Competencia | Que significa | Ejemplo en SDD |
|---|-------------|--------------|-----------------|
| 1 | **Especificacion** | Saber definir QUE se quiere construir con precision, eliminando ambiguedad | Escribir el prompt de `/constitution` y `/specify` con el detalle suficiente para que la IA no invente |
| 2 | **Juicio critico** | Saber evaluar si la salida de la IA es correcta, no solo si "funciona" | Revisar el `spec.md` generado y detectar requisitos faltantes, contradicciones o suposiciones incorrectas |
| 3 | **Revision de codigo** | Tratar TODO el codigo generado por IA como "codigo de un junior sin revisar" | Leer el codigo de `/implement`, buscar bugs sutiles, problemas de seguridad, complejidad innecesaria |
| 4 | **Arquitectura** | Entender como se conectan las piezas de un sistema para tomar decisiones de diseno | Decidir que Flask use Blueprints, que el servicio sea generico, que el middleware use `before_request` |
| 5 | **Iteracion** | Saber refinar los prompts y documentos cuando el resultado no es satisfactorio | Re-ejecutar `/specify` con mas detalle cuando la spec generada omitio el RBAC |

### Que NO es un Desarrollador con IA

| Mito | Realidad |
|------|----------|
| "Solo copia/pega lo que dice la IA" | Revisa, cuestiona, corrige y mejora. La IA es el borrador, el humano es el editor |
| "No necesita saber programar" | Necesita entender el codigo para juzgar si es correcto. No necesita memorizarlo, pero si comprenderlo |
| "La IA reemplaza al desarrollador" | La IA reemplaza la parte mecanica (escribir sintaxis). El juicio, la arquitectura y la revision son humanos |
| "Es mas facil que desarrollar sin IA" | Es diferente. Escribir prompts precisos y revisar codigo generado requiere habilidades que antes no existian |

> *"Escribir codigo es barato. Pensar es caro."*
> — [DEV Community, 2026](https://dev.to/austinwdigital/ai-assisted-development-in-2026-best-practices-real-risks-and-the-new-bar-for-engineers-3fom)

### Gartner: el futuro es orquestar, no codificar

Segun [Gartner (citado por Shift Asia)](https://shiftasia.com/column/ai-in-software-development-the-rise-of-the-ai-augmented-developer/), para finales de 2026:

- **75% de los desarrolladores** orquestaran en vez de codificar
- **80% de las organizaciones** evolucionaran equipos grandes a equipos pequenos aumentados con IA
- Los desarrolladores estimaron que la IA asiste en el **42% del codigo** que hacen commit

Esto no significa menos trabajo — significa **trabajo diferente**: mas pensamiento critico, mas revision, mas diseno, menos tipeo.

---

## 2. Que hacer cuando el resultado NO cumple las expectativas

### El principio fundamental

> *"Cuando la salida de la IA no es correcta, no empiezas de cero. Retrocedes, mejoras la especificacion, y le pides al agente que regenere."*
> — [Hypergen, Spec Driven Development](https://www.hypergen.com.au/blog/spec-driven-development)

En SDD, la correccion siempre se hace **en la especificacion, no en el codigo**. Si el codigo generado es incorrecto, el problema esta en que la spec no fue lo suficientemente clara.

### El ciclo Generar → Evaluar → Refinar → Regenerar

```mermaid
graph TB
    GEN["1. GENERAR
    Ejecutar el comando
    (/constitution, /specify, /plan, etc.)"]
    EVAL["2. EVALUAR
    Revisar el documento generado
    con la checklist de la fase"]
    DEC{"3. DECIDIR
    Cumple con
    las expectativas?"}
    OK["4a. ACEPTAR
    Guardar y pasar
    a la siguiente fase"]
    REFINE["4b. REFINAR
    Identificar que falta,
    que sobra o que esta mal"]
    EDIT["5. CORREGIR
    Editar el prompt,
    editar el documento,
    o ambos"]
    REGEN["6. REGENERAR
    Re-ejecutar el comando
    con el prompt mejorado"]

    GEN --> EVAL --> DEC
    DEC -->|Si| OK
    DEC -->|No| REFINE
    REFINE --> EDIT --> REGEN
    REGEN --> EVAL

    style GEN fill:#3b82f6,stroke:#1d4ed8,color:#fff
    style EVAL fill:#f59e0b,stroke:#d97706,color:#fff
    style DEC fill:#8b5cf6,stroke:#6d28d9,color:#fff
    style OK fill:#22c55e,stroke:#16a34a,color:#fff
    style REFINE fill:#ef4444,stroke:#dc2626,color:#fff
    style EDIT fill:#ec4899,stroke:#db2777,color:#fff
    style REGEN fill:#06b6d4,stroke:#0891b2,color:#fff
```

### Estrategias de correccion por fase

Cada fase tiene formas especificas de corregir cuando el resultado no es satisfactorio:

#### FASE 0: /constitution — El resultado no refleja mis principios

| Problema | Estrategia de correccion |
|----------|--------------------------|
| La IA incluyo tecnologias que no pedi (ej: Django en vez de Flask) | **Editar directamente** el `constitution.md` y eliminar/cambiar la tecnologia incorrecta. No es necesario re-ejecutar el comando |
| Faltan principios que si mencionaste en el prompt | **Agregarlos manualmente** al archivo. La constitution es editable como cualquier Markdown |
| El documento es demasiado generico, sin los detalles especificos de tu proyecto | **Re-ejecutar** con un prompt mas especifico. Agregar ejemplos concretos: en vez de "usar Bootstrap", decir "usar Bootstrap 5.3 con layout sidebar y tabla responsive" |

#### FASE 1: /specify — La spec no cubre todas las funcionalidades

| Problema | Estrategia de correccion |
|----------|--------------------------|
| Faltan requisitos completos (ej: no menciono el RBAC) | **Re-ejecutar `/specify`** agregando al prompt las funcionalidades faltantes con mas detalle |
| Los requisitos son vagos (ej: "el usuario puede gestionar productos") | **Editar el spec.md** y reemplazar requisitos vagos por especificos: "El usuario puede listar productos en tabla, crear con formulario, editar y eliminar con confirmacion" |
| La IA invento funcionalidades que no pediste | **Eliminar** los requisitos inventados directamente del spec.md |
| Los flujos de usuario estan incompletos | **Agregar** los pasos faltantes manualmente o re-ejecutar `/clarify` para que la IA pregunte |

#### FASE 3: /plan — La arquitectura no coincide con lo esperado

| Problema | Estrategia de correccion |
|----------|--------------------------|
| La estructura de carpetas es diferente a la que quieres | **Editar el plan.md** con la estructura correcta. El plan es tu diseno, no el de la IA |
| Sugiere librerias que no quieres (ej: SQLAlchemy) | **Verificar la constitution.md** — si la regla "no ORM" esta ahi y la IA la ignoro, **reforzar** en el prompt: "Respetar estrictamente la constitution.md. No usar ORM bajo ninguna circunstancia" |
| Los componentes no tienen suficiente detalle | **Re-ejecutar `/plan`** agregando contexto al prompt: "El plan debe detallar los metodos de cada servicio y los endpoints que consume" |

#### FASE 4: /tasks — Las tareas estan desordenadas o faltan

| Problema | Estrategia de correccion |
|----------|--------------------------|
| El orden de dependencias es incorrecto | **Reordenar manualmente** en tasks.md. Tu conoces las dependencias mejor que la IA |
| Hay tareas demasiado grandes (ej: "Crear todos los CRUDs") | **Descomponer** la tarea grande en tareas pequenas: una por Blueprint |
| Faltan tareas para requisitos de la spec | **Ejecutar `/analyze`** para detectar gaps automaticamente |

#### FASE 7: /implement — El codigo generado tiene errores

| Problema | Estrategia de correccion |
|----------|--------------------------|
| El codigo no compila / no ejecuta | **Leer el error**, identificar la causa, y pedirle a la IA que corrija ESE error especifico (no re-generar todo) |
| El codigo funciona pero no sigue la constitution | **Senalar la violacion** a la IA: "El codigo usa Django pero la constitution dice Flask. Corregir" |
| El codigo es correcto pero demasiado complejo | **Pedir simplificacion**: "Simplificar este metodo. Eliminar abstracciones innecesarias" |
| El codigo tiene bugs sutiles (seguridad, logica) | **Este es TU trabajo como Desarrollador con IA.** La IA no detecta sus propios bugs. Tu debes revisarlo como "codigo de junior sin revisar" |

### Las 3 reglas de oro de la iteracion en SDD

```mermaid
graph LR
    R1["REGLA 1
    Corrige la spec,
    no el codigo
    ━━━
    Si el codigo es incorrecto,
    el problema esta en la spec.
    Mejora la spec y regenera."]

    R2["REGLA 2
    Nunca aceptes
    sin revisar
    ━━━
    Cada salida de la IA
    debe pasar por tu
    checklist de la fase."]

    R3["REGLA 3
    Iterar es barato,
    no iterar es caro
    ━━━
    Refinar y regenerar cuesta
    minutos. Un bug en produccion
    cuesta horas o dias."]

    style R1 fill:#3b82f6,stroke:#1d4ed8,color:#fff
    style R2 fill:#f59e0b,stroke:#d97706,color:#fff
    style R3 fill:#22c55e,stroke:#16a34a,color:#fff
```

### Ejemplo practico: la spec no incluyo el RBAC

**Situacion:** Ejecutaste `/specify` y el spec.md generado no menciona el control de acceso por roles.

**Paso 1 — Identificar el gap:**
> "El spec.md tiene requisitos de login pero no dice nada sobre middleware, rutas_permitidas ni roles."

**Paso 2 — Decidir la estrategia:**
> Opcion A: Editar spec.md manualmente y agregar los requisitos de RBAC.
> Opcion B: Re-ejecutar `/specify` con un prompt que enfatice el RBAC.

**Paso 3 — Ejecutar la correccion (Opcion B):**

```
/speckit-specify

(prompt anterior completo) +

IMPORTANTE — REQUISITOS DE RBAC QUE DEBEN INCLUIRSE:
- Middleware @app.before_request que intercepta CADA request
- Verifica sesion activa, permisos por ruta, cambio de contrasena forzado
- Las rutas permitidas se cargan al login via JOIN de 5 tablas
- El menu de navegacion solo muestra rutas permitidas para el rol del usuario
- Pagina 403 "Sin acceso" cuando el rol no tiene permiso
- Rutas publicas exentas: /login, /logout, /static, /recuperar-contrasena
```

**Paso 4 — Re-evaluar:**
> Abrir el nuevo spec.md y verificar con la checklist que ahora SI incluye RBAC.

**Paso 5 — Si sigue faltando:**
> Editarlo manualmente. Tu eres el dueno del spec, no la IA.

---

## 3. Objetivo del documento

Ejecutar las 7 fases de SDD (Spec-Driven Development) con GitHub Spec Kit sobre el proyecto **FrontFlaskSDD**: un frontend web en Flask que consume una API REST generica en C#.

El mismo conjunto de prompts se ejecutara en multiples IAs para comparar la calidad de la documentacion generada.

| IA | Herramienta | Modo |
|----|-------------|------|
| Claude Code | CLI / VS Code | Slash commands `/speckit-*` |
| GitHub Copilot | VS Code Chat | Slash commands `/specify`, `/plan`, `/tasks` |
| Gemini CLI | Terminal | Slash commands |
| Cursor | IDE | Chat con contexto |

```mermaid
graph LR
    PROMPTS["Mismos prompts
    (este documento)"]

    PROMPTS --> C["Claude Code"]
    PROMPTS --> CO["GitHub Copilot"]
    PROMPTS --> G["Gemini CLI"]
    PROMPTS --> CU["Cursor"]

    C --> RC["Resultado Claude"]
    CO --> RCO["Resultado Copilot"]
    G --> RG["Resultado Gemini"]
    CU --> RCU["Resultado Cursor"]

    RC --> COMP["Comparativa
    03_Comparativa_IAs.md"]
    RCO --> COMP
    RG --> COMP
    RCU --> COMP

    style PROMPTS fill:#8b5cf6,stroke:#6d28d9,color:#fff
    style COMP fill:#22c55e,stroke:#16a34a,color:#fff
```

---

## 2. Contexto del Proyecto

### Descripcion general

**FrontFlaskSDD** es un frontend web construido con Flask (Python) que consume una API REST generica en C# (.NET 9). La API permite operaciones CRUD sobre cualquier tabla de base de datos y ejecucion de stored procedures. El frontend implementa autenticacion JWT, control de acceso por roles (RBAC) y gestion de facturas maestro-detalle.

> **Repositorio de la API:** [https://github.com/ccastro2050/ApiGenericaCsharp](https://github.com/ccastro2050/ApiGenericaCsharp)
> **Repositorio de este proyecto SDD:** [https://github.com/ccastro2050/FrontFlaskSDD](https://github.com/ccastro2050/FrontFlaskSDD)

### Arquitectura

```mermaid
graph TB
    subgraph Frontend["Frontend Flask (Python)"]
        direction TB
        APP["app.py
        Punto de entrada"]
        MW["middleware/
        auth_middleware.py
        Verifica sesion + RBAC"]
        ROUTES["routes/
        12 Blueprints
        auth, home, producto,
        persona, usuario, cliente,
        empresa, rol, ruta,
        vendedor, factura"]
        SERVICES["services/
        api_service.py (CRUD generico)
        auth_service.py (login, roles, rutas)
        email_service.py (SMTP)"]
        TEMPLATES["templates/
        layout/base.html
        components/nav_menu.html
        pages/ (14 paginas HTML)"]
        STATIC["static/
        css/app.css"]

        APP --> MW --> ROUTES
        ROUTES --> SERVICES
        ROUTES --> TEMPLATES
    end

    subgraph API["API Generica C# (.NET 9)"]
        direction TB
        CTRL["Controllers
        Entidades, Consultas,
        Procedimientos, Autenticacion,
        Diagnostico, Estructuras"]
        SVC["Servicios
        ServicioCrud
        ServicioConsultas"]
        REPO["Repositorios
        SQL Server | Postgres | MariaDB"]
    end

    subgraph BD["Base de Datos"]
        TABLES["12 tablas
        6 triggers
        15 stored procedures"]
    end

    Frontend -->|HTTP + JWT| API
    API -->|ADO.NET + Dapper| BD

    style Frontend fill:#3b82f6,stroke:#1d4ed8,color:#fff
    style API fill:#10b981,stroke:#059669,color:#fff
    style BD fill:#f59e0b,stroke:#d97706,color:#fff
```

### Stack tecnologico

| Capa | Tecnologia |
|------|-----------|
| Frontend | Python 3.12, Flask 3.x, Jinja2, Bootstrap 5 |
| Comunicacion | HTTP REST + JWT Bearer |
| Backend (API) | C# .NET 9, ASP.NET Core, Dapper |
| Bases de datos | SQL Server, PostgreSQL, MySQL/MariaDB |
| Autenticacion | JWT + BCrypt |
| Email | SMTP (Gmail) con contrasena de aplicacion |

### Modulos del frontend

| Blueprint | Ruta | Tipo | Descripcion |
|-----------|------|------|-------------|
| `auth` | `/login`, `/logout`, `/cambiar-contrasena`, `/recuperar-contrasena` | Autenticacion | Login JWT, cambio y recuperacion de contrasena |
| `home` | `/` | Dashboard | Pagina principal |
| `producto` | `/producto` | CRUD simple | Codigo, nombre, stock, valor unitario |
| `persona` | `/persona` | CRUD simple | Codigo, nombre, email, telefono |
| `empresa` | `/empresa` | CRUD simple | Codigo, nombre |
| `cliente` | `/cliente` | CRUD simple | Id, credito, FK persona, FK empresa |
| `vendedor` | `/vendedor` | CRUD simple | Id, carnet, direccion, FK persona |
| `rol` | `/rol` | CRUD simple | Id, nombre |
| `ruta` | `/ruta` | CRUD simple | Id, ruta, descripcion |
| `usuario` | `/usuario` | CRUD + SP | Email (PK), contrasena. Gestion de roles via SP |
| `factura` | `/factura` | Maestro-detalle via SP | Crear/consultar/listar/actualizar/eliminar facturas con productos |

### Base de datos

**12 tablas:**

```
empresa, persona, producto, rol, ruta, usuario,
cliente, vendedor, factura, productosporfactura,
rol_usuario, rutarol
```

**15 stored procedures:**

| Grupo | SPs |
|-------|-----|
| Facturas (5) | `sp_insertar_factura_y_productosporfactura`, `sp_consultar_factura_y_productosporfactura`, `sp_listar_facturas_y_productosporfactura`, `sp_actualizar_factura_y_productosporfactura`, `sp_borrar_factura_y_productosporfactura` |
| Usuarios (6) | `crear_usuario_con_roles`, `actualizar_usuario_con_roles`, `eliminar_usuario_con_roles`, `actualizar_roles_usuario`, `consultar_usuario_con_roles`, `listar_usuarios_con_roles` |
| Permisos (4) | `verificar_acceso_ruta`, `listar_rutarol`, `crear_rutarol`, `eliminar_rutarol` |

### Diagrama Entidad-Relacion

```mermaid
erDiagram
    empresa ||--o{ cliente : "fkcodempresa"
    persona ||--o{ cliente : "fkcodpersona"
    persona ||--o{ vendedor : "fkcodpersona"
    cliente ||--o{ factura : "fkidcliente"
    vendedor ||--o{ factura : "fkidvendedor"
    factura ||--o{ productosporfactura : "fknumfactura"
    producto ||--o{ productosporfactura : "fkcodproducto"
    usuario ||--o{ rol_usuario : "fkemail"
    rol ||--o{ rol_usuario : "fkidrol"
    rol ||--o{ rutarol : "fkidrol"
    ruta ||--o{ rutarol : "fkidruta"

    empresa {
        varchar codigo PK
        varchar nombre
    }
    persona {
        varchar codigo PK
        varchar nombre
        varchar email
        varchar telefono
    }
    producto {
        varchar codigo PK
        varchar nombre
        int stock
        decimal valorunitario
    }
    usuario {
        varchar email PK
        varchar contrasena
    }
    rol {
        int id PK
        varchar nombre
    }
    ruta {
        int id PK
        varchar ruta
        varchar descripcion
    }
    cliente {
        int id PK
        decimal credito
        varchar fkcodpersona FK
        varchar fkcodempresa FK
    }
    vendedor {
        int id PK
        int carnet
        varchar direccion
        varchar fkcodpersona FK
    }
    factura {
        int numero PK
        timestamp fecha
        decimal total
        int fkidcliente FK
        int fkidvendedor FK
    }
    productosporfactura {
        int fknumfactura PK,FK
        varchar fkcodproducto PK,FK
        int cantidad
        decimal subtotal
    }
    rol_usuario {
        varchar fkemail PK,FK
        int fkidrol PK,FK
    }
    rutarol {
        int fkidruta PK,FK
        int fkidrol PK,FK
    }
```

---

## 3. FASE 0: /constitution

> **Comando:** `/speckit-constitution` (Claude Code) o `/constitution` (Copilot/Gemini)
> **Archivo que genera:** `memory/constitution.md`
> **Proposito:** Establecer los principios inmutables que todos los demas comandos deben respetar.

### Prompt exacto

```
/constitution

El proyecto FrontFlaskSDD es un frontend web que consume una API REST generica en C#.
Repositorio de la API: https://github.com/ccastro2050/ApiGenericaCsharp

PRINCIPIOS DE TECNOLOGIA:
- Python 3.12 con Flask 3.x como framework web
- Templates con Jinja2 y Bootstrap 5.3
- NO usar ORM ni acceso directo a base de datos. Todo se consume via API REST
- La API REST esta en C# .NET 9 con Dapper (no Entity Framework)
- Comunicacion frontend-API mediante HTTP (requests) + JWT Bearer token
- La API soporta SQL Server, PostgreSQL y MySQL/MariaDB con el mismo codigo

PRINCIPIOS DE ARQUITECTURA:
- Patron Blueprint: cada modulo del frontend es un Blueprint independiente de Flask
- Servicio generico centralizado (ApiService) para operaciones CRUD (listar, crear, actualizar, eliminar)
- Servicio generico centralizado para ejecucion de stored procedures (ejecutar_sp)
- Servicio de autenticacion separado (AuthService) con descubrimiento dinamico de PKs y FKs
- Middleware de autenticacion con @app.before_request que verifica sesion y permisos
- Context processor para inyectar variables de sesion (usuario, roles, rutas_permitidas) en todas las templates

PRINCIPIOS DE SEGURIDAD:
- Autenticacion JWT: el frontend obtiene token de la API y lo almacena en session de Flask
- Control de acceso RBAC: las rutas permitidas por rol se consultan a la BD y se verifican en cada request
- Contrasenas encriptadas con BCrypt (la API lo maneja via parametro camposEncriptar)
- Secret key de Flask para encriptar cookies de sesion
- Rutas publicas: /login, /logout, /recuperar-contrasena, /static
- Recuperacion de contrasena via SMTP (Gmail) con contrasena temporal

PRINCIPIOS DE CODIGO:
- Archivos en espanol (nombres de variables, comentarios, mensajes flash)
- snake_case para variables y funciones Python
- Cada Blueprint en su propio archivo dentro de routes/
- Templates organizadas en templates/pages/, templates/layout/, templates/components/
- Un solo archivo CSS personalizado en static/css/app.css
- No usar JavaScript frameworks (React, Vue, etc). Solo Jinja2 server-side rendering
- Los stored procedures se llaman via el metodo ejecutar_sp del ApiService

PRINCIPIOS DE TESTING:
- Tests con pytest
- Tests de integracion contra la API real (no mocks)
- Cada Blueprint debe tener tests de sus rutas principales

PRINCIPIOS DE DOCUMENTACION:
- Docstrings en cada archivo Python explicando que hace y como se relaciona con otros archivos
- Comentarios extensos tipo tutorial (el proyecto es educativo)
- Diagramas Mermaid en documentacion Markdown
```

### Explicacion de cada principio

| Principio | Por que se incluye |
|-----------|-------------------|
| Flask + Jinja2 + Bootstrap | Evita que la IA sugiera React, Vue, Django o FastAPI |
| No ORM, todo via API REST | Evita que genere modelos SQLAlchemy o acceso directo a BD |
| Blueprint por modulo | Define la estructura de carpetas que debe respetar |
| Servicio generico centralizado | Evita que cree clientes HTTP diferentes en cada Blueprint |
| Middleware con before_request | Define COMO se implementa la seguridad (no con decoradores por ruta) |
| BCrypt via API (camposEncriptar) | Aclara que el frontend NO encripta, delega a la API |
| Espanol en codigo | Evita que genere variables en ingles |
| No JavaScript frameworks | Evita que sugiera SPA o frontend separado |
| Tests contra API real | Evita mocks que no reflejan el comportamiento real |
| Estilo tutorial | El codigo es educativo, los comentarios son extensos a proposito |

---

## 4. FASE 1: /specify

> **Comando:** `/speckit-specify` (Claude Code) o `/specify` (Copilot/Gemini)
> **Archivo que genera:** `spec.md`
> **Proposito:** Definir QUE se va a construir con requisitos formales, flujos de usuario y criterios de aceptacion.

### Prompt exacto

```
/specify

El proyecto FrontFlaskSDD es un frontend Flask que consume la API REST generica ApiGenericaCsharp.
Repositorio de la API: https://github.com/ccastro2050/ApiGenericaCsharp

FUNCIONALIDADES DEL SISTEMA:

1. AUTENTICACION Y SEGURIDAD
   - Login con email y contrasena (POST a /api/autenticacion/token)
   - La API valida credenciales con BCrypt y retorna JWT
   - Almacenar token JWT en session de Flask
   - Logout (limpiar sesion)
   - Cambiar contrasena (verificar actual, validar nueva, encriptar con BCrypt via API)
   - Recuperar contrasena olvidada (generar temporal, enviar por SMTP Gmail, forzar cambio al login)
   - Validacion de contrasena: minimo 6 caracteres, 1 mayuscula, 1 numero, no trivial

2. CONTROL DE ACCESO RBAC
   - Al hacer login, consultar roles del usuario (tabla rol_usuario → rol)
   - Al hacer login, consultar rutas permitidas por rol (tabla rutarol → ruta)
   - Middleware @app.before_request verifica en cada request:
     a) Si es ruta publica (/login, /static) → dejar pasar
     b) Si no hay sesion → redirigir a /login
     c) Si debe cambiar contrasena → redirigir a /cambiar-contrasena
     d) Si la ruta no esta en rutas_permitidas → mostrar pagina 403
   - Menu de navegacion dinamico: solo muestra las rutas permitidas para el usuario
   - La consulta de roles y rutas se hace con UNA sola consulta SQL via ConsultasController
     (JOIN de 5 tablas: usuario → rol_usuario → rol → rutarol → ruta)
   - Fallback: si ConsultasController falla, usar 5 GETs separados al CRUD generico

3. CRUDS SIMPLES (7 modulos)
   Cada modulo tiene: listado con tabla, formulario crear, formulario editar, eliminar con confirmacion.
   Todos usan el ApiService generico (mismos 4 metodos: listar, crear, actualizar, eliminar).
   - Producto: codigo (PK), nombre, stock, valorunitario
   - Persona: codigo (PK), nombre, email, telefono
   - Empresa: codigo (PK), nombre
   - Cliente: id (PK auto), credito, fkcodpersona (FK→persona), fkcodempresa (FK→empresa)
   - Vendedor: id (PK auto), carnet, direccion, fkcodpersona (FK→persona)
   - Rol: id (PK auto), nombre
   - Ruta: id (PK auto), ruta, descripcion

4. GESTION DE USUARIOS CON ROLES (via Stored Procedures)
   - Listar usuarios con sus roles (SP: listar_usuarios_con_roles)
   - Crear usuario con roles (SP: crear_usuario_con_roles) - contrasena se encripta con BCrypt
   - Actualizar usuario con roles (SP: actualizar_usuario_con_roles)
   - Eliminar usuario con roles (SP: eliminar_usuario_con_roles)
   - Consultar un usuario con roles (SP: consultar_usuario_con_roles)
   - Actualizar solo roles sin tocar contrasena (SP: actualizar_roles_usuario)

5. GESTION DE PERMISOS RBAC (via Stored Procedures)
   - Listar permisos ruta-rol (SP: listar_rutarol)
   - Crear permiso ruta-rol (SP: crear_rutarol)
   - Eliminar permiso ruta-rol (SP: eliminar_rutarol)
   - Verificar acceso de usuario a ruta (SP: verificar_acceso_ruta)

6. FACTURAS MAESTRO-DETALLE (via Stored Procedures)
   - Listar todas las facturas con productos, cliente y vendedor (SP: sp_listar_facturas_y_productosporfactura)
   - Consultar una factura con detalle (SP: sp_consultar_factura_y_productosporfactura)
   - Crear factura: seleccionar cliente, vendedor, agregar N productos con cantidad (SP: sp_insertar_factura_y_productosporfactura)
   - Actualizar factura: cambiar cliente/vendedor, reemplazar productos (SP: sp_actualizar_factura_y_productosporfactura)
   - Eliminar factura con cascada (SP: sp_borrar_factura_y_productosporfactura)
   - Los triggers de la BD calculan subtotales, totales y ajustan stock automaticamente

7. LAYOUT Y NAVEGACION
   - Template base (base.html) con Bootstrap 5 sidebar layout
   - Barra superior con nombre de usuario y boton logout
   - Menu lateral (nav_menu.html) con links condicionales segun rutas_permitidas
   - Sistema de mensajes flash (alertas Bootstrap dismissible)
   - CSS personalizado en static/css/app.css

FLUJOS DE USUARIO CRITICOS:
- Login → cargar roles/rutas → redirigir a home
- Crear factura → seleccionar cliente y vendedor → agregar productos → enviar SP
- Recuperar contrasena → generar temporal → enviar email SMTP → forzar cambio al login
- Navegacion RBAC → middleware verifica permisos → mostrar/ocultar menu segun rol
```

### Desglose del prompt por seccion

| Seccion | Que cubre | Por que es importante |
|---------|-----------|----------------------|
| Autenticacion | Login, logout, cambio, recuperacion | Es el flujo mas complejo del frontend |
| RBAC | Roles, rutas, middleware, menu dinamico | Define la seguridad de toda la app |
| CRUDs simples | 7 modulos identicos con CRUD generico | Son el 70% del proyecto pero el patron es el mismo |
| Usuarios con roles | 6 SPs de usuario | Mezcla CRUD + stored procedures |
| Permisos | 4 SPs de rutarol | Administracion del RBAC |
| Facturas | 5 SPs maestro-detalle | El modulo mas complejo (formulario dinamico) |
| Layout | Templates, menu, flash | Estructura visual compartida |

---

## 5. FASE 2: /clarify

> **Comando:** `/speckit-clarify` (Claude Code) o `/clarify` (Copilot/Gemini)
> **Archivo que modifica:** `spec.md`
> **Proposito:** Identificar ambiguedades y resolverlas antes de planificar.

### Prompt exacto

```
/clarify
```

(No necesita prompt adicional — el agente lee `spec.md` y genera preguntas)

### Preguntas anticipadas y respuestas preparadas

La IA probablemente preguntara sobre estos puntos ambiguos. Estas son las respuestas correctas basadas en el proyecto real:

| Pregunta probable | Respuesta |
|-------------------|-----------|
| *"La encriptacion BCrypt se hace en el frontend Flask o en la API C#?"* | En la API C#. El frontend envia la contrasena en texto plano, la API la encripta con BCrypt via el parametro `?camposEncriptar=contrasena` en el query string del PUT. |
| *"El descubrimiento de PKs y FKs es dinamico o hardcodeado?"* | Dinamico. AuthService consulta `GET /api/estructuras/{tabla}/modelo` para descubrir PKs y FKs. Los resultados se cachean en memoria (`_fk_cache`). |
| *"La consulta de roles y rutas usa ConsultasController o el CRUD generico?"* | Primero intenta ConsultasController (1 sola consulta SQL con JOINs). Si falla, usa fallback con 5 GETs separados al CRUD generico. |
| *"El menu de navegacion se genera en cada request o se cachea?"* | Se cachea en la sesion de Flask al momento del login. Las rutas_permitidas se guardan en `session["rutas_permitidas"]` y el context_processor las inyecta en todas las templates. |
| *"Las facturas se crean desde un formulario con productos dinamicos. Como se manejan los N productos?"* | Con campos HTML de nombre `prod_codigo[]` y `prod_cantidad[]`. Flask los recoge con `request.form.getlist()`. Se construye un JSON array y se pasa al SP como parametro `p_productos`. |
| *"La recuperacion de contrasena usa un link de reset o una contrasena temporal?"* | Contrasena temporal. Se genera un string aleatorio de 8 caracteres (1 mayuscula, 1 minuscula, 1 numero + 5 random), se guarda en la BD encriptada con BCrypt, se envia por SMTP y se fuerza el cambio al siguiente login. |
| *"El frontend maneja multiples bases de datos o solo una?"* | Solo una. El frontend no sabe cual BD usa la API. La API cambia de motor con `DatabaseProvider` en `appsettings.json`. El frontend es identico para SQL Server, Postgres o MariaDB. |

---

## 6. FASE 3: /plan

> **Comando:** `/speckit-plan` (Claude Code) o `/plan` (Copilot/Gemini)
> **Archivo que genera:** `plan.md`
> **Proposito:** Definir COMO se construira el proyecto (arquitectura, componentes, dependencias).

### Prompt exacto

```
/plan
```

(No necesita prompt adicional — el agente lee `constitution.md` y `spec.md`)

### Arquitectura de carpetas esperada

El plan generado deberia reflejar esta estructura:

```
FrontFlaskSDD/
├── app.py                          # Punto de entrada Flask
├── config.py                       # Variables de configuracion (API URL, SMTP, secret key)
├── requirements.txt                # Dependencias Python
├── middleware/
│   └── auth_middleware.py          # @app.before_request + context_processor
├── services/
│   ├── __init__.py
│   ├── api_service.py              # CRUD generico + ejecutar_sp
│   ├── auth_service.py             # Login, roles, rutas, cambiar contrasena
│   └── email_service.py            # SMTP para contrasena temporal
├── routes/
│   ├── __init__.py
│   ├── auth.py                     # /login, /logout, /cambiar, /recuperar
│   ├── home.py                     # /
│   ├── producto.py                 # /producto (CRUD)
│   ├── persona.py                  # /persona (CRUD)
│   ├── empresa.py                  # /empresa (CRUD)
│   ├── cliente.py                  # /cliente (CRUD)
│   ├── vendedor.py                 # /vendedor (CRUD)
│   ├── rol.py                      # /rol (CRUD)
│   ├── ruta.py                     # /ruta (CRUD)
│   ├── usuario.py                  # /usuario (CRUD + SPs)
│   └── factura.py                  # /factura (maestro-detalle SPs)
├── templates/
│   ├── layout/
│   │   └── base.html               # Layout Bootstrap con sidebar
│   ├── components/
│   │   └── nav_menu.html           # Menu lateral dinamico por RBAC
│   └── pages/
│       ├── login.html
│       ├── home.html
│       ├── producto.html
│       ├── persona.html
│       ├── empresa.html
│       ├── cliente.html
│       ├── vendedor.html
│       ├── rol.html
│       ├── ruta.html
│       ├── usuario.html
│       ├── factura.html
│       ├── cambiar_contrasena.html
│       ├── recuperar_contrasena.html
│       └── sin_acceso.html
├── static/
│   └── css/
│       └── app.css                 # Estilos personalizados
└── tests/
    ├── test_auth.py
    ├── test_crud.py
    └── test_factura.py
```

---

## 7. FASE 4: /tasks

> **Comando:** `/speckit-tasks` (Claude Code) o `/tasks` (Copilot/Gemini)
> **Archivo que genera:** `tasks.md`
> **Proposito:** Descomponer el plan en tareas concretas, ordenadas por dependencia.

### Prompt exacto

```
/tasks
```

(No necesita prompt adicional — el agente lee `spec.md` y `plan.md`)

### Orden esperado de tareas

Las tareas deberian seguir este orden logico de dependencias:

```mermaid
graph TB
    T1["Task 1: Crear estructura
    del proyecto Flask"]
    T2["Task 2: config.py
    API URL, SMTP, secret key"]
    T3["Task 3: requirements.txt
    flask, requests, pytest"]
    T4["Task 4: ApiService
    listar, crear, actualizar,
    eliminar, ejecutar_sp"]
    T5["Task 5: Layout base.html
    Bootstrap sidebar"]
    T6["Task 6: AuthService
    login, roles, rutas"]
    T7["Task 7: Middleware
    before_request + context_processor"]
    T8["Task 8: Blueprint auth
    login, logout, cambiar, recuperar"]
    T9["Task 9: email_service
    SMTP contrasena temporal"]
    T10["Task 10: nav_menu.html
    Menu dinamico RBAC"]
    T11["Task 11: Blueprint home
    Dashboard"]
    T12["Task 12-18: CRUDs simples
    producto, persona, empresa,
    cliente, vendedor, rol, ruta"]
    T19["Task 19: Blueprint usuario
    CRUD + SPs de roles"]
    T20["Task 20: Blueprint factura
    Maestro-detalle con SPs"]
    T21["Task 21: Tests"]

    T1 --> T2 --> T3 --> T4
    T4 --> T5
    T4 --> T6
    T5 --> T7
    T6 --> T7
    T7 --> T8
    T8 --> T9
    T7 --> T10
    T10 --> T11
    T11 --> T12
    T12 --> T19
    T19 --> T20
    T20 --> T21

    style T1 fill:#3b82f6,stroke:#1d4ed8,color:#fff
    style T4 fill:#10b981,stroke:#059669,color:#fff
    style T7 fill:#f59e0b,stroke:#d97706,color:#fff
    style T20 fill:#ef4444,stroke:#dc2626,color:#fff
    style T21 fill:#8b5cf6,stroke:#6d28d9,color:#fff
```

---

## 8. FASE 5: /analyze

> **Comando:** `/speckit-analyze` (Claude Code) o `/analyze` (Copilot/Gemini)
> **Archivo que genera:** Reporte en pantalla
> **Proposito:** Validar consistencia entre constitution, spec, plan y tasks.

### Prompt exacto

```
/analyze
```

### Que validaciones esperar

| Validacion | Que revisa |
|------------|-----------|
| Constitution vs Spec | Que la spec respete las tecnologias y patrones definidos |
| Spec vs Plan | Que cada requisito funcional tenga componentes en el plan |
| Plan vs Tasks | Que cada componente del plan tenga tareas asignadas |
| Tasks vs Constitution | Que ninguna tarea viole los principios inmutables |
| Completitud | Que no haya requisitos sin tareas ni tareas sin requisitos |
| Dependencias | Que el orden de tareas respete las dependencias |

---

## 9. FASE 6: /checklist

> **Comando:** `/speckit-checklist` (Claude Code) o `/checklist` (Copilot/Gemini)
> **Archivo que genera:** Checklist integrada en los artefactos
> **Proposito:** Criterios de aceptacion para verificar que cada requisito se cumplio.

### Prompt exacto

```
/checklist
```

### Criterios de aceptacion esperados por modulo

| Modulo | Criterios clave |
|--------|----------------|
| **Login** | Acepta email+contrasena, retorna JWT, almacena en sesion, redirige a home |
| **RBAC** | Middleware bloquea rutas no permitidas, menu se adapta a roles, pagina 403 funciona |
| **CRUD producto** | Listar, crear, editar, eliminar. Formulario valida campos requeridos |
| **CRUD cliente** | Muestra nombre de persona y empresa (no solo FKs). Dropdown con FK |
| **Usuario + roles** | Crear con roles, editar roles, eliminar con roles. BCrypt via API |
| **Factura** | Crear con N productos, calcular totales (trigger), editar productos, eliminar cascada |
| **Recuperar contrasena** | Genera temporal, envia SMTP, fuerza cambio al login |
| **Layout** | Sidebar responsive, flash messages, boton logout visible |

---

## 10. FASE 7: /implement

> **Comando:** `/speckit-implement` (Claude Code) o `/implement` (Copilot/Gemini)
> **Archivo que genera:** Codigo fuente del proyecto
> **Proposito:** Generar el codigo tarea por tarea.

### Prompt exacto

```
/implement
```

### Estrategia de ejecucion por fases

No ejecutar todo de golpe. Dividir en 4 rondas con revision entre cada una:

| Ronda | Tareas | Que se genera | Punto de revision |
|-------|--------|---------------|-------------------|
| **Ronda 1: Cimientos** | Tasks 1-5 | Estructura, config, ApiService, layout | Verificar que `api_service.py` se conecta a la API |
| **Ronda 2: Seguridad** | Tasks 6-11 | AuthService, middleware, login, menu | Verificar login funcional con JWT y RBAC |
| **Ronda 3: CRUDs** | Tasks 12-18 | 7 Blueprints CRUD | Verificar que cada CRUD lista, crea, edita, elimina |
| **Ronda 4: Avanzado** | Tasks 19-21 | Usuario+roles, factura, tests | Verificar SPs y maestro-detalle |

### Prompt para cada ronda

**Ronda 1:**
```
/implement

Ejecutar solamente las tareas 1 a 5 (estructura, config, ApiService, layout base).
Detenerse despues de completarlas para revision.
```

**Ronda 2:**
```
/implement

Continuar con las tareas 6 a 11 (AuthService, middleware, login, email, menu, home).
Detenerse despues para verificar que el login funciona.
```

**Ronda 3:**
```
/implement

Continuar con las tareas 12 a 18 (CRUDs simples: producto, persona, empresa, cliente, vendedor, rol, ruta).
Detenerse despues para verificar que todos los CRUDs funcionan.
```

**Ronda 4:**
```
/implement

Continuar con las tareas 19 a 21 (usuario con roles via SPs, factura maestro-detalle via SPs, tests).
```

---

## 11. Tabla Resumen de Ejecucion

| # | Fase | Comando | Archivo generado | Entrada requerida |
|---|------|---------|-----------------|-------------------|
| 0 | Constitution | `/constitution` | `constitution.md` | Prompt con principios del proyecto |
| 1 | Specify | `/specify` | `spec.md` | Prompt con funcionalidades completas |
| 2 | Clarify | `/clarify` | Actualiza `spec.md` | Responder preguntas de la IA |
| 3 | Plan | `/plan` | `plan.md` | Automatico (lee constitution + spec) |
| 4 | Tasks | `/tasks` | `tasks.md` | Automatico (lee spec + plan) |
| 5 | Analyze | `/analyze` | Reporte en pantalla | Automatico (lee todo) |
| 6 | Checklist | `/checklist` | Checklist en artefactos | Automatico (lee spec + tasks) |
| 7 | Implement | `/implement` | Codigo fuente | Automatico o por rondas |

---

## 12. Protocolo de Comparacion entre IAs

### Que evaluar

Despues de ejecutar las 7 fases en cada IA, evaluar con esta rubrica:

| Criterio | Descripcion | Peso |
|----------|-------------|------|
| **Completitud** | Cubrio todos los requisitos del prompt? | 25% |
| **Adherencia a constitution** | Respeto tecnologias, patrones, convenciones? | 20% |
| **Calidad de la spec** | Requisitos claros, criterios de aceptacion, flujos de usuario? | 15% |
| **Calidad del plan** | Arquitectura coherente, dependencias correctas? | 15% |
| **Calidad de las tasks** | Orden logico, tareas aisladas, dependencias marcadas? | 10% |
| **Codigo funcional** | El codigo generado compila/ejecuta sin errores? | 10% |
| **Estilo educativo** | Comentarios claros, docstrings, estilo tutorial? | 5% |

### Rubrica de puntuacion (1-5)

| Puntaje | Significado |
|---------|-------------|
| 5 | Excelente — supera expectativas |
| 4 | Bueno — cumple sin errores significativos |
| 3 | Aceptable — cumple parcialmente, requiere ajustes |
| 2 | Deficiente — omisiones importantes |
| 1 | Inaceptable — no sirve |

### Tabla de resultados (llenar despues de ejecutar)

| Criterio | Claude Code | GitHub Copilot | Gemini CLI | Cursor |
|----------|:-----------:|:--------------:|:----------:|:------:|
| Completitud | /5 | /5 | /5 | /5 |
| Adherencia a constitution | /5 | /5 | /5 | /5 |
| Calidad de la spec | /5 | /5 | /5 | /5 |
| Calidad del plan | /5 | /5 | /5 | /5 |
| Calidad de las tasks | /5 | /5 | /5 | /5 |
| Codigo funcional | /5 | /5 | /5 | /5 |
| Estilo educativo | /5 | /5 | /5 | /5 |
| **TOTAL PONDERADO** | **/5** | **/5** | **/5** | **/5** |

---

## 13. Notas y Tips

### Tips por IA

| IA | Tip |
|----|-----|
| **Claude Code** | Los comandos son `/speckit-constitution`, `/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`. Tiene buena adherencia a constitution |
| **GitHub Copilot** | Los comandos son `/constitution`, `/specify`, `/plan`, `/tasks`. Funciona mejor si abres los archivos `.specify/` en el editor |
| **Gemini CLI** | Similar a Copilot. Puede necesitar mas contexto en el prompt inicial |
| **Cursor** | No tiene slash commands nativos de Spec Kit. Copiar los prompts directamente al chat con los archivos constitution.md y spec.md adjuntos |

### Orden estricto

```
constitution → specify → clarify → plan → tasks → analyze → checklist → implement
```

> **Nunca saltar fases.** Cada fase depende de los artefactos generados por la fase anterior. Si se salta `/specify` y se va directo a `/plan`, el plan no tendra requisitos claros que seguir.

### Versionamiento

Despues de cada fase, hacer commit del artefacto generado:

```bash
git add constitution.md && git commit -m "SDD fase 0: constitution"
git add spec.md && git commit -m "SDD fase 1: specify"
git add plan.md && git commit -m "SDD fase 3: plan"
git add tasks.md && git commit -m "SDD fase 4: tasks"
```

Esto permite comparar los artefactos generados por cada IA en branches separados.

---

## 16. Referencias

### Sobre el rol del Desarrollador con IA

- [Fortune - The Supervisor Class: How AI Agents Are Remaking the Developer's Career (2026)](https://fortune.com/2026/03/31/fortune-com-2026-03-26-ai-agents-vibe-coding-developer-skills-supervisor-class/) — Define el concepto de "Clase Supervisora" y como el rol del desarrollador muta de escribir codigo a orquestar agentes
- [DEV Community - AI-Assisted Development in 2026: Best Practices, Real Risks, and the New Bar for Engineers](https://dev.to/austinwdigital/ai-assisted-development-in-2026-best-practices-real-risks-and-the-new-bar-for-engineers-3fom) — Mejores practicas, riesgos reales y la nueva vara para ingenieros. Fuente de "La IA produce volumen, los humanos aseguran calidad"
- [MindStudio - How AI Is Changing What It Means to Be a Developer in 2026](https://www.mindstudio.ai/blog/how-ai-is-changing-what-it-means-to-be-a-developer) — Analisis del cambio de competencias del desarrollador moderno
- [Shift Asia - The Rise of the AI-Augmented Developer](https://shiftasia.com/column/ai-in-software-development-the-rise-of-the-ai-augmented-developer/) — Cita las predicciones de Gartner: 75% de desarrolladores orquestaran en vez de codificar para 2026
- [Pragmatic Engineer - AI Tooling for Software Engineers in 2026](https://newsletter.pragmaticengineer.com/p/ai-tooling-2026) — Herramientas y flujos de trabajo del ingeniero aumentado con IA
- [Intetics - The State of AI-Native Software Engineering: 2026 Industry Analysis](https://intetics.com/white-papers/the-state-of-ai-native-software-engineering-2026-industry-analysis/) — Analisis de la industria sobre ingenieria de software nativa de IA

### Sobre iteracion y correccion en SDD

- [Hypergen - The End of Agile? Introducing Spec Driven Development](https://www.hypergen.com.au/blog/spec-driven-development) — Explica el ciclo de bajo costo "refinar spec → regenerar codigo" y por que SDD reduce el retrabajo
- [GitHub Spec Kit - Issue #1191: Spec-Driven Editing Flow](https://github.com/github/spec-kit/issues/1191) — Discusion oficial sobre como actualizar y refinar specs existentes
- [Fred Hutch - Spec-Driven Development with spec-kit: A Walkthrough](https://matsen.fredhutch.org/general/2026/02/10/spec-kit-walkthrough.html) — Ejemplo practico paso a paso con iteraciones y correcciones
- [Martin Fowler / Birgitta Bockeler - Understanding SDD Tools](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) — Analisis critico que advierte sobre la necesidad de revisar agresivamente la salida de la IA

### Sobre SDD y GitHub Spec Kit (del documento 01)

- [GitHub Blog - Spec-driven development with AI](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/) — Anuncio oficial del toolkit
- [GitHub Spec Kit - Repositorio](https://github.com/github/spec-kit) — Codigo fuente y templates
- [Microsoft for Developers - Diving Into Spec-Driven Development](https://developer.microsoft.com/blog/spec-driven-development-spec-kit) — Perspectiva de Microsoft

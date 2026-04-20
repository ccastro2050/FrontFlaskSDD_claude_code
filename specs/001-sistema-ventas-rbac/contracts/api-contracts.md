# API Consumer Contracts — FrontFlaskSDD → ApiGenericaCsharp

**Feature**: 001-sistema-ventas-rbac
**Fecha**: 2026-04-19
**Dirección**: consumer (este frontend) → `ApiGenericaCsharp` (proyecto externo)

Este documento fija **lo que el frontend espera de la API REST**: los endpoints que invoca, los payloads que envía y las formas que acepta. **No** es la especificación canónica de la API (esa vive en el repositorio `https://github.com/ccastro2050/ApiGenericaCsharp`); es un contrato de consumidor que actúa como fuente para los tests de integración del frontend y para detectar drift de la API.

## Convenciones generales

- **Base URL**: variable de entorno `API_BASE_URL` (ej. `https://api.zenith.local`).
- **Autenticación**: header `Authorization: Bearer <jwt>` en todas las rutas privadas. Excepción: `POST /api/autenticacion/token`.
- **Content-Type**: `application/json` para request y response excepto el login que puede aceptar `application/x-www-form-urlencoded`.
- **Formato de error**: la API devuelve `4xx` / `5xx` con cuerpo `{ "mensaje": "...", "detalle": "..." }`. El frontend lo traduce a `ApiError(status_code, mensaje, detalle)`.
- **Encriptación de campos**: para endpoints de escritura, el frontend envía el parámetro `camposEncriptar` con la lista de campos que la API debe encriptar con BCrypt (ej. `["contrasena"]`).

## 1. Autenticación

### `POST /api/autenticacion/token`

**Consumer intent**: intercambiar credenciales por un JWT.

**Request**

```json
{
  "email": "usuario@zenith.local",
  "contrasena": "Secreto123"
}
```

**Response 200**

```json
{
  "token": "eyJhbGciOi...",
  "expira_en": 3600
}
```

**Response 401**: credenciales inválidas. Cuerpo: `{ "mensaje": "Credenciales inválidas" }` (el frontend siempre muestra un mensaje neutro al usuario — FR-002).

## 2. CRUD genérico (ApiService)

Todos los catálogos simples usan el mismo cuadrilátero de endpoints. `{tabla}` es el nombre de tabla en la BD (ej. `producto`, `persona`, `empresa`, `cliente`, `vendedor`, `rol`, `ruta`).

### `GET /api/{tabla}`

Lista todos los registros.

**Response 200**: array de objetos con todos los campos de la tabla.

### `POST /api/{tabla}`

Crea un registro.

**Request**: objeto con los campos de la tabla. Puede incluir `camposEncriptar` cuando aplica.

**Response 201**: objeto creado (con PK asignada si es auto).

### `PUT /api/{tabla}/{pk}`

Actualiza el registro por PK.

**Request**: objeto con los campos a actualizar (+ `camposEncriptar` opcional).

**Response 200**: objeto actualizado.

### `DELETE /api/{tabla}/{pk}`

Elimina físicamente el registro por PK.

**Response 204** sin cuerpo. `409` si hay integridad referencial.

### Contrato por tabla

| Tabla | PK | Campos escribibles | Campos a encriptar |
|-------|----|--------------------|--------------------|
| `producto` | `codigo` | `codigo, nombre, stock, valorunitario` | — |
| `persona` | `codigo` | `codigo, nombre, email, telefono` | — |
| `empresa` | `codigo` | `codigo, nombre` | — |
| `cliente` | `id` | `credito, fkcodpersona, fkcodempresa` | — |
| `vendedor` | `id` | `carnet, direccion, fkcodpersona` | — |
| `rol` | `id` | `nombre` | — |
| `ruta` | `id` | `ruta, descripcion` | — |

## 3. Stored procedures (ejecutar_sp)

### `POST /api/ejecutar-sp` (o endpoint equivalente expuesto por la API)

**Consumer intent**: ejecutar un stored procedure por nombre pasando un diccionario de parámetros.

**Request**

```json
{
  "nombre": "sp_insertar_factura_y_productosporfactura",
  "parametros": {
    "fkid_cliente": 12,
    "fkid_vendedor": 3,
    "productos": [
      { "fkcodproducto": "P001", "cantidad": 2 },
      { "fkcodproducto": "P002", "cantidad": 1 }
    ]
  }
}
```

**Response 200**: resultado del SP serializado como JSON. La forma depende del SP (ver tabla siguiente). Errores de negocio (stock insuficiente, factura ya anulada, etc.) se devuelven como `400` con mensaje accionable.

### Catálogo de SPs consumidos

| SP | Propósito | Parámetros de entrada (claves) | Respuesta esperada | Rol requerido |
|----|-----------|--------------------------------|--------------------|---------------|
| `consulta_roles_y_rutas_por_usuario` | Carga consolidada en login | `fkid_usuario` | `{ roles: [{id,nombre}], rutas: [{id,ruta}] }` | cualquiera autenticado |
| `listar_usuarios_con_roles` | Usuarios + sus roles | — | array `{ id, email, requiere_cambio, roles: [...] }` | administrador |
| `crear_usuario_con_roles` | Alta de usuario con roles | `email, contrasena, requiere_cambio, roles:[int]` | `{ id }` | administrador |
| `actualizar_usuario_con_roles` | Edición total | `id, email, contrasena?, roles:[int]` | `{ ok: true }` | administrador |
| `consultar_usuario_con_roles` | Detalle 1 usuario | `id` | objeto usuario | administrador |
| `eliminar_usuario_con_roles` | Baja | `id` | `{ ok: true }` | administrador |
| `actualizar_roles_usuario` | Cambiar sólo roles | `id, roles:[int]` | `{ ok: true }` | administrador |
| `listar_rutarol` | Permisos ruta-rol | — | array `{ id, rol, ruta, descripcion }` | administrador |
| `crear_rutarol` | Alta permiso | `fkid_rol, fkid_ruta` | `{ id }` | administrador |
| `eliminar_rutarol` | Baja permiso | `id` | `{ ok: true }` | administrador |
| `verificar_acceso_ruta` | Debug / auditoría | `fkid_usuario, ruta` | `{ tiene_acceso: bool }` | administrador |
| `sp_listar_facturas_y_productosporfactura` | Listado con detalle | — | array factura con `detalle: [...]`, `cliente`, `vendedor` | vendedor / administrador |
| `sp_consultar_factura_y_productosporfactura` | Detalle 1 factura | `id` | objeto factura con detalle | vendedor / administrador |
| `sp_insertar_factura_y_productosporfactura` | Crear factura + líneas | `fkid_cliente, fkid_vendedor, productos:[{fkcodproducto,cantidad}]` | `{ id, total }` | vendedor / administrador |
| `sp_actualizar_factura_y_productosporfactura` | Editar factura activa | `id, fkid_cliente, fkid_vendedor, productos:[...]` | `{ ok: true, total }` | vendedor / administrador |
| `sp_anular_factura` | Borrado lógico | `id` | `{ ok: true }` | vendedor / administrador |
| `sp_borrar_factura_y_productosporfactura` | Borrado físico | `id` | `{ ok: true }` | **sólo administrador** |

## 4. Reglas de error del frontend

| Status HTTP | Interpretación | Acción del frontend |
|-------------|----------------|---------------------|
| 200 / 201 / 204 | OK | flash `success` en operaciones de escritura |
| 400 | Error de negocio (ej. stock insuficiente) | flash `warning`/`danger` con `mensaje` de la API |
| 401 | Token inválido o expirado | `session.clear()` + redirigir a `/login` con flash `Sesión expirada` |
| 403 | Autorizado en API pero no en negocio | flash `danger` con mensaje específico |
| 404 | Recurso no encontrado | flash `warning` y redirigir al listado |
| 409 | Conflicto (ej. FK bloquea borrado) | flash `warning` con explicación |
| 5xx | Fallo de servidor/red | flash `danger` genérico + log de stderr |

## 5. Fallback de carga de roles/rutas (FR-010)

Si `POST /api/ejecutar-sp` con `consulta_roles_y_rutas_por_usuario` falla con `5xx` o timeout:

1. `GET /api/usuario/{id}`
2. `GET /api/rol_usuario` → filtrar por `fkid_usuario`
3. `GET /api/rol` → lookup por `id`
4. `GET /api/rutarol` → filtrar por `fkid_rol`
5. `GET /api/ruta` → lookup por `id`

Si también falla cualquier paso: abortar login con flash `"No se pudo validar los permisos. Intenta más tarde."` y **no** conceder sesión.

## 6. Tests de contrato (dónde viven)

- Cada SP consumido: un test en `tests/integration/test_<blueprint>.py` que:
  1. Prepara datos semilla vía endpoints CRUD.
  2. Llama al flujo de UI que dispara el SP.
  3. Verifica que la respuesta y el estado quedan como este contrato indica.
- Los tests fallan si la API rompe el contrato (drift) → el frontend detecta la incompatibilidad antes de desplegar.

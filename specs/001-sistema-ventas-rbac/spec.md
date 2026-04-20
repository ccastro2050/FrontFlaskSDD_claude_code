# Feature Specification: Sistema de Ventas con RBAC y Facturación

**Feature Branch**: `001-sistema-ventas-rbac`
**Created**: 2026-04-19
**Status**: Draft
**Input**: User description: "Frontend web del sistema FrontFlaskSDD que consume la API REST ApiGenericaCsharp. Incluye autenticación, control de acceso por rol (RBAC), CRUDs de catálogos, gestión de usuarios y permisos, y facturación maestro-detalle con anulación lógica."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Acceso autenticado con control de acceso por rol (Priority: P1)

Un colaborador de Zenith abre el sistema, introduce su correo y contraseña, y entra a la aplicación. Una vez dentro, solo ve en el menú lateral los módulos a los que su rol le da acceso; si intenta acceder por URL a un módulo no autorizado, el sistema lo bloquea. Al terminar, cierra sesión desde la barra superior.

**Why this priority**: Sin autenticación ni control de acceso, ningún otro módulo puede usarse de forma segura. Define el perímetro de seguridad del sistema completo y es prerrequisito técnico y legal para operar con datos comerciales.

**Independent Test**: Se valida creando dos usuarios con roles distintos (por ejemplo, "vendedor" y "administrador"), iniciando sesión con cada uno, y comprobando que: (a) cada uno ve un menú distinto, (b) cada uno accede solo a las páginas permitidas, (c) el intento de URL no autorizada devuelve un error de acceso denegado, (d) tras cerrar sesión las páginas privadas redirigen al login.

**Acceptance Scenarios**:

1. **Given** un usuario registrado con rol "vendedor", **When** introduce credenciales válidas, **Then** el sistema lo lleva a la página de inicio y muestra solo los módulos asociados a su rol en el menú lateral.
2. **Given** un usuario con rol "vendedor" ya autenticado, **When** escribe manualmente la URL de un módulo reservado a administradores, **Then** el sistema muestra una página de "acceso denegado" y no revela el contenido restringido.
3. **Given** un usuario no autenticado, **When** intenta cargar cualquier página privada, **Then** el sistema lo redirige al login.
4. **Given** un usuario autenticado, **When** pulsa el botón de cerrar sesión, **Then** el sistema finaliza la sesión y vuelve al login; al retroceder con el navegador, no puede regresar al contenido privado.
5. **Given** credenciales inválidas, **When** se envía el formulario de login, **Then** el sistema muestra un mensaje de error claro y no concede acceso.

---

### User Story 2 - Facturación maestro-detalle con anulación lógica (Priority: P2)

Un vendedor emite una factura para un cliente: selecciona cliente y vendedor, agrega varios productos con sus cantidades, y guarda. El sistema registra la factura con sus totales, refleja el descuento de stock, y la muestra en el listado. Cuando una factura fue emitida por error, un usuario autorizado la anula (queda marcada como "anulada" y se repone el stock), pero la factura **nunca** desaparece del listado histórico. Solo el administrador puede borrar físicamente una factura.

**Why this priority**: Es el flujo de valor de negocio principal del sistema. Sin facturación la aplicación no cumple su objetivo comercial. La anulación lógica es un requisito de auditoría no negociable para documentos financieros.

**Independent Test**: Se valida: (a) creando una factura con múltiples productos y verificando que los totales se calculan y el stock disminuye; (b) anulando la factura y verificando que pasa a estado "anulada", el stock se repone, y la factura sigue siendo consultable en el historial; (c) confirmando que el botón de borrado físico solo está disponible para administrador; (d) consultando el detalle de una factura específica y verificando que muestra cliente, vendedor y líneas de productos.

**Acceptance Scenarios**:

1. **Given** existen clientes, vendedores y productos con stock, **When** el usuario crea una factura con cliente, vendedor y al menos un producto con cantidad, **Then** el sistema registra la factura, calcula subtotales y total, reduce el stock de cada producto según la cantidad vendida, y la factura aparece en el listado con estado "activa".
2. **Given** existe una factura "activa", **When** el usuario autorizado ejecuta la acción "anular", **Then** la factura cambia a estado "anulada", el stock de los productos facturados se restaura a los valores previos, y la factura sigue siendo visible en el listado histórico (no desaparece).
3. **Given** existe una factura (activa o anulada), **When** un usuario sin rol de administrador intenta borrarla físicamente, **Then** la acción no está disponible o se rechaza con un mensaje de acceso denegado.
4. **Given** existe una factura con rol administrador, **When** el administrador ejecuta "borrar factura", **Then** la factura y sus líneas son eliminadas físicamente y desaparecen del listado.
5. **Given** existe una factura "activa", **When** el usuario autorizado la edita cambiando cliente, vendedor o la lista de productos, **Then** el sistema reemplaza el detalle, recalcula totales y reajusta el stock consistentemente con la nueva composición.
6. **Given** se intenta facturar una cantidad mayor al stock disponible de un producto, **When** se envía la factura, **Then** el sistema rechaza la operación con un mensaje claro y no altera stocks ni crea la factura.

---

### User Story 3 - Mantenimiento de catálogos (CRUDs simples) (Priority: P3)

Un usuario con permisos de mantenimiento gestiona los catálogos base del sistema: productos, personas, empresas, clientes, vendedores, roles y rutas. Para cada catálogo puede listar los registros en una tabla, crear nuevos, editar existentes y eliminarlos con una confirmación previa. Los catálogos alimentan el módulo de facturación (productos, clientes, vendedores) y el de seguridad (roles, rutas).

**Why this priority**: Sin catálogos poblados no se pueden emitir facturas ni configurar permisos. Es prerrequisito de uso pero su complejidad es baja y repetitiva, por lo que se prioriza después del MVP de login + facturación.

**Independent Test**: Para cada catálogo se valida: (a) ver el listado con los registros existentes; (b) crear un registro nuevo y comprobar que aparece en el listado; (c) editar un registro y comprobar que los cambios persisten; (d) eliminar un registro tras confirmación y comprobar que ya no aparece; (e) para clientes y vendedores, que la relación con persona/empresa se muestra correctamente en el listado.

**Acceptance Scenarios**:

1. **Given** el usuario tiene acceso al catálogo de productos, **When** abre el módulo, **Then** ve una tabla con todos los productos mostrando código, nombre, stock y valor unitario.
2. **Given** el formulario de creación de un catálogo, **When** el usuario completa los campos obligatorios y envía, **Then** el registro aparece en el listado y el sistema muestra un mensaje de éxito.
3. **Given** un registro existente, **When** el usuario elige "editar", modifica valores y guarda, **Then** el listado refleja los cambios.
4. **Given** un registro existente, **When** el usuario pulsa "eliminar", **Then** el sistema pide confirmación explícita antes de borrar; al confirmar, el registro desaparece del listado.
5. **Given** un cliente referencia a una persona y una empresa, **When** se lista el catálogo de clientes, **Then** se muestran los datos relacionados (nombre de persona y empresa) de forma legible, no solo los identificadores.

---

### User Story 4 - Administración de usuarios y permisos (Priority: P4)

Un administrador gestiona las cuentas del sistema: crea usuarios con sus roles asignados, actualiza datos, reasigna roles sin tener que cambiar la contraseña, y elimina cuentas. Adicionalmente, configura qué rutas del sistema están permitidas para cada rol, pudiendo añadir o quitar permisos. Estas operaciones afectan inmediatamente qué módulos ven los usuarios en su próximo inicio de sesión.

**Why this priority**: Es imprescindible para operar el sistema en producción pero es una tarea de configuración esporádica, posterior al valor de negocio inmediato (facturación).

**Independent Test**: Se valida: (a) creando un usuario con uno o varios roles y comprobando que ese usuario puede iniciar sesión; (b) reasignando roles sin cambiar contraseña y comprobando que el menú y los permisos del usuario reflejan el cambio tras reiniciar sesión; (c) añadiendo una ruta a un rol y comprobando que los usuarios con ese rol obtienen acceso; (d) quitando una ruta de un rol y comprobando que pierden el acceso.

**Acceptance Scenarios**:

1. **Given** el administrador está en la pantalla de usuarios, **When** crea un usuario con email, contraseña y uno o más roles, **Then** el usuario aparece en el listado con sus roles visibles y puede iniciar sesión con esas credenciales.
2. **Given** un usuario existente, **When** el administrador cambia la lista de roles del usuario sin tocar el campo contraseña, **Then** los roles se actualizan y la contraseña del usuario sigue siendo válida para iniciar sesión.
3. **Given** un rol existente, **When** el administrador añade una ruta al conjunto de rutas permitidas para ese rol, **Then** los usuarios que tengan ese rol pasan a ver y poder acceder a esa ruta.
4. **Given** un permiso ruta-rol existente, **When** el administrador lo elimina, **Then** los usuarios con ese rol dejan de poder acceder a esa ruta (tanto por menú como por URL directa).
5. **Given** un usuario existente, **When** el administrador lo elimina, **Then** desaparece del listado y ya no puede iniciar sesión.

---

### User Story 5 - Gestión de contraseña por el propio usuario (Priority: P5)

Un usuario puede cambiar su propia contraseña introduciendo la actual y una nueva válida. Si la olvida, solicita recuperación introduciendo su correo; el sistema le envía una contraseña temporal por email y, al iniciar sesión con ella, el sistema le obliga a establecer una nueva antes de permitirle continuar.

**Why this priority**: Es una capacidad de autoservicio que reduce carga administrativa pero no es crítica para el primer lanzamiento: el administrador puede resetear contraseñas manualmente hasta que se habilite.

**Independent Test**: Se valida: (a) cambiando contraseña desde una sesión válida y comprobando que el siguiente login exige la nueva; (b) usando "olvidé mi contraseña" con un correo registrado y comprobando que llega un email con una clave temporal; (c) iniciando sesión con la clave temporal y comprobando que el sistema redirige al formulario de cambio obligatorio antes de permitir cualquier otra navegación; (d) comprobando que contraseñas demasiado débiles son rechazadas.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado, **When** pide cambiar contraseña, introduce la actual correcta y una nueva válida, **Then** el sistema confirma el cambio y la nueva es la única válida a partir de ese momento.
2. **Given** un usuario autenticado, **When** introduce la contraseña actual incorrecta, **Then** el sistema rechaza el cambio con un mensaje claro.
3. **Given** un usuario autenticado o el formulario de recuperación, **When** la nueva contraseña no cumple las reglas mínimas (longitud, mayúscula, número, no trivial), **Then** el sistema muestra el motivo específico y no actualiza la contraseña.
4. **Given** un usuario olvidó su contraseña, **When** solicita recuperación con un correo registrado, **Then** el sistema envía un email con una contraseña temporal y le indica que la revise.
5. **Given** un usuario inicia sesión con una contraseña temporal, **When** entra, **Then** el sistema lo lleva directamente al formulario de cambio obligatorio y no le permite navegar a ningún otro módulo hasta completarlo.
6. **Given** se solicita recuperación con un correo **no** registrado, **When** se envía la petición, **Then** el sistema responde con un mensaje neutro que no revela si el correo existe en el sistema.

---

### Edge Cases

- **Stock insuficiente en creación o edición de factura**: el sistema rechaza la operación con mensaje claro y no altera stock ni crea/modifica la factura.
- **Catálogo con dependencias**: si se intenta eliminar una persona referenciada por un cliente o vendedor, el sistema rechaza con mensaje explicativo.
- **Eliminación de rol en uso**: al eliminar un rol asignado a usuarios, el sistema avisa o impide la acción para evitar dejar usuarios sin rol válido.
- **Caída de la fuente de roles/rutas al iniciar sesión**: el sistema usa una consulta de respaldo para cargar roles y rutas del usuario; si todo falla, el login se rechaza con un mensaje operativo y no se concede acceso sin permisos validados.
- **Cambio de permisos de un usuario mientras tiene sesión abierta**: los cambios se aplican en su siguiente inicio de sesión (no hay cierre forzado automático).
- **Intento de anular o editar una factura ya anulada**: el sistema bloquea la acción e informa que la factura ya está anulada.
- **Factura con cero productos**: el formulario no permite guardar hasta añadir al menos un producto con cantidad mayor a cero.
- **Contraseña temporal vencida o ya usada**: el sistema rechaza el login y ofrece volver a solicitar recuperación.
- **Usuario eliminado con sesión activa**: al siguiente request autenticado, el sistema lo cierra y redirige a login.
- **Fallo al enviar el email de recuperación**: el sistema informa del problema sin revelar existencia del correo y no deja al usuario en un estado incoherente (no se marca como "cambio obligatorio" si la temporal no llegó).

## Requirements *(mandatory)*

### Functional Requirements

**Autenticación y sesión**

- **FR-001**: El sistema MUST permitir iniciar sesión con correo electrónico y contraseña.
- **FR-002**: El sistema MUST rechazar credenciales inválidas con un mensaje no revelador (no distinguir entre "correo no existe" y "contraseña incorrecta").
- **FR-003**: El sistema MUST mantener la sesión del usuario entre peticiones mientras no cierre sesión explícitamente o la sesión expire por inactividad.
- **FR-004**: El sistema MUST permitir cerrar sesión desde cualquier página privada; tras el cierre, las páginas privadas MUST redirigir al login.
- **FR-005**: El sistema MUST obligar a cambiar la contraseña al iniciar sesión con una contraseña marcada como temporal, sin permitir otra navegación hasta completar el cambio.

**Control de acceso (RBAC)**

- **FR-006**: Al iniciar sesión, el sistema MUST cargar los roles del usuario y el conjunto de rutas permitidas para esos roles, y mantenerlos disponibles durante toda la sesión.
- **FR-007**: En cada petición, el sistema MUST verificar que la ruta solicitada esté dentro de las rutas permitidas del usuario; de lo contrario MUST mostrar una página de acceso denegado.
- **FR-008**: Las rutas públicas (login, cierre de sesión, recuperación de contraseña y recursos estáticos) MUST estar accesibles sin sesión; el resto MUST exigir sesión.
- **FR-009**: El menú de navegación MUST mostrar únicamente las opciones correspondientes a rutas permitidas del usuario actual.
- **FR-010**: El sistema MUST disponer de un mecanismo de respaldo para cargar roles y rutas si la fuente primaria consolidada no responde, de modo que un fallo puntual no deje el acceso sin control.

**Gestión de contraseña**

- **FR-011**: El sistema MUST permitir al usuario autenticado cambiar su propia contraseña introduciendo la actual.
- **FR-012**: El sistema MUST validar nuevas contraseñas con reglas mínimas: al menos 6 caracteres, al menos una mayúscula, al menos un número, y rechazar contraseñas triviales (p. ej. coincidir con el correo o ser una secuencia obvia).
- **FR-013**: El sistema MUST almacenar contraseñas de forma irreversible (hash con algoritmo probado) y nunca en texto plano.
- **FR-014**: El sistema MUST permitir a un usuario solicitar recuperación de contraseña indicando su correo; si existe, MUST generar una contraseña temporal, marcarla como "requiere cambio al próximo login" y enviarla por correo electrónico.
- **FR-015**: El sistema MUST responder a solicitudes de recuperación con un mensaje neutro que no revele si el correo está o no registrado.

**Catálogos (CRUDs simples)**

- **FR-016**: El sistema MUST ofrecer, para cada uno de los siguientes catálogos, las operaciones listar, crear, editar y eliminar: Producto, Persona, Empresa, Cliente, Vendedor, Rol y Ruta.
- **FR-017**: Cada formulario de creación/edición MUST validar campos obligatorios y formatos básicos (por ejemplo, correo en Persona, valores numéricos no negativos en stock y valor unitario).
- **FR-018**: La acción de eliminar MUST requerir confirmación explícita del usuario antes de proceder.
- **FR-019**: Los listados de Cliente y Vendedor MUST mostrar los datos relacionados de Persona y (para Cliente) Empresa de forma legible, no solo los identificadores.
- **FR-020**: El sistema MUST impedir la eliminación de registros de catálogo que estén referenciados por otros (p. ej., una persona usada por un cliente), informando la causa.

**Administración de usuarios y permisos**

- **FR-021**: El sistema MUST permitir al administrador listar, crear, consultar, actualizar y eliminar usuarios, asignando uno o varios roles en cada caso.
- **FR-022**: El sistema MUST permitir al administrador actualizar los roles de un usuario sin modificar la contraseña.
- **FR-023**: El sistema MUST permitir al administrador listar, crear y eliminar permisos que asocian una ruta a un rol.
- **FR-024**: Los cambios en roles y permisos MUST ser efectivos a partir del siguiente inicio de sesión de cada usuario afectado.

**Facturación**

- **FR-025**: El sistema MUST permitir crear una factura seleccionando cliente y vendedor y añadiendo una o más líneas de producto con cantidad.
- **FR-026**: El sistema MUST calcular subtotales por línea y total general de la factura automáticamente, sin intervención manual.
- **FR-027**: El sistema MUST descontar del stock de cada producto la cantidad facturada al crear la factura.
- **FR-028**: El sistema MUST rechazar la creación o edición de una factura cuando la cantidad solicitada supere el stock disponible, sin alterar datos.
- **FR-029**: El sistema MUST permitir consultar el detalle completo de una factura (cliente, vendedor, líneas y totales).
- **FR-030**: El sistema MUST permitir editar una factura activa reemplazando cliente, vendedor o las líneas, reajustando el stock de forma consistente.
- **FR-031**: El sistema MUST permitir anular una factura activa: al anularla, cambia su estado a "anulada" y restaura el stock de los productos facturados.
- **FR-032**: Las facturas anuladas MUST permanecer visibles en el listado histórico y consultables; no MUST desaparecer.
- **FR-033**: El sistema MUST impedir anular o editar una factura que ya esté en estado "anulada".
- **FR-034**: Solo el administrador MUST poder eliminar físicamente una factura; para cualquier otro rol la acción MUST estar ausente o rechazada.

**Navegación y retroalimentación**

- **FR-035**: Toda acción de creación, edición, eliminación, anulación o cambio de estado MUST mostrar al usuario un mensaje de confirmación (éxito o error) visible y descartable.
- **FR-036**: Toda página privada MUST mostrar el nombre del usuario en sesión y un acceso visible a cerrar sesión.

### Key Entities *(include if feature involves data)*

- **Usuario**: persona que accede al sistema. Atributos clave: correo (identificador único de acceso), contraseña (almacenada cifrada), indicador de "cambio obligatorio", y conjunto de roles. Se relaciona con Rol (N:M).
- **Rol**: agrupación de permisos (p. ej., "administrador", "vendedor"). Se relaciona con Ruta (N:M mediante permisos ruta-rol) y con Usuario.
- **Ruta**: camino navegable del sistema que puede estar restringido (p. ej., "/productos", "/facturas/nueva"). Incluye una descripción para documentación.
- **Permiso ruta-rol**: asociación explícita que indica que los usuarios con un rol concreto pueden acceder a una ruta concreta.
- **Producto**: artículo vendible. Atributos: código (identificador), nombre, stock actual, valor unitario.
- **Persona**: datos personales básicos. Atributos: código (identificador), nombre, correo, teléfono. Referenciada por Cliente y Vendedor.
- **Empresa**: entidad comercial. Atributos: código (identificador), nombre. Referenciada por Cliente.
- **Cliente**: entidad de venta, asociada a una Persona y una Empresa. Atributos propios: identificador autoasignado, crédito disponible.
- **Vendedor**: emisor de facturas, asociado a una Persona. Atributos propios: identificador autoasignado, carnet, dirección.
- **Factura** (maestro): documento de venta. Atributos clave: identificador, fecha, cliente asociado, vendedor asociado, total calculado y estado (`activa` / `anulada`).
- **Línea de factura** (detalle): un producto dentro de una factura con cantidad, valor unitario aplicado y subtotal. Varias líneas pueden pertenecer a la misma factura.
- **Contraseña temporal**: estado transitorio de la credencial de un usuario tras solicitar recuperación, que obliga al cambio en el próximo inicio de sesión.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las rutas privadas están protegidas: un usuario sin sesión nunca ve contenido privado, y un usuario autenticado nunca ve un módulo que no esté en su lista de rutas permitidas (verificado por pruebas con al menos dos roles distintos cubriendo todos los módulos del menú).
- **SC-002**: Un usuario puede iniciar sesión y llegar a su página de inicio en menos de 5 segundos desde que pulsa "entrar", en condiciones normales de red.
- **SC-003**: El 100% de las facturas anuladas permanecen visibles y consultables en el listado histórico por al menos 7 años (periodo legal típico de conservación contable), sin degradación del tiempo de listado.
- **SC-004**: La creación de una factura con hasta 10 líneas se completa en menos de 3 segundos desde que el usuario pulsa "guardar".
- **SC-005**: Al anular una factura, los stocks afectados quedan reajustados con exactitud al valor previo a la emisión en el 100% de los casos (diferencia cero entre stock antes-de-factura y después-de-anulación).
- **SC-006**: Las contraseñas de todos los usuarios son irrecuperables en texto plano: una inspección directa del almacén no revela ninguna contraseña legible.
- **SC-007**: El flujo "olvidé mi contraseña → recibir temporal por email → iniciar sesión → establecer nueva" es completable por un usuario final en menos de 5 minutos sin asistencia.
- **SC-008**: Un cambio de permisos por parte del administrador se refleja en el menú y en el acceso del usuario afectado en su siguiente inicio de sesión, en el 100% de los casos.
- **SC-009**: Al intentar facturar una cantidad superior al stock, el sistema rechaza la operación en el 100% de los casos sin dejar datos inconsistentes (sin factura parcial ni stock alterado).
- **SC-010**: La tasa de mensajes de error genéricos ("ocurrió un error") en los flujos críticos (login, creación/anulación de factura, cambio de contraseña) es inferior al 1% del total de errores: el resto son mensajes específicos y accionables para el usuario.

## Assumptions

- **Auditoría fiscal**: La conservación histórica de facturas anuladas (SC-003) asume el estándar contable habitual de 7 años. Puede ajustarse sin cambiar el diseño.
- **Expiración de contraseña temporal**: Se asume una ventana razonable (por defecto 24 horas) para usar la contraseña temporal antes de requerir una nueva solicitud. Configurable sin impacto en el flujo.
- **Tiempo de inactividad de sesión**: Se asume un timeout de sesión razonable (por defecto 30 minutos de inactividad) acorde con aplicaciones administrativas similares.
- **Límite por factura**: No se establece un máximo estricto de líneas por factura; el rendimiento se valida hasta 50 líneas como volumen típico de uso.
- **Entrega de correos**: Se asume disponibilidad de un canal SMTP externo para envío del correo de contraseña temporal; caídas de ese canal se tratan como error operativo visible al usuario sin comprometer la consistencia de datos.
- **Fuente de datos única**: Toda persistencia se delega a la API REST existente (sin acceso directo a base de datos desde el frontend), conforme al artículo I de la constitución del proyecto.
- **Idioma**: Toda la interfaz, mensajes de error y mensajes flash se entregan en español.
- **Identidad visual**: La aplicación aplica la identidad visual Zenith definida en `Manual_de_Marca_Zenith.md` (colores, tipografía, iconos); las desviaciones visuales se tratan como defectos.
- **Capacidad de administración inicial**: Se asume la existencia de al menos un usuario administrador semilla al desplegar el sistema, para poder crear el resto de usuarios y permisos.
- **Reglas de negocio de cálculo y stock**: Los cálculos de totales y los ajustes de stock los produce la capa de persistencia (triggers y procedimientos del sistema de datos existente); el frontend los refleja pero no los recalcula por su cuenta.

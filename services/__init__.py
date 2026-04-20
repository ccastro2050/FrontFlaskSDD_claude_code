"""Paquete ``services`` — lógica de integración con la API externa.

Contiene dos servicios centralizados obligatorios por la Constitución
(Principio II):

- ``api_service.ApiService``: CRUD genérico y ejecución de stored procedures
  contra ``ApiGenericaCsharp``.
- ``auth_service.AuthService``: autenticación, RBAC, cambio/recuperación de
  contraseña y descubrimiento dinámico de PKs/FKs.

Los blueprints de ``routes/`` NUNCA hablan HTTP directamente: siempre pasan
por estos servicios.
"""

"""Paquete ``routes`` — blueprints de Flask organizados por módulo.

Cada archivo ``routes/<modulo>.py`` expone un ``Blueprint`` independiente
con las rutas de ese módulo (Principio II de la Constitución:
``Patrón Blueprint: cada módulo del frontend es un Blueprint independiente``).

Los blueprints NO hablan HTTP directamente: delegan en
``current_app.api`` (ApiService) y ``current_app.auth`` (AuthService).
"""

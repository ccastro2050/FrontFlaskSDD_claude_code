"""
routes/home.py — Blueprint de la página de inicio.

La landing page tras autenticación. Muestra un saludo al usuario y accesos
rápidos a los módulos para los que tiene permiso (la vista filtra por
``rutas_permitidas`` de la sesión — no duplica la lógica del middleware).

Cómo se relaciona con el resto:
- Está permitida **siempre** para usuarios autenticados (el middleware
  considera ``/`` como ruta permitida por defecto).
- La plantilla ``templates/pages/home/index.html`` usa las variables del
  context processor (``usuario``, ``roles``, ``rutas_permitidas``).
"""

from flask import Blueprint, render_template

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    return render_template("pages/home/index.html")

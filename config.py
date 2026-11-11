"""Configuración general del sistema POS Chifa Shun Fa.

Cada integrante pone SU servidor en config_local.py (no se sube a Git).
Copia config_local.ejemplo.py como config_local.py y ajústalo.
"""

DB_CONFIG = {
    "driver": "ODBC Driver 17 for SQL Server",  # o 18
    "server": r"localhost\SQLEXPRESS",
    "database": "PosShunFa",
    "trusted_connection": True,  # Autenticación de Windows
    "user": None,                # solo si trusted_connection = False
    "password": None,
}

TOTAL_MESAS = 23
INTERVALO_COCINA_MS = 5000  # refresco de la pantalla de cocina

COLOR_LIBRE = "#1E88E5"      # azul
COLOR_EN_CURSO = "#E53935"   # rojo

# Configuración personal de cada integrante (no se sube a Git)
try:
    from config_local import DB_CONFIG  # noqa: F401,F811
except ImportError:
    pass

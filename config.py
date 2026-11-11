"""Configuración general del sistema POS Chifa Shun Fa."""

# Ajusta SERVER según tu instalación de SQL Server.
# SQL Server Express suele ser: r"localhost\SQLEXPRESS"
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

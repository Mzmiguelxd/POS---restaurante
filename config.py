"""Configuración general del sistema POS Chifa Shun Fa."""

# Ajusta SERVER según tu instalación de SQL Server.
# SQL Server Express suele ser: r"localhost\SQLEXPRESS"
DB_CONFIG = {
    "driver": "ODBC Driver 17 for SQL Server",  # lo confirmamos abajo
    "server": "HeliosNeo",
    "database": "PosShunFa",
    "trusted_connection": True,  # Autenticación de Windows
    "user": None,
    "password": None,
}

TOTAL_MESAS = 23
INTERVALO_COCINA_MS = 5000  # refresco de la pantalla de cocina

COLOR_LIBRE = "#1E88E5"      # azul
COLOR_EN_CURSO = "#E53935"   # rojo

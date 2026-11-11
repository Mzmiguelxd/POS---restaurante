# POS Chifa Shun Fa (POODEROSOS)

Sistema POS para restaurante: Python + Tkinter + SQL Server.

## Puesta en marcha
1. Ejecutar `database/schema.sql` en SQL Server (SSMS).
2. Ajustar `config.py` (servidor y driver ODBC).
3. `pip install -r requirements.txt`
4. `python main.py`

## Estructura
- `database/` conexión y script SQL
- `models/` clases del dominio
- `services/` lógica de negocio
- `ui/` pantallas Tkinter

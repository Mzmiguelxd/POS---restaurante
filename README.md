# POS Chifa Shun Fa (POODEROSOS)

Sistema POS para restaurante: Python + Tkinter + SQL Server.

## Puesta en marcha (cada integrante)
1. Clonar el repo: `git clone https://github.com/Mzmiguelxd/POS---restaurante.git`
2. Crear la BD: abrir `database/schema.sql` en SSMS y ejecutarlo completo (F5).
   - Si ya tenías la BD creada con la versión anterior, ejecuta `database/migracion_001.sql`.
3. Copiar `config_local.ejemplo.py` como `config_local.py` y poner el nombre de tu servidor
   (el que aparece en SSMS al conectar). Este archivo no se sube a Git.
4. Instalar dependencias: `python -m pip install -r requirements.txt`
5. Ejecutar: `python main.py`

## Estructura
- `database/` conexión, script SQL y migraciones
- `models/` clases del dominio (Mesa, Plato, Pedido, DetallePedido)
- `services/` lógica de negocio (mesas, pedidos, reportes)
- `ui/` pantallas Tkinter (salón, pedido, cocina, cuenta)

## Funcionalidades
- Mapa del salón con 23 mesas: azul = libre, rojo = en curso.
- Toma de pedido: agregar, sumar, restar y quitar platos. Un solo pedido abierto por mesa.
- Cocina: muestra solo los platos que faltan preparar y marca los adicionales.
- Cuenta automática y cierre de mesa.
- Reporte del día: ventas, platos más vendidos y tiempo promedio por mesa.

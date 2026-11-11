# POS Chifa Shun Fa (POODEROSOS)

Sistema POS para restaurante: Python + Tkinter + SQL Server.

## Estructura
- `database/` conexión, script SQL y migraciones
- `models/` clases del dominio (Usuario, Mesa, Plato, Pedido, DetallePedido)
- `services/` lógica de negocio (usuarios, mesas, pedidos, reportes, comprobante)
- `ui/` pantallas Tkinter: `login`, `layout` (plantilla con menú por rol), `salon` (plano),
  `usuario/` (mesas, pedido, cocina), `admin/` (mesas, personal, ventas), detalle, pago, comprobante
- `util/` carga de imágenes

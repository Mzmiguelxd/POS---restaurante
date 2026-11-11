# POS Chifa Shun Fa (POODEROSOS)

Sistema POS para restaurante: Python + Tkinter + SQL Server.

## Puesta en marcha (cada integrante)
1. Clonar el repo: `git clone https://github.com/Mzmiguelxd/POS---restaurante.git`
2. Crear la BD: abrir `database/schema.sql` en SSMS y ejecutarlo completo (F5).
   - Si ya tenías la BD de una versión anterior, ejecuta en orden
     `database/migracion_001.sql` y `database/migracion_002.sql`.
3. Copiar `config_local.ejemplo.py` como `config_local.py` y poner el nombre de tu servidor
   (el que aparece en SSMS al conectar). Este archivo no se sube a Git.
4. Instalar dependencias: `python -m pip install -r requirements.txt`
5. Ejecutar: `python main.py`

Al primer arranque se crea el administrador **admin@shunfa.pe / Admin123**.
Cambia esa contraseña en CONFIGURACIÓN. El personal crea su cuenta con "Regístrese aquí".

## Roles
- **Usuario (personal de salón):** EN ORDEN (plano del salón, toma de pedidos, detalle,
  cobro y comprobante), COCINA, CONFIGURACIÓN, SALIR.
- **Administrador:** MESAS (plano, ver pedidos y cobrar), PERSONAL (estado y contacto),
  REGISTRO DE VENTAS (diario, mensual, trimestral; por tipo de pago; exportar CSV),
  CONFIGURACIÓN, SALIR.

## Imágenes
- Platos: guarda la foto en `img/platos/` con el nombre del plato en minúsculas y con guiones,
  por ejemplo `img/platos/arroz-chaufa-de-pollo.jpg`. Sin foto se muestran las iniciales.
- Personal: cada uno sube su foto desde CONFIGURACIÓN (se guarda en `img/personal/`).
- Para fotos .jpg instala Pillow (incluido en requirements.txt); sin Pillow solo se ven .png/.gif.

## Estructura
- `database/` conexión, script SQL y migraciones
- `models/` clases del dominio (Usuario, Mesa, Plato, Pedido, DetallePedido)
- `services/` lógica de negocio (usuarios, mesas, pedidos, reportes, comprobante)
- `ui/` pantallas Tkinter: `login`, `layout` (plantilla con menú por rol), `salon` (plano),
  `usuario/` (mesas, pedido, cocina), `admin/` (mesas, personal, ventas), detalle, pago, comprobante
- `util/` carga de imágenes

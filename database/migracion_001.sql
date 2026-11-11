-- Migración 001: ejecutar SOLO si ya creaste la BD con la versión anterior
-- de schema.sql. (Si creas la BD desde cero, usa schema.sql y omite esto.)
USE PosShunFa;
GO

-- 1) Estado de cada plato en cocina
IF COL_LENGTH('DetallePedido', 'estado') IS NULL
BEGIN
    ALTER TABLE DetallePedido ADD estado VARCHAR(10) NOT NULL
        CONSTRAINT DF_DetallePedido_estado DEFAULT 'PENDIENTE'
        CONSTRAINT CK_DetallePedido_estado CHECK (estado IN ('PENDIENTE','LISTO'));
END
GO

-- Los platos de pedidos ya listos o cobrados se marcan como preparados
UPDATE d SET d.estado = 'LISTO'
FROM DetallePedido d JOIN Pedido p ON p.id = d.id_pedido
WHERE p.estado IN ('LISTO','FINALIZADO');
GO

-- 2) Cerrar pedidos duplicados que pudieran existir (deja el más reciente)
;WITH dup AS (
    SELECT id, ROW_NUMBER() OVER (PARTITION BY id_mesa ORDER BY id DESC) AS rn
    FROM Pedido WHERE estado <> 'FINALIZADO'
)
UPDATE Pedido SET estado = 'FINALIZADO', fecha_fin = GETDATE()
WHERE id IN (SELECT id FROM dup WHERE rn > 1);
GO

-- 3) Una mesa solo puede tener UN pedido abierto
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UX_Pedido_MesaActiva')
    CREATE UNIQUE INDEX UX_Pedido_MesaActiva ON Pedido(id_mesa)
        WHERE estado <> 'FINALIZADO';
GO

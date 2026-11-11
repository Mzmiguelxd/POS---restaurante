-- Migración 002: usuarios, observaciones, método de pago e imágenes.
-- Ejecutar si tu BD ya existía (después de migracion_001.sql).
USE PosShunFa;
GO

IF OBJECT_ID('Usuario') IS NULL
BEGIN
    CREATE TABLE Usuario (
        id                INT IDENTITY(1,1) PRIMARY KEY,
        nombres           VARCHAR(60)  NOT NULL,
        apellidos         VARCHAR(60)  NOT NULL,
        correo            VARCHAR(120) NOT NULL UNIQUE,
        password_hash     VARCHAR(200) NOT NULL,
        fecha_nacimiento  DATE NULL,
        telefono          VARCHAR(20)  NULL,
        foto              VARCHAR(200) NULL,
        rol               VARCHAR(10)  NOT NULL DEFAULT 'USUARIO'
                          CHECK (rol IN ('ADMIN','USUARIO')),
        estado            VARCHAR(12)  NOT NULL DEFAULT 'AUSENTE'
                          CHECK (estado IN ('TRABAJANDO','AUSENTE')),
        activo            BIT NOT NULL DEFAULT 1,
        fecha_registro    DATETIME NOT NULL DEFAULT GETDATE()
    );
END
GO

IF COL_LENGTH('Plato', 'imagen') IS NULL
    ALTER TABLE Plato ADD imagen VARCHAR(200) NULL;
GO
IF COL_LENGTH('Pedido', 'id_usuario') IS NULL
    ALTER TABLE Pedido ADD id_usuario INT NULL
        CONSTRAINT FK_Pedido_Usuario REFERENCES Usuario(id);
GO
IF COL_LENGTH('Pedido', 'observaciones') IS NULL
    ALTER TABLE Pedido ADD observaciones VARCHAR(400) NULL;
GO
IF COL_LENGTH('Pedido', 'metodo_pago') IS NULL
    ALTER TABLE Pedido ADD metodo_pago VARCHAR(10) NULL
        CONSTRAINT CK_Pedido_metodo CHECK (metodo_pago IN ('EFECTIVO','TARJETA','YAPE'));
GO

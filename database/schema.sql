-- Esquema POS Chifa Shun Fa (SQL Server)
IF DB_ID('PosShunFa') IS NULL CREATE DATABASE PosShunFa;
GO
USE PosShunFa;
GO

CREATE TABLE Mesa (
    id      INT IDENTITY(1,1) PRIMARY KEY,
    numero  INT NOT NULL UNIQUE,
    estado  VARCHAR(10) NOT NULL DEFAULT 'LIBRE'
            CHECK (estado IN ('LIBRE','EN_CURSO'))
);

CREATE TABLE Plato (
    id         INT IDENTITY(1,1) PRIMARY KEY,
    nombre     VARCHAR(80) NOT NULL,
    categoria  VARCHAR(40) NOT NULL,
    precio     DECIMAL(10,2) NOT NULL CHECK (precio >= 0),
    activo     BIT NOT NULL DEFAULT 1
);

CREATE TABLE Pedido (
    id            INT IDENTITY(1,1) PRIMARY KEY,
    id_mesa       INT NOT NULL REFERENCES Mesa(id),
    fecha_inicio  DATETIME NOT NULL DEFAULT GETDATE(),
    fecha_fin     DATETIME NULL,
    estado        VARCHAR(12) NOT NULL DEFAULT 'PENDIENTE'
                  CHECK (estado IN ('PENDIENTE','LISTO','FINALIZADO')),
    total         DECIMAL(10,2) NOT NULL DEFAULT 0
);

CREATE TABLE DetallePedido (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    id_pedido       INT NOT NULL REFERENCES Pedido(id),
    id_plato        INT NOT NULL REFERENCES Plato(id),
    cantidad        INT NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10,2) NOT NULL,   -- precio congelado al vender
    nota            VARCHAR(150) NULL
);
GO

-- Datos iniciales: 23 mesas
DECLARE @i INT = 1;
WHILE @i <= 23
BEGIN
    INSERT INTO Mesa (numero) VALUES (@i);
    SET @i += 1;
END
GO

-- Menú de ejemplo (ajústalo al real del chifa)
INSERT INTO Plato (nombre, categoria, precio) VALUES
('Arroz Chaufa de Pollo',   'Chaufa',   18.00),
('Arroz Chaufa Especial',   'Chaufa',   22.00),
('Tallarín Saltado de Pollo','Tallarín', 19.00),
('Tallarín Saltado de Carne','Tallarín', 21.00),
('Aeropuerto',              'Combinados',24.00),
('Pollo con Tausi',         'Platos',   23.00),
('Lomo Saltado',            'Platos',   25.00),
('Kam Lu Wantán',           'Platos',   26.00),
('Wantán Frito (6 und)',    'Entradas', 12.00),
('Sopa Wantán',             'Sopas',    16.00),
('Sopa Fuchifu',            'Sopas',    20.00),
('Chicha Morada (jarra)',   'Bebidas',  14.00),
('Inca Kola 1.5 L',         'Bebidas',  10.00),
('Té (pote)',               'Bebidas',   4.00),
('Gaseosa personal',        'Bebidas',   4.50);
GO

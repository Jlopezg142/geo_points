CREATE EXTENSION IF NOT EXISTS postgis;

DROP TABLE IF EXISTS puntos;

CREATE TABLE puntos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    descripcion TEXT,
    categoria VARCHAR(50),
    geom GEOGRAPHY(Point,4326)
);

INSERT INTO puntos (nombre, descripcion, categoria, geom)
VALUES
('Agencia Zona 12', 'Ferreteria', 'Punto de Venta', ST_SetSRID(ST_MakePoint(-90.5459,14.5847),4326)),
('Agencia Retalhuleu', 'Ferreteria', 'Punto de Venta', ST_SetSRID(ST_MakePoint(-91.6714,14.5412),4326)),
('Agencia San Juan', 'Materiales de Construccion', 'Punto de Venta', ST_SetSRID(ST_MakePoint(-90.6435,14.7298),4326)), 
('Agencia Villa Hermosa', 'Materiales de Construccion', 'Punto de Ventas', ST_SetSRID(ST_MakePoint(-90.5531,14.5274),4326)), 
('Cementos Progreso', 'Ferreteria', 'Proveedor', ST_SetSRID(ST_MakePoint(-90.5224,14.5769),4326), 
('Aceros de Guatemala', 'Materiales de Construccion', 'Proveedor', ST_SetSRID(ST_MakePoint(-90.1753,14.8198),4326), 
('Oficinas Administrativas', 'RRHH', 'Servicio', ST_SetSRID(ST_MakePoint(-90.4848,14.4685),4326));  

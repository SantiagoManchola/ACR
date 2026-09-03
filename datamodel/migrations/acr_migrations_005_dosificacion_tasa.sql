-- Migración increment: agrega a `dosificaciones` la tasa/caudal con la que
-- dosifica la bomba (ej. ml/min). Es un dato INFORMATIVO: NO descuenta
-- inventario. Lo que descuenta sigue siendo `cantidad` (químico incorporado,
-- ej. 1 L de cloro). Con la tasa + el stock puesto en el tanque se estima
-- cuántas horas de dosificación continua quedan (momentos críticos).
--
-- Ejecutar en MySQL con la base ya creada a partir de acr_migrations.sql:
--   mysql -u <usuario> -p <basedatos> < acr_migrations_005_dosificacion_tasa.sql

ALTER TABLE dosificaciones
  ADD COLUMN tasa DECIMAL(12,4) NULL
  AFTER unidad;

ALTER TABLE dosificaciones
  ADD COLUMN unidad_tasa VARCHAR(20) NULL DEFAULT 'ml/min'
  AFTER tasa;

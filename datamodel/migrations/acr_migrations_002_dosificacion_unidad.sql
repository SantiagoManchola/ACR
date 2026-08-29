-- Migración increment: agrega la columna `unidad` a `dosificaciones`
-- para guardar la unidad del químico al momento de la dosificación
-- (punto 4: el valor queda fijo aunque luego se cambie la unidad del producto).
--
-- Ejecutar en MySQL con la base ya creada a partir de acr_migrations.sql:
--   mysql -u <usuario> -p <basedatos> < acr_migrations_002_dosificacion_unidad.sql

ALTER TABLE dosificaciones
  ADD COLUMN unidad VARCHAR(20) NULL
  AFTER cantidad;

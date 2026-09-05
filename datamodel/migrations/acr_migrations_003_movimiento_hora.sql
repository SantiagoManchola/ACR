-- NOTA: ya consolidado en acr_migrations.sql (principal actualizado).
-- Solo aplicar si tu BD se creó con una versión anterior del principal.
-- Migración increment: agrega la columna `hora` a `movimientos_inventario`
-- para registrar la hora del movimiento además de la fecha (punto 3).
--
-- Ejecutar en MySQL con la base ya creada a partir de acr_migrations.sql:
--   mysql -u <usuario> -p <basedatos> < acr_migrations_003_movimiento_hora.sql

ALTER TABLE movimientos_inventario
  ADD COLUMN hora TIME NULL
  AFTER fecha;

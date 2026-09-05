-- NOTA: ya consolidado en acr_migrations.sql (principal actualizado).
-- Solo aplicar si tu BD se creó con una versión anterior del principal.
-- Migración increment: agrega la columna `condicion` a `micromedidores`
-- para la condición operativa del medidor (punto 1):
--   bueno      -> normal (por defecto)
--   defectuoso -> se marca (se fija manualmente desde el CMS)
--   frenado    -> contador detenido; se detecta automáticamente cuando las
--                 3 últimas lecturas mensuales son idénticas y se desactiva
--                 con la siguiente medición distinta.
-- Los medidores existentes quedan en 'bueno'.
--
-- Ejecutar en MySQL con la base ya creada a partir de acr_migrations.sql:
--   mysql -u <usuario> -p <basedatos> < acr_migrations_004_micromedidor_condicion.sql

ALTER TABLE micromedidores
  ADD COLUMN condicion ENUM('bueno','defectuoso','frenado') NOT NULL DEFAULT 'bueno'
  AFTER fecha_instalacion;

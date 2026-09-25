-- NOTA: ya consolidado en acr_migrations.sql (principal actualizado).
-- Solo aplicar si tu BD se creó con una versión anterior del principal.
-- Migración increment: agrega la columna `condicion_reset_lectura_id` a
-- `micromedidores` para el corte de la detección automática de frenado.
--
-- Regla (punto 1, ajuste): cuando un medidor marcado como 'frenado' se marca
-- manualmente como 'bueno', el sistema debe esperar 3 MEDICIONES NUEVAS antes
-- de volver a reportarlo como frenado; no puede reutilizar las lecturas que
-- originaron el aviso anterior.
--
-- La columna guarda el id de la última lectura del medidor en el momento del
-- marcado manual como 'bueno'. `evaluar_condicion` solo cuenta lecturas con id
-- mayor a ese corte; NULL significa "sin corte" (comportamiento original).
--
-- Ejecutar en MySQL con la base ya creada a partir de acr_migrations.sql:
--   mysql -u <usuario> -p <basedatos> < acr_migrations_009_frenado_reset.sql

ALTER TABLE micromedidores
  ADD COLUMN condicion_reset_lectura_id INT NULL
  AFTER condicion;

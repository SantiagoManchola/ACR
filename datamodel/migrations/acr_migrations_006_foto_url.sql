-- 006: evidencias fotográficas opcionales (URL pública en Cloudflare R2).
-- mediciones de parámetros, lecturas de micromedidores y actividades de planta.
-- Re-ejecutable: solo agrega la columna si no existe (MySQL no soporta IF NOT EXISTS en ALTER).
SET @col := (SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'mediciones' AND COLUMN_NAME = 'foto_url');
SET @sql := IF(@col = 0,
  'ALTER TABLE mediciones ADD COLUMN foto_url VARCHAR(500) NULL AFTER observaciones',
  'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @col := (SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'lecturas' AND COLUMN_NAME = 'foto_url');
SET @sql := IF(@col = 0,
  'ALTER TABLE lecturas ADD COLUMN foto_url VARCHAR(500) NULL AFTER irregular',
  'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @col := (SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'actividades_planta' AND COLUMN_NAME = 'foto_url');
SET @sql := IF(@col = 0,
  'ALTER TABLE actividades_planta ADD COLUMN foto_url VARCHAR(500) NULL AFTER evidencia',
  'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

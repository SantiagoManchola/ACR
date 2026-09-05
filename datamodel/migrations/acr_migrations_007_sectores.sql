-- 007: catálogo administrable de sectores (clasificación de suscriptores).
-- Re-ejecutable: crea la tabla si no existe, inserta los base solo si faltan
-- y normaliza sectores históricos de suscriptores al nombre canónico.
CREATE TABLE IF NOT EXISTS sectores (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  nombre        VARCHAR(80) NOT NULL UNIQUE,
  estado        ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',
  created_by    INT,
  updated_by    INT,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_sec_created FOREIGN KEY (created_by) REFERENCES usuarios(id) ON DELETE SET NULL,
  CONSTRAINT fk_sec_updated FOREIGN KEY (updated_by) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO sectores (nombre) VALUES
  ('ALBANIA'),
  ('LA ISLA'),
  ('MIRAMAR'),
  ('ORQUIDEAS'),
  ('RICAURTE'),
  ('VILLA BARBARA');

-- Normaliza valores históricos de texto libre al canónico del catálogo
-- (insensible a mayúsculas/espacios). Lo no reconocido se conserva tal cual.
UPDATE suscriptores su
  JOIN sectores se ON LOWER(TRIM(su.sector)) = LOWER(se.nombre)
  SET su.sector = se.nombre
  WHERE su.sector IS NOT NULL;

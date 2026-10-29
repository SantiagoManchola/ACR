-- 010: estado operativo del diagrama de la planta de tratamiento.
--
-- Agrega el catálogo de partes de la planta (`componentes_planta`) y el
-- historial inmutable de cambios de estado (`estados_componente_planta`).
-- El estado actual de una parte es su último evento.
--
-- Aplicar sobre una BD ya creada con `acr_migrations.sql`:
--   mysql -u <usuario> -p <basedatos> < acr_migrations_010_estado_planta.sql
--
-- También está consolidado en `acr_migrations.sql` para instalaciones nuevas.

CREATE TABLE IF NOT EXISTS componentes_planta (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  nombre       VARCHAR(100) NOT NULL,
  descripcion  VARCHAR(255),
  orden        INT NOT NULL DEFAULT 0,
  estado       ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',
  created_by   INT,
  updated_by   INT,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_componente_nombre (nombre),
  KEY idx_comp_orden (orden),
  CONSTRAINT fk_comp_created FOREIGN KEY (created_by) REFERENCES usuarios(id) ON DELETE SET NULL,
  CONSTRAINT fk_comp_updated FOREIGN KEY (updated_by) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS estados_componente_planta (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  componente_id  INT NOT NULL,
  estado         ENUM('funcionando','afectacion','fuera_servicio') NOT NULL,
  nota           TEXT,
  fecha          DATE NOT NULL,
  hora           TIME,
  responsable_id INT,
  created_by     INT,
  updated_by     INT,
  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_estado_comp       (componente_id),
  KEY idx_estado_comp_fecha (componente_id, fecha, hora),
  KEY idx_estado_fecha      (fecha, estado),
  CONSTRAINT fk_estado_comp    FOREIGN KEY (componente_id) REFERENCES componentes_planta(id) ON DELETE RESTRICT,
  CONSTRAINT fk_estado_resp    FOREIGN KEY (responsable_id) REFERENCES usuarios(id)            ON DELETE SET NULL,
  CONSTRAINT fk_estado_created FOREIGN KEY (created_by)    REFERENCES usuarios(id)            ON DELETE SET NULL,
  CONSTRAINT fk_estado_updated FOREIGN KEY (updated_by)    REFERENCES usuarios(id)            ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Partes iniciales (idempotente por nombre único). El admin puede
-- renombrarlas, reordenarlas, desactivarlas o agregar más desde el CMS.
INSERT IGNORE INTO componentes_planta (nombre, orden, estado) VALUES
  ('Fuente de abastecimiento quebrada', 1, 'activo'),
  ('Bocatoma', 2, 'activo'),
  ('Red de aducción', 3, 'activo'),
  ('Desarenador', 4, 'activo'),
  ('Sistema de coagulación', 5, 'activo'),
  ('Tanque de floculación', 6, 'activo'),
  ('Sedimentador', 7, 'activo'),
  ('Red de conducción', 8, 'activo'),
  ('Sistema de desinfección', 9, 'activo'),
  ('Tanques de almacenamiento', 10, 'activo');

-- Estado inicial "En funcionamiento" para las partes que todavía no tienen
-- historial (incluye las que se acaban de sembrar). Se hace con un INSERT
-- directo para no crear tablas temporales sin PRIMARY KEY: algunos servidores
-- de producción tienen `sql_require_primary_key=ON` y rechazan esas tablas.
INSERT INTO estados_componente_planta (componente_id, estado, nota, fecha, hora)
SELECT c.id, 'funcionando', 'Estado inicial',
       DATE(UTC_TIMESTAMP() - INTERVAL 5 HOUR),
       TIME(UTC_TIMESTAMP() - INTERVAL 5 HOUR)
FROM componentes_planta c
LEFT JOIN estados_componente_planta e ON e.componente_id = c.id
WHERE e.id IS NULL AND c.estado = 'activo';

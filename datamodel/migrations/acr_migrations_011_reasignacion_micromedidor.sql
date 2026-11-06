-- 011: auditoría de correcciones de asignación suscriptor-medidor.
--
-- Permite que admin/administrativo corrijan un medidor asignado a la persona
-- equivocada. La operación mueve también todas las lecturas del medidor al
-- suscriptor correcto (no borra ninguna) y deja este registro de auditoría:
-- quién hizo el cambio, de qué suscriptor a cuál, cuántas lecturas se movieron
-- y el motivo opcional.
--
-- Aplicar sobre una BD ya creada con `acr_migrations.sql`:
--   mysql -u <usuario> -p <basedatos> < acr_migrations_011_reasignacion_micromedidor.sql
--
-- También está consolidado en `acr_migrations.sql` para instalaciones nuevas.

CREATE TABLE IF NOT EXISTS reasignaciones_micromedidor (
  id                      INT AUTO_INCREMENT PRIMARY KEY,
  micromedidor_id         INT NOT NULL,
  suscriptor_anterior_id  INT NULL,
  suscriptor_nuevo_id     INT NULL,
  lecturas_movidas        INT NOT NULL DEFAULT 0,
  motivo                  VARCHAR(255) NULL,
  created_by              INT NULL,
  updated_by              INT NULL,
  created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_reasig_mm_fecha (micromedidor_id, created_at),
  CONSTRAINT fk_reasig_mm      FOREIGN KEY (micromedidor_id)        REFERENCES micromedidores(id) ON DELETE RESTRICT,
  CONSTRAINT fk_reasig_ant     FOREIGN KEY (suscriptor_anterior_id) REFERENCES suscriptores(id)  ON DELETE RESTRICT,
  CONSTRAINT fk_reasig_nuevo   FOREIGN KEY (suscriptor_nuevo_id)    REFERENCES suscriptores(id)  ON DELETE RESTRICT,
  CONSTRAINT fk_reasig_created FOREIGN KEY (created_by)             REFERENCES usuarios(id)       ON DELETE SET NULL,
  CONSTRAINT fk_reasig_updated FOREIGN KEY (updated_by)             REFERENCES usuarios(id)       ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- ACR — Acueducto Comunitario Acuaricaurte
-- Esquema de base de datos (MySQL)
-- ----------------------------------------------------------------------------
-- Archivo ÚNICO y editablE: representa el estado actual del esquema.
-- Cuando el modelo cambie, se edita directamente la tabla aquí y en
-- datamodel/acr.dbml (el diseño fuente). El historial de versiones lo lleva
-- Git/GitHub, no este archivo.
--
-- Aplicar / recrear:
--   mysql -u <user> -p acr < datamodel/migrations/acr_migrations.sql
-- ============================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------- Autenticación / admin ------------------------
CREATE TABLE IF NOT EXISTS roles (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  nombre       VARCHAR(50)  NOT NULL UNIQUE,
  descripcion  TEXT,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS permisos (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  codigo       VARCHAR(50)  NOT NULL UNIQUE,
  descripcion  TEXT,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS usuarios (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  nombre          VARCHAR(150) NOT NULL,
  identificacion  VARCHAR(30),
  username        VARCHAR(50)  NOT NULL UNIQUE,
  password_hash   VARCHAR(255) NOT NULL,
  rol_id          INT NOT NULL,
  estado          ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',
  ultimo_acceso   TIMESTAMP NULL,
  created_by      INT,
  updated_by      INT,
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_usuarios_rol (rol_id),
  CONSTRAINT fk_usuarios_rol      FOREIGN KEY (rol_id)     REFERENCES roles(id)      ON DELETE RESTRICT,
  CONSTRAINT fk_usuarios_created   FOREIGN KEY (created_by) REFERENCES usuarios(id)  ON DELETE SET NULL,
  CONSTRAINT fk_usuarios_updated   FOREIGN KEY (updated_by) REFERENCES usuarios(id)  ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS rol_permisos (
  rol_id       INT NOT NULL,
  permiso_id   INT NOT NULL,
  PRIMARY KEY (rol_id, permiso_id),
  CONSTRAINT fk_rp_rol     FOREIGN KEY (rol_id)    REFERENCES roles(id)    ON DELETE CASCADE,
  CONSTRAINT fk_rp_permiso FOREIGN KEY (permiso_id) REFERENCES permisos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------- Inventario ------------------------------------
CREATE TABLE IF NOT EXISTS categorias_inventario (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  nombre       VARCHAR(100) NOT NULL,
  tipo         ENUM('equipo','herramienta','laboratorio','accesorio','insumo') NOT NULL,
  descripcion  TEXT,
  created_by   INT,
  updated_by   INT,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_cat_created (created_by),
  CONSTRAINT fk_cat_created FOREIGN KEY (created_by) REFERENCES usuarios(id) ON DELETE SET NULL,
  CONSTRAINT fk_cat_updated FOREIGN KEY (updated_by) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS elementos_inventario (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  nombre         VARCHAR(150) NOT NULL,
  categoria_id   INT NOT NULL,
  unidad         VARCHAR(20),
  proveedor      VARCHAR(150),
  valor          DECIMAL(14,2),
  minimo         DECIMAL(12,2),
  estado         ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',
  observaciones  TEXT,
  created_by     INT,
  updated_by     INT,
  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_elem_categoria (categoria_id),
  CONSTRAINT fk_elem_cat     FOREIGN KEY (categoria_id) REFERENCES categorias_inventario(id) ON DELETE RESTRICT,
  CONSTRAINT fk_elem_created FOREIGN KEY (created_by)   REFERENCES usuarios(id)              ON DELETE SET NULL,
  CONSTRAINT fk_elem_updated FOREIGN KEY (updated_by)   REFERENCES usuarios(id)              ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ubicaciones (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  nombre       VARCHAR(100) NOT NULL UNIQUE,
  descripcion  TEXT,
  created_by   INT,
  updated_by   INT,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_ub_created (created_by),
  CONSTRAINT fk_ub_created FOREIGN KEY (created_by) REFERENCES usuarios(id) ON DELETE SET NULL,
  CONSTRAINT fk_ub_updated FOREIGN KEY (updated_by) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Existencias del MISMO producto en cada ubicación (un producto puede estar en N lugares)
CREATE TABLE IF NOT EXISTS stock_ubicacion (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  elemento_id    INT NOT NULL,
  ubicacion_id   INT NOT NULL,
  cantidad       DECIMAL(12,2) NOT NULL DEFAULT 0,
  created_by     INT,
  updated_by     INT,
  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_stock_elem_ubi (elemento_id, ubicacion_id),
  KEY idx_su_elem (elemento_id),
  KEY idx_su_ubi (ubicacion_id),
  CONSTRAINT fk_su_elem    FOREIGN KEY (elemento_id)  REFERENCES elementos_inventario(id) ON DELETE CASCADE,
  CONSTRAINT fk_su_ubi     FOREIGN KEY (ubicacion_id) REFERENCES ubicaciones(id)          ON DELETE RESTRICT,
  CONSTRAINT fk_su_created FOREIGN KEY (created_by)   REFERENCES usuarios(id)             ON DELETE SET NULL,
  CONSTRAINT fk_su_updated FOREIGN KEY (updated_by)   REFERENCES usuarios(id)             ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS traslados (
  id                    INT AUTO_INCREMENT PRIMARY KEY,
  elemento_id           INT NOT NULL,
  ubicacion_origen_id   INT NOT NULL,
  ubicacion_destino_id  INT NOT NULL,
  cantidad              DECIMAL(12,2) NOT NULL,
  responsable_id        INT,
  observaciones         TEXT,
  fecha                 DATE NOT NULL,
  hora                  TIME,
  created_by            INT,
  updated_by            INT,
  created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_trasl_fecha (fecha),
  CONSTRAINT fk_trasl_elem  FOREIGN KEY (elemento_id)           REFERENCES elementos_inventario(id) ON DELETE RESTRICT,
  CONSTRAINT fk_trasl_orig  FOREIGN KEY (ubicacion_origen_id)  REFERENCES ubicaciones(id)          ON DELETE RESTRICT,
  CONSTRAINT fk_trasl_dest  FOREIGN KEY (ubicacion_destino_id) REFERENCES ubicaciones(id)          ON DELETE RESTRICT,
  CONSTRAINT fk_trasl_resp  FOREIGN KEY (responsable_id)     REFERENCES usuarios(id)           ON DELETE SET NULL,
  CONSTRAINT fk_trasl_created FOREIGN KEY (created_by)       REFERENCES usuarios(id)           ON DELETE SET NULL,
  CONSTRAINT fk_trasl_updated FOREIGN KEY (updated_by)       REFERENCES usuarios(id)           ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS movimientos_inventario (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  elemento_id   INT NOT NULL,
  ubicacion_id  INT NOT NULL,
  tipo          ENUM('entrada','salida') NOT NULL,
  cantidad      DECIMAL(12,2) NOT NULL,
  responsable_id INT,
  motivo        VARCHAR(150),
  observaciones TEXT,
  fecha         DATE NOT NULL,
  hora          TIME,
  created_by    INT,
  updated_by    INT,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_mov_elemento     (elemento_id),
  KEY idx_mov_fecha_elem   (fecha, elemento_id),
  CONSTRAINT fk_mov_elem    FOREIGN KEY (elemento_id)  REFERENCES elementos_inventario(id) ON DELETE RESTRICT,
  CONSTRAINT fk_mov_ubi     FOREIGN KEY (ubicacion_id) REFERENCES ubicaciones(id)          ON DELETE RESTRICT,
  CONSTRAINT fk_mov_resp    FOREIGN KEY (responsable_id) REFERENCES usuarios(id)           ON DELETE SET NULL,
  CONSTRAINT fk_mov_created FOREIGN KEY (created_by)    REFERENCES usuarios(id)           ON DELETE SET NULL,
  CONSTRAINT fk_mov_updated FOREIGN KEY (updated_by)    REFERENCES usuarios(id)           ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------- Micromedidores -------------------------------
CREATE TABLE IF NOT EXISTS suscriptores (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  nombre            VARCHAR(150) NOT NULL,
  identificacion    VARCHAR(30),
  codigo_usuario    VARCHAR(30) UNIQUE,
  codigo_facturacion VARCHAR(30),
  tipo_usuario      ENUM('residencial','comercial','otro') NOT NULL DEFAULT 'residencial',
  sector            VARCHAR(80),
  direccion         VARCHAR(200),
  estado            ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',
  created_by        INT,
  updated_by        INT,
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_sub_sector  (sector),
  KEY idx_sub_codigo (codigo_usuario),
  CONSTRAINT fk_sub_created FOREIGN KEY (created_by) REFERENCES usuarios(id) ON DELETE SET NULL,
  CONSTRAINT fk_sub_updated FOREIGN KEY (updated_by) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS micromedidores (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  serial            VARCHAR(50) NOT NULL UNIQUE,
  tipo              VARCHAR(50),
  suscriptor_id     INT,
  direccion         VARCHAR(200),
  fecha_instalacion DATE,
  estado            ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',
  created_by        INT,
  updated_by        INT,
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_mm_suscriptor (suscriptor_id),
  CONSTRAINT fk_mm_suscriptor FOREIGN KEY (suscriptor_id) REFERENCES suscriptores(id) ON DELETE RESTRICT,
  CONSTRAINT fk_mm_created    FOREIGN KEY (created_by)   REFERENCES usuarios(id)    ON DELETE SET NULL,
  CONSTRAINT fk_mm_updated    FOREIGN KEY (updated_by)   REFERENCES usuarios(id)    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS lecturas (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  micromedidor_id INT NOT NULL,
  suscriptor_id   INT NOT NULL,
  fecha           DATE NOT NULL,
  hora            TIME,
  lectura         DECIMAL(12,3) NOT NULL,
  consumo         DECIMAL(12,3),
  promedio_usado  TINYINT(1) NOT NULL DEFAULT 0,
  responsable_id  INT,
  novedad         VARCHAR(200),
  irregular       TINYINT(1) NOT NULL DEFAULT 0,
  created_by      INT,
  updated_by      INT,
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_lec_mm        (micromedidor_id),
  KEY idx_lec_sub       (suscriptor_id),
  KEY idx_lec_fecha_mm  (fecha, micromedidor_id),
  CONSTRAINT fk_lec_mm      FOREIGN KEY (micromedidor_id) REFERENCES micromedidores(id) ON DELETE RESTRICT,
  CONSTRAINT fk_lec_sub     FOREIGN KEY (suscriptor_id)   REFERENCES suscriptores(id)   ON DELETE RESTRICT,
  CONSTRAINT fk_lec_resp    FOREIGN KEY (responsable_id)  REFERENCES usuarios(id)        ON DELETE SET NULL,
  CONSTRAINT fk_lec_created FOREIGN KEY (created_by)       REFERENCES usuarios(id)        ON DELETE SET NULL,
  CONSTRAINT fk_lec_updated FOREIGN KEY (updated_by)       REFERENCES usuarios(id)        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------- Planta de tratamiento ------------------------
CREATE TABLE IF NOT EXISTS dosificaciones (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  elemento_id   INT NOT NULL,
  cantidad      DECIMAL(12,2) NOT NULL,
  unidad        VARCHAR(20),
  fecha         DATE NOT NULL,
  hora          TIME,
  responsable_id INT,
  observaciones TEXT,
  created_by    INT,
  updated_by    INT,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_dos_elem       (elemento_id),
  KEY idx_dos_fecha_elem (fecha, elemento_id),
  CONSTRAINT fk_dos_elem    FOREIGN KEY (elemento_id)   REFERENCES elementos_inventario(id) ON DELETE RESTRICT,
  CONSTRAINT fk_dos_resp    FOREIGN KEY (responsable_id) REFERENCES usuarios(id)            ON DELETE SET NULL,
  CONSTRAINT fk_dos_created FOREIGN KEY (created_by)    REFERENCES usuarios(id)            ON DELETE SET NULL,
  CONSTRAINT fk_dos_updated FOREIGN KEY (updated_by)    REFERENCES usuarios(id)            ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS parametros_planta (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  nombre       VARCHAR(80) NOT NULL,
  tipo_agua    ENUM('cruda','tratada') NOT NULL,
  unidad       VARCHAR(20),
  valor_min    DECIMAL(12,4),
  valor_max    DECIMAL(12,4),
  estado       ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',
  created_by   INT,
  updated_by   INT,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_pp_created FOREIGN KEY (created_by) REFERENCES usuarios(id) ON DELETE SET NULL,
  CONSTRAINT fk_pp_updated FOREIGN KEY (updated_by) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS mediciones (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  parametro_id      INT NOT NULL,
  valor             DECIMAL(12,4) NOT NULL,
  fecha             DATE NOT NULL,
  hora              TIME,
  responsable_id    INT,
  fuera_rango       TINYINT(1) NOT NULL DEFAULT 0,
  accion_correctiva TEXT,
  observaciones     TEXT,
  created_by        INT,
  updated_by        INT,
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_med_param      (parametro_id),
  KEY idx_med_fecha_param (fecha, parametro_id),
  CONSTRAINT fk_med_param    FOREIGN KEY (parametro_id)  REFERENCES parametros_planta(id) ON DELETE RESTRICT,
  CONSTRAINT fk_med_resp     FOREIGN KEY (responsable_id) REFERENCES usuarios(id)           ON DELETE SET NULL,
  CONSTRAINT fk_med_created  FOREIGN KEY (created_by)    REFERENCES usuarios(id)           ON DELETE SET NULL,
  CONSTRAINT fk_med_updated  FOREIGN KEY (updated_by)    REFERENCES usuarios(id)           ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS actividades_planta (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  tipo          VARCHAR(80) NOT NULL,
  fecha         DATE NOT NULL,
  hora          TIME,
  responsable_id INT,
  estado        ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',
  observaciones TEXT,
  evidencia     VARCHAR(255),
  created_by    INT,
  updated_by    INT,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_act_fecha_tipo (fecha, tipo),
  CONSTRAINT fk_act_resp    FOREIGN KEY (responsable_id) REFERENCES usuarios(id) ON DELETE SET NULL,
  CONSTRAINT fk_act_created FOREIGN KEY (created_by)    REFERENCES usuarios(id) ON DELETE SET NULL,
  CONSTRAINT fk_act_updated FOREIGN KEY (updated_by)    REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS horas_servicio (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  fecha         DATE NOT NULL,
  horas         DECIMAL(6,2) NOT NULL,
  responsable_id INT,
  observaciones TEXT,
  created_by    INT,
  updated_by    INT,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_hs_fecha (fecha),
  CONSTRAINT fk_hs_resp    FOREIGN KEY (responsable_id) REFERENCES usuarios(id) ON DELETE SET NULL,
  CONSTRAINT fk_hs_created FOREIGN KEY (created_by)    REFERENCES usuarios(id) ON DELETE SET NULL,
  CONSTRAINT fk_hs_updated FOREIGN KEY (updated_by)    REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;

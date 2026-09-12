-- 008: agrega 'oficial' al catálogo de tipo de usuario de suscriptores.
-- El sistema tenía residencial/comercial/otro; la base real usa OFICIAL.
ALTER TABLE suscriptores
  MODIFY COLUMN tipo_usuario ENUM('residencial','comercial','otro','oficial') NOT NULL DEFAULT 'residencial';

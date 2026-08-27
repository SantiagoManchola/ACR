# Plan Fase 2 — Modelo de datos (dbdiagram.io)

> Entregable: `datamodel/acr.dbml` + SQL PostgreSQL. Agente: `agents/datamodel-agent.md`.

---

## Objetivo
Convertir los módulos y reglas de `docs/01-alcance.md` en un modelo DBML visual en
[dbdiagram.io](https://dbdiagram.io/), y exportarlo a SQL de PostgreSQL listo para la API.

## Entidades propuestas (borrador)

### Administración / seguridad
- `usuarios` (id, nombre, identificacion, username, password_hash, rol_id, estado, ...)
- `roles` (id, nombre, descripcion)
- `permisos` (id, codigo, descripcion)  — o unión rol↔permiso
- `auditoria` (id, usuario_id, accion, tabla, registro_id, fecha, detalle)  [opcional]

### Inventario
- `categorias_inventario` (id, nombre, tipo: equipo/herramienta/lab/accesorio)
- `elementos_inventario` (id, nombre, categoria_id, tipo, ubicacion, cantidad,
  proveedor, valor, estado, minimo, created_by, updated_by, timestamps)
- `movimientos_inventario` (id, elemento_id, tipo: entrada/salida, cantidad,
  responsable_id, motivo, observaciones, fecha, created_by, timestamps)

### Micromedidores
- `suscriptores` (id, nombre, identificacion, codigo_usuario, codigo_facturacion,
  tipo_usuario, sector, direccion, estado)
- `micromedidores` (id, serial, tipo, suscriptor_id, direccion, fecha_instalacion, estado)
- `lecturas` (id, micromedidor_id, suscriptor_id, fecha, hora, lectura, consumo,
  responsable_id, promedio_usado: bool, novedad, created_by, timestamps)
- `novedades_lectura` (id, lectura_id, tipo, descripcion)  [opcional, o campo en lecturas]

### Planta de tratamiento
- `parametros_planta` (id, nombre, tipo_agua: cruda/tratada, unidad, valor_min, valor_max, estado)
- `mediciones` (id, parametro_id, valor, fecha, hora, responsable_id, fuera_rango: bool,
  accion_correctiva, observaciones, created_by, timestamps)
- `productos_quimicos` (id, nombre, unidad, cantidad_disponible, ...)
- `dosificaciones` (id, producto_id, cantidad, fecha, hora, responsable_id, observaciones)
- `actividades_planta` (id, tipo, fecha, hora, responsable_id, estado, observaciones, evidencia)
- `horas_servicio` (id, fecha, horas, responsable_id, observaciones)

## Reglas a reflejar en el modelo
- Relaciones: suscriptor 1─* micromedidores; micromedidor 1─* lecturas;
  elemento 1─* movimientos; parámetro 1─* mediciones; producto 1─* dosificaciones.
- Cada tabla transaccional lleva `created_by` / `updated_by` (trazabilidad, RNF-07).
- `estado` (activo/inactivo) para soft delete donde aplique (regla de negocio 14).
- Índices sugeridos: `lecturas(fecha, micromedidor_id)`, `mediciones(fecha, parametro_id)`,
  `movimientos_inventario(fecha, elemento_id)`, `suscriptores(sector)`.

## Criterio de aceptación
- [ ] El diagrama abre en dbdiagram.io sin errores.
- [ ] Cubre todos los RF de `docs/01-alcance.md`.
- [ ] SQL PostgreSQL generado y revisado.
- [ ] Nombres y tipos acordes a PostgreSQL.
- [ ] Se entrega a la Fase 3 como fuente del esquema.

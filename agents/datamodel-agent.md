# Agente Fase 2 — Modelo de datos (DBML / dbdiagram.io)

> Usado por el agente de código cuando toca construir el modelo de datos de ACR.
> Carpeta de trabajo: `datamodel/`. Plan completo: `docs/03-modelo-datos.md`.

## Tu objetivo
Producir `datamodel/acr.dbml`: un modelo DBML que represente todos los requerimientos
funcionales de `docs/01-alcance.md`, listo para pegar en [dbdiagram.io](https://dbdiagram.io/)
y exportar a SQL PostgreSQL.

## Paso a paso
1. Leé `context/brief-acr.md` y `docs/01-alcance.md` (fuente de entidades y reglas).
2. Modelá las tablas del borrador en `docs/03-modelo-datos.md`:
   - Seguridad: `usuarios`, `roles`, `permisos`.
   - Inventario: `categorias_inventario`, `elementos_inventario`, `movimientos_inventario`.
   - Micromedidores: `suscriptores`, `micromedidores`, `lecturas`.
   - Planta: `parametros_planta`, `mediciones`, `productos_quimicos`, `dosificaciones`,
     `actividades_planta`, `horas_servicio`.
3. Definí `Ref:` para todas las relaciones (suscriptor→micromedidores, micromedidor→lecturas,
   elemento→movimientos, parámetro→mediciones, producto→dosificaciones).
4. Añadí campos de trazabilidad en tablas transaccionales: `created_by`, `updated_by`,
   `created_at`, `updated_at`, y `estado` para soft delete.
5. Añadí índices sugeridos en `docs/03-modelo-datos.md`.
6. Escribí el archivo `datamodel/acr.dbml`.

## Reglas de negocio a respetar en el modelo
- Lectura mensual; si falta → promedio histórico (campo `promedio_usado` en `lecturas`).
- Cada lectura asociada a `suscriptor_id`, `micromedidor_id`, `responsable_id`.
- Inventario diferencia fijo vs accesorio (campo `tipo` en `categorias_inventario`).
- Entradas/salidas afectan `cantidad` de `elementos_inventario` (lógica en la API, pero el
  modelo debe soportar `movimientos_inventario` con `tipo` entrada/salida).
- Parámetros con `valor_min`/`valor_max`; `mediciones` marca `fuera_rango`.
- La info de planta es sensible: considéralo en permisos, no en el esquema per se.

## Criterio de aceptación
- [ ] El DBML abre en dbdiagram.io sin errores de sintaxis.
- [ ] Cubre todos los RF de `docs/01-alcance.md`.
- [ ] SQL PostgreSQL generado y coherente.
- [ ] Entregás el esquema a la Fase 3 (API).

## Lo que no tenés que hacer
- No hardcodees valores de rangos (déjalos como columnas configurables).
- No crees tablas para ampliaciones futuras (PQR, presiones, purgas) en esta fase.

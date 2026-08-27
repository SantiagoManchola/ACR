# Ruta de construcción paso a paso — ACR

> Documento maestro del proyecto. Describe el orden de las fases y qué hacer en cada una.
> Cada fase tiene su agente (ver `AGENTS.md`).

---

## Índice de la construcción

| Paso | Fase | Entregable | Carpeta | Agente |
|---|---|---|---|---|
| 0 | Setup | Estructura, brief, contexto, marca | raíz + `context/` | orquestador |
| 1 | Documentación | Docs paso a paso + manual | `docs/` | orquestador |
| 2 | Modelo de datos | Diagrama DBML + SQL | `datamodel/` | `agents/datamodel-agent.md` |
| 3 | API | Backend FastAPI + PostgreSQL | `api/` | `agents/api-agent.md` |
| 4 | CMS | Panel web (SPA) | `cms/` | `agents/cms-agent.md` |

---

## Paso 0 — Setup del proyecto (HECHO)

1. Crear carpeta `ACR-acueducto-comunitario/` con subcarpetas: `context/`, `docs/`,
   `agents/`, `datamodel/`, `api/`, `cms/`.
2. Escribir `context/marca-acr.md` (investigación + paleta `#2160AD`/blanco).
3. Escribir `context/brief-acr.md` (resumen de negocio y alcance).
4. Escribir `brief-acr.md` (brief ejecutable por agente).
5. Escribir `AGENTS.md` y `agents/*.md`.
6. Escribir `README.md` y `CLAUDE.md`.

## Paso 1 — Documentación paso a paso (ESTE ARCHIVO + docs/)

- `docs/00-ruta-de-construccion.md` (este archivo).
- `docs/01-alcance.md` — módulos, actores, reglas de negocio.
- `docs/02-arquitectura.md` — visión técnica de conjunto.
- `docs/03-modelo-datos.md` — plan de la Fase 2.
- `docs/04-api.md` — plan de la Fase 3.
- `docs/05-cms.md` — plan de la Fase 4.
- `docs/manual-de-usuario.md` — manual para los actores de Acuaricaurte.

## Paso 2 — Modelo de datos (Fase 2, siguiente)

**Responsable:** `agents/datamodel-agent.md`.

1. Leer `context/brief-acr.md` y `docs/01-alcance.md` (fuente de entidades y reglas).
2. Traducir cada módulo a tablas DBML:
   - `usuarios`, `roles`, `permisos` (auth/admin).
   - `categorias_inventario`, `elementos_inventario`, `movimientos_inventario`.
   - `suscriptores`, `micromedidores`, `lecturas`, `novedades_lectura`.
   - `parametros_planta`, `rangos_parametros`, `dosificaciones`, `productos_quimicos`,
     `actividades_planta`, `horas_servicio`.
   - Tablas de auditoría donde aplique.
3. Definir relaciones, claves, índices y `created_by`/`updated_by`/`created_at`.
4. Exportar a `datamodel/acr.dbml` y generar SQL PostgreSQL.
5. Verificar en dbdiagram.io que el diagrama es coherente con los requerimientos.
6. Pasar el esquema validado a la Fase 3.

## Paso 3 — API (Fase 3)

**Responsable:** `agents/api-agent.md`.

1. Inicializar proyecto FastAPI en `api/`.
2. Crear conexión a PostgreSQL y ejecutar el SQL de la Fase 2.
3. Implementar auth (JWT, roles, permisos) — base transversal.
4. Implementar módulos en orden de prioridad alta (ver `docs/01-alcance.md`):
   auth/admin → inventario → micromedidores → planta → reportes.
5. Validaciones Pydantic que reflejen reglas de negocio (lectura mensual, promedio histórico,
   soft delete, alertas de rango).
6. Endpoints de exportación (CSV/Excel/PDF) para reportes.
7. Tests de los endpoints críticos. Documentación OpenAPI (Swagger) automática.

## Paso 4 — CMS / Panel web (Fase 4)

**Responsable:** `agents/cms-agent.md`.

1. Inicializar SPA (Vue 3 + Pinia + Vite) en `cms/`.
2. Tema con variables `--acr-azul:#2160AD` y `--acr-blanco:#FFFFFF`.
3. Login + control de menús por rol.
4. CRUD de cada módulo consumiendo la API de la Fase 3.
5. Pantallas de registro rápido para fontaneros/operarios (móvil).
6. Pantallas de reportes con filtros y exportación.
7. Indicadores/alertas (inventario bajo, parámetros fuera de rango).

---

## Cómo avanzar entre fases

- El agente de una fase **no empieza** hasta que la anterior dejó su entregable validado.
- Cada fase lee los documentos de `context/` y `docs/` como fuente de verdad.
- Los agentes viven en `AGENTS.md` (orquestador) y `agents/*.md` (especializados).

## Riesgos y decisiones pendientes

- Definir valores reales de rangos de parámetros (pH min/max, cloro, turbiedad) con la org.
- Definir umbrales de alerta de inventario por elemento.
- Confirmar stack (FastAPI/Vue 3) o ajustar antes de Fase 3.
- Definir política de respaldos y entorno de producción.

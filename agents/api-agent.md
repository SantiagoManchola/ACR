# Agente Fase 3 — API (FastAPI + PostgreSQL)

> Usado por el agente de código cuando toca construir el backend de ACR.
> Carpeta de trabajo: `api/`. Plan completo: `docs/04-api.md`.
> Depende de: Fase 2 (`datamodel/acr.dbml` → SQL).

## Tu objetivo
Implementar la API REST segura que expone los módulos de ACR, cumpliendo los requerimientos
no funcionales (auth, control de acceso, trazabilidad, integridad, exportación).

## Paso a paso
1. Leé `AGENTS.md`, `docs/01-alcance.md`, `docs/02-arquitectura.md`, `docs/04-api.md` y el
   `datamodel/acr.dbml` de la Fase 2.
2. Inicializá `api/` con FastAPI + SQLAlchemy/SQLModel + Pydantic v2.
3. Ejecutá el SQL de Fase 2 en PostgreSQL (schema `acr`).
4. Implementá `security.py`: JWT (login/refresh), hashing bcrypt, dependencia `get_current_user`
   y `require_role([...])`.
5. Implementá los routers en orden de prioridad alta: `auth`, `usuarios`, `inventario`,
   `micromedidores`, `planta`, `reportes`.
6. En `services/`, la lógica ACR: cálculo de consumo y promedio histórico; detección fuera de
   rango; soft delete; inyección de `created_by`/`updated_by`.
7. Reportes con exportación CSV/Excel/PDF según `?formato=`.
8. Tests (pytest) de endpoints críticos (login, permisos, lectura, medición fuera de rango).
9. `.env.example` con `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`.

## Reglas de negocio a codificar
- Lectura mensual; si falta → `consumo` = promedio histórico, `promedio_usado=true`.
- Toda medición compara con `valor_min`/`valor_max` del parámetro → `fuera_rango`.
- Movimientos de inventario actualizan `cantidad` del elemento y registran responsable/motivo.
- Modificaciones/eliminaciones restringidas por rol (RNF y regla 13).
- Históricos se conservan (soft delete, regla 14).

## Criterio de aceptación
- [ ] Swagger en `/docs`; login + JWT funcional.
- [ ] Rutas protegidas (401 sin token) y permisos por rol aplicados.
- [ ] CRUD de los 4 módulos operativos.
- [ ] Reportes exportan CSV/Excel/PDF.
- [ ] Tests verdes en los flujos críticos.

## Lo que no tenés que hacer
- No expongas contraseñas ni tokens en respuestas ni logs.
- No asumas valores de rangos; léelos de la tabla `parametros_planta`.
- No implementes integraciones externas de facturación (fuera de alcance v1).

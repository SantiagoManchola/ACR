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
| 3 | API | Backend FastAPI + MySQL | `api/` | `agents/api-agent.md` |
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
   - `parametros_planta`, `rangos_parametros`, `dosificaciones`,
      `actividades_planta`, `horas_servicio`. Los químicos viven en
      `elementos_inventario` (categoría tipo `insumo`).
   - Tablas de auditoría donde aplique.
3. Definir relaciones, claves, índices y `created_by`/`updated_by`/`created_at`.
4. Exportar a `datamodel/acr.dbml` y generar SQL MySQL.
5. Verificar en dbdiagram.io que el diagrama es coherente con los requerimientos.
6. Pasar el esquema validado a la Fase 3.

## Paso 3 — API (Fase 3) — ✅ CÓDIGO GENERADO (pendiente de ejecutar contra BD)

**Responsable:** `agents/api-agent.md`. **Estado:** implementación completa en `api/`
(FastAPI + SQLAlchemy 2.0 + MySQL + JWT + roles + reportes CSV/XLSX/PDF).
Falta ejecutar en un entorno con MySQL disponible.

Orden de arranque (ver `api/README.md` y `docs/04-api.md` para detalle):

0. **Crear la BD y correr el SQL** (prerrequisito, antes de arrancar el API):
   - `CREATE DATABASE acr CHARSET utf8mb4;` + usuario `acr_user`.
   - `mysql -u acr_user -p acr < datamodel/migrations/acr_migrations.sql`.
   - Definir `DATABASE_URL=mysql+pymysql://acr_user:acr_password@localhost:3306/acr`.
1. `pip install -r api/requirements.txt` e `cp api/.env.example api/.env`.
2. `python api/seed.py` → crea roles (`admin`, `administrativo`, `operario`,
   `fontanero`) y usuario admin desde env.
3. `uvicorn app.main:app --reload` (desde `api/`).
4. Swagger automático en **`/docs`**.
5. Auth JWT (HS256) + control de acceso por rol en todos los módulos.
6. Validaciones Pydantic (RNF-06), trazabilidad `created_by`/`updated_by` (RNF-07),
   soft delete con `estado`, y exportación CSV/XLSX/PDF (RNF-19) en `/reportes/*`.

## Paso 4 — CMS / Panel web (Fase 4) — ✅ IMPLEMENTADO

**Responsable:** `agents/cms-agent.md`. **Estado:** SPA completa en `cms/`,
compila con `npm run build` y sirve en `http://localhost:5173`.

Pasos realizados:

1. SPA inicializada (Vue 3 + Pinia + Vite) en `cms/` con tema de marca
   `--acr-azul:#2160AD` / `--acr-blanco:#FFFFFF` (`src/styles/theme.css`).
2. **Ejecutar el CMS apuntando a la API**: el CMS consume `VITE_API_URL`
   (por defecto `http://127.0.0.1:8000`). Levantar primero la API (Fase 3) y luego
   `cd cms && npm install && npm run dev`.
3. Login OAuth2 (`/auth/login`) con token JWT en `localStorage` + interceptor Axios
   que adjunta `Authorization: Bearer` y redirige a login ante 401.
4. Control de menús y rutas por rol (admin / administrativo / operario / fontanero)
   usando `GET /auth/me`.
5. Módulos: Inventario (elementos, entradas/salidas, movimientos, alertas),
   Micromedidores (suscriptores, medidores, lecturas, consumo por sector),
   Planta (parámetros, mediciones con `fuera_rango`, dosificaciones, actividades,
   horas de servicio), Reportes (filtros + exportar CSV/XLSX/PDF) y
   Usuarios/Roles (admin).
6. UI responsive para uso en campo (sidebar colapsable en móvil).
7. Indicadores/alertas: existencias bajo mínimo (rojo/ámbar) y mediciones fuera de rango.

Ver detalle en `docs/05-cms.md` y `cms/README.md`.

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

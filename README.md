# ACR — Acueducto Comunitario Acuaricaurte

Sistema de gestión operativa web para el acueducto comunitario del barrio Ricaurte, Ibagué,
Tolima, Colombia. Centraliza **inventario**, **micromedidores** y **planta de tratamiento**
con control de acceso por rol, trazabilidad y reportes exportables.

> Marca: azul `#2160AD` + blanco. Ver `context/marca-acr.md`.

## Estructura

| Carpeta | Contenido |
|---|---|
| `context/` | `brief-acr.md` (negocio) y `marca-acr.md` (investigación y paleta) |
| `docs/` | Ruta paso a paso, alcance, arquitectura, planes de fase, manual de usuario |
| `agents/` | Agentes especializados por fase (datamodel, api, cms) |
| `datamodel/` | Fase 2: `acr.dbml` (dbdiagram.io) |
| `api/` | Fase 3: backend FastAPI + MySQL |
| `cms/` | Fase 4: panel web (SPA) |

## Fases del proyecto

1. **Fase 1 (hecha):** estructura, contexto, brief, documentación y manual — orquestador (`AGENTS.md`).
2. **Fase 2:** modelo de datos DBML — `agents/datamodel-agent.md`.
3. **Fase 3:** API FastAPI — `agents/api-agent.md`.
4. **Fase 4:** CMS / panel web — `agents/cms-agent.md`.

Cada fase tiene su agente dedicado. Para empezar, leé `AGENTS.md` y luego
`docs/00-ruta-de-construccion.md`.

## Documentación clave

- Negocio y alcance: `context/brief-acr.md`, `docs/01-alcance.md`
- Arquitectura: `docs/02-arquitectura.md`
- Manual de usuario: `docs/manual-de-usuario.md`

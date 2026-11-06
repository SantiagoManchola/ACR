# ACR — Acueducto Comunitario Acuaricaurte

Sistema de gestión operativa web para el acueducto comunitario del barrio Ricaurte, Ibagué,
Tolima, Colombia. Centraliza **inventario**, **micromedidores** y **planta de tratamiento**
con control de acceso por rol, trazabilidad y reportes exportables. Incluye un **sitio web
público** con noticias administrables, historia, proceso del agua y canales de contacto.

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
| `web/` | Fase 5: sitio público Astro 7 (en desarrollo) |

## Fases del proyecto

1. **Fase 1 (hecha):** estructura, contexto, brief, documentación y manual — orquestador (`AGENTS.md`).
2. **Fase 2:** modelo de datos DBML — `agents/datamodel-agent.md`.
3. **Fase 3:** API FastAPI — `agents/api-agent.md`.
4. **Fase 4:** CMS / panel web — `agents/cms-agent.md`.
5. **Fase 5 (en desarrollo):** sitio web público — `agents/web-agent.md`. Plan en
   `docs/06-sitio-web.md`; herramientas y referencias en `docs/07-herramientas-y-referencias.md`.

Cada fase tiene su agente dedicado. Para empezar, leé `AGENTS.md` y luego
`docs/00-ruta-de-construccion.md`.

## Sitio web público (Fase 5)

```bash
cd web
nvm use 24
npm install
npm run dev        # http://localhost:4321
```

Requiere Node 22.23.4+ (recomendado 24). El sitio usa contenido local de
demostración hasta conectar el API público y el módulo de contenido del CMS.
Ver `web/README.md`, `docs/06-sitio-web.md` y `docs/07-herramientas-y-referencias.md`.

## Documentación clave

- Negocio y alcance: `context/brief-acr.md`, `docs/01-alcance.md`
- Arquitectura: `docs/02-arquitectura.md`
- Plan del sitio público: `docs/06-sitio-web.md`
- Herramientas y referencias: `docs/07-herramientas-y-referencias.md`
- Manual de usuario: `docs/manual-de-usuario.md`

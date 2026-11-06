# AGENTS.md

Instrucciones para el agente de código que abre este repo (Claude Code, Cursor, Codex, etc.).
Si sos ese agente: seguí esto antes de escribir código nuevo en el proyecto **ACR**.

## Contexto del proyecto

Este repo es el **Sistema de Gestión Operativa del Acueducto Comunitario Acuaricaurte (ACR)**,
una plataforma web para centralizar inventario, micromedidores y planta de tratamiento de un
acueducto comunitario de Ibagué, Tolima. Incluye además el **sitio web público** (Fase 5) con
noticias administrables, historia, proceso del agua y canales de contacto. No es un bot de
WhatsApp: el proyecto de referencia (`013_agente-whatsapp-ia`) solo se usó como **guía de
formato** para esta documentación.

La marca usa azul `#2160AD` + blanco (ver `context/marca-acr.md`). El alcance funcional y las
reglas de negocio están en `docs/01-alcance.md`; la arquitectura en `docs/02-arquitectura.md`.

## Estructura del repo

```
ACR-acueducto-comunitario/
  brief-acr.md            # brief ejecutable por agente
  context/
    brief-acr.md          # resumen de negocio y alcance
    marca-acr.md          # investigación y paleta de marca
  docs/
    00-ruta-de-construccion.md  # paso a paso de las fases
    01-alcance.md               # módulos, actores, reglas de negocio
    02-arquitectura.md          # visión técnica
    03-modelo-datos.md          # plan Fase 2
    04-api.md                   # plan Fase 3
    05-cms.md                   # plan Fase 4
    06-sitio-web.md             # plan Fase 5 (sitio público)
    07-herramientas-y-referencias.md # research, repos y IA de diseño
    manual-de-usuario.md        # manual para los actores
  agents/
    datamodel-agent.md   # agente Fase 2 (modelo de datos)
    api-agent.md         # agente Fase 3 (API)
    cms-agent.md         # agente Fase 4 (CMS)
    web-agent.md         # agente Fase 5 (sitio público)
  datamodel/   # Fase 2: acr.dbml
  api/         # Fase 3: FastAPI
  cms/         # Fase 4: SPA web
  web/         # Fase 5: Astro 7 (sitio público)
```

## Tu rol acá

Sos el **agente orquestador** de la Fase 1 (estructura, contexto, brief, documentación, manual),
que ya está generada. Para trabajo en las fases siguientes, delegá al agente especializado:

| Fase | Cuándo | Agente a usar |
|---|---|---|
| 2 — Modelo de datos | al modelo de datos | leé `agents/datamodel-agent.md` |
| 3 — API | al construir el backend | leé `agents/api-agent.md` |
| 4 — CMS | al construir el panel web | leé `agents/cms-agent.md` |
| 5 — Sitio web público | al construir la web pública | leé `agents/web-agent.md` |

## Reglas generales (aplican a todas las fases)

1. **Fuente de verdad:** `context/` y `docs/01-alcance.md`. No inventes requerimientos.
2. **Marca:** usá `#2160AD` (azul) + blanco siempre. Variables CSS `--acr-azul` / `--acr-blanco`.
3. **Trazabilidad:** toda escritura lleva `created_by`/`updated_by` y timestamps.
4. **Soft delete:** entidades críticas usan `estado` en lugar de borrado físico.
5. **No funcionales:** auth + control de acceso por rol desde el día uno (RNF-03/04).
6. **No avances de fase** sin que la anterior dejó su entregable validado (ver `00-ruta`).
7. **Contenido público:** no publiques cifras de usuarios/facturación, nombres, fechas ni fotos
   sin validación de la organización. Las fotos de referencia deben reemplazarse por material propio.
8. **Privacidad:** el sitio público no expone datos sensibles de usuarios ni información
   operativa restringida de la planta.

## Paso 0 — Antes de escribir código

- Si vas a la **Fase 2**, leé `agents/datamodel-agent.md` y `docs/03-modelo-datos.md`.
- Si vas a la **Fase 3**, leé `agents/api-agent.md`, `docs/04-api.md` y el DBML de Fase 2.
- Si vas a la **Fase 4**, leé `agents/cms-agent.md`, `docs/05-cms.md` y la API de Fase 3.
- Si vas a la **Fase 5**, leé `agents/web-agent.md`, `docs/06-sitio-web.md`,
  `docs/07-herramientas-y-referencias.md` y el contrato del API público.

## Lo que no tenés que hacer

- No asumas valores reales de rangos de parámetros (pH min/max, cloro, turbiedad) ni umbrales
  de inventario: marcalos como configurables hasta que la organización los confirme.
- No cambies la paleta de marca sin autorización.
- No construyas la API o el CMS antes de tener el modelo de datos validado.
- No publiques contenido demo, cifras de usuarios/facturación ni fotos de stock como si fueran
  de Acuaricaurte.

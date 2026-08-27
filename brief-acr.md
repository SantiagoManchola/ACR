# Brief: Sistema de Gestión Operativa — Acueducto Comunitario Acuaricaurte (ACR)

> Plantilla reutilizable para arrancar el sistema ACR. Última revisión: agosto 2026.
> Basado en `013_agente-whatsapp-ia/brief-whatsapp-bot-ia.md` como guía de formato.

---

## Cómo usar este brief

1. **Como prompt para un agente de código** (Claude Code, Cursor, Codex). Rellena el bloque
   de variables y pásale el archivo; está escrito para que el agente ejecute sin preguntar 20 cosas.
2. **Como documento de arranque de equipo.** Decisiones tomadas con su porqué.
3. **Como checklist de revisión.** La sección de alcance y requerimientos es la fuente de verdad.

> Lo que **no** es: un tutorial de SQL o de frameworks. La documentación técnica de cada fase
> vive en `docs/`.

---

## Variables a rellenar (estado actual)

```yaml
proyecto:
  nombre:            ACR — Acueducto Comunitario Acuaricaurte
  proposito:         Centralizar y digitalizar la gestión operativa (inventario, micromedidores, planta)
  organizacion:      Acueducto Comunitario Acuaricaurte — Barrio Ricaurte, Ibagué, Tolima, Colombia
  idioma_usuarios:   es

alcance:
  modulos:           [auth/admin, inventario, micromedidores, planta, reportes]
  fuera_de_alcance:  [PQR, presiones de red, monitoreo IoT, facturación externa, purgas, niveles de tanque]
  volumen_estimado:  ~1.124 usuarios, 3 operarios, 2 fontaneros, planta con mediciones diarias

tecnico:
  api:               FastAPI + PostgreSQL + JWT  (propuesta)
  modelo_datos:      DBML en dbdiagram.io       (propuesta)
  cms:               Vue 3 + Pinia + Vite        (propuesta)
  auth:              JWT + roles/permisos
```

---

## Decisiones ya tomadas (y por qué)

### Forma del producto: plataforma web, no app móvil nativa

RNF-01/RNF-08/RNF-09 exigen acceso web, usabilidad y adaptabilidad a móvil. Una SPA web
cumple los tres sin instalar software en cada equipo. Los fontaneros/operarios usarán el
navegador del celular en campo.

### Backend: API primero, desacoplada del frontend

Separar **API (FastAPI)** de **CMS (SPA)** permite que el mismo backend sirva reportes,
futuras integraciones y mantenga la trazabilidad centralizada. También deja cada fase con su
agente y su repositorio lógico.

### Modelo de datos: DBML (dbdiagram.io) antes de código

El levantamiento de requerimientos ya definió entidades (suscriptores, micromedidores,
lecturas, inventario, movimientos, parámetros, dosificaciones, actividades, usuarios, roles).
Pasarlos a **DBML** da un diagrama visual y el SQL de PostgreSQL listo, evitando errores de
esquema antes de la API.

### Auth: JWT + roles/permisos desde el día uno

La planta de tratamiento es información sensible (regla de negocio 12). El control de acceso
no es opcional: se modela en el modelo de datos y se impone en la API y en el CMS.

### Paleta de marca fija

`#2160AD` (azul) + blanco obligatorios. Ver `context/marca-acr.md`. El CMS usa variables CSS
para no duplicar el color.

---

## Arquitectura obligatoria (visión de conjunto)

```
[ CMS / SPA web ]  ──HTTPS/JSON──►  [ API FastAPI ]
                                      │
                                      ├── Auth/JWT + roles
                                      ├── Lógica de negocio (reglas ACR)
                                      └── PostgreSQL (esquema DBML)
```

Requisitos que el agente de código debe implementar sin que se los pidan dos veces:

| Requisito | Por qué |
|---|---|
| Autenticación + refresh token | RNF-03 seguridad |
| Control de acceso por rol en cada endpoint | RNF-04 control de acceso |
| Trazabilidad: `created_by` / `updated_by` / timestamps en tablas clave | RNF-05, RF-34/RF-05 |
| Validaciones de integridad (Pydantic/SQL) | RNF-06 integridad |
| Historiales no borrables (soft delete / append-only donde aplique) | Regla de negocio 14 |
| Exportación CSV/Excel/PDF en reportes | RF-33/RF-20/RF-36 |
| Respaldos de PostgreSQL | RNF-15/RNF-16 |
| Interfaz responsive + modo claro (azul/blanco) | RNF-08/RNF-09 y marca |

---

## Fases y sus agentes

Cada fase tiene un agente dedicado (ver `AGENTS.md` y `agents/`):

| Fase | Entregable | Agente |
|---|---|---|
| 1 | Estructura, contexto, brief, docs, manual | orquestador (`AGENTS.md`) |
| 2 | `datamodel/acr.dbml` (dbdiagram.io) | `agents/datamodel-agent.md` |
| 3 | `api/` (FastAPI + PostgreSQL) | `agents/api-agent.md` |
| 4 | `cms/` (SPA web) | `agents/cms-agent.md` |

---

## Checklist de arranque (Fase 1)

- [x] Brief de negocio (`context/brief-acr.md`)
- [x] Contexto de marca (`context/marca-acr.md`)
- [x] Ruta de construcción paso a paso (`docs/00-ruta-de-construccion.md`)
- [x] Alcance y arquitectura (`docs/01-alcance.md`, `docs/02-arquitectura.md`)
- [x] Manual de usuario (`docs/manual-de-usuario.md`)
- [x] Agentes definidos (`AGENTS.md` + `agents/*`)
- [ ] Validar stack propuesto (FastAPI / Vue 3) antes de Fase 3
- [ ] Reunir valores exactos de rangos de parámetros y umbrales de inventario con la org.

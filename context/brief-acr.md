# Brief de negocio — ACR (Acueducto Comunitario Acuaricaurte)

> Resumen del negocio y el alcance para que cualquier agente o persona del equipo entienda
> de qué trata el sistema sin leer todos los documentos de requerimientos.

---

## La organización en una frase

Acuaricaurte es un **acueducto comunitario** del barrio Ricaurte (Ibagué, Tolima) que capta
agua de la quebrada El Tejar, la trata en su planta y la distribuye a ~1.124 usuarios
facturables (~8.000 personas atendidas), gestionado por una junta/admin comunitaria.

## Problema que resuelve el sistema

Hoy la operación depende de **formatos físicos, hojas de cálculo y WhatsApp**. Eso dificulta:

- Consultar información histórica (buscar fechas/registros a mano).
- Controlar movimientos de inventario y responsables.
- Consolidar lecturas de micromedidores (proceso de ~2 días).
- Detectar parámetros de agua fuera de rango y registrar acciones correctivas.
- Riesgo de pérdida/deterioro de papeles en la planta (humedad).

## Propósito del software

Una **plataforma web centralizada de gestión operativa** que reúna inventario, micromedidores
y planta de tratamiento, con control de acceso por rol, trazabilidad y reportes exportables.

## Actores

| Actor | Responsabilidad en el sistema |
|---|---|
| **Administrador** | Control general: gestiona usuarios, roles, permisos y consulta todo. |
| **Personal administrativo** | Consolida info operativa: inventario y lecturas de micromedidores. |
| **Operario de planta** | Registra parámetros de agua, dosificaciones, actividades y horas de servicio. |
| **Fontanero** | Toma física de lecturas; entrega la info para registro (puede no usar el sistema directo). |

## Módulos del alcance inicial

1. **Autenticación y administración** — usuarios, roles, permisos, auditoría.
2. **Inventario** — equipos, herramientas, lab, accesorios; entradas/salidas; alertas mínimas.
3. **Micromedidores** — suscriptores, medidores, lecturas mensuales, consumo histórico, novedades.
4. **Planta de tratamiento** — parámetros (pH, color, turbiedad, cloro, temp.), dosificación,
   químicos, actividades, horas de servicio, acciones correctivas.
5. **Consultas y reportes** — históricos filtrables y exportación (CSV/Excel/PDF).

## Fuera de alcance (v1)

PQR, presiones de red, purgas, niveles de tanques, monitoreo IoT, integración con sistemas de
facturación externos, automatización de captura desde dispositivos. (Ampliaciones futuras.)

## Requerimientos no funcionales clave

Web accesible 24/7, autenticación, control de acceso por rol, trazabilidad de operaciones,
usabilidad para usuarios con bajo nivel tecnológico, responsive (móvil + escritorio),
escalabilidad (~1.124→más micromedidores), respaldos y documentación básica.

## Identidad

Azul `#2160AD` + blanco. Ver `context/marca-acr.md`.

## Decisión de stack (propuesta para validar)

| Capa | Propuesta | Por qué |
|---|---|---|
| API | **FastAPI (Python) + MySQL + JWT** | Rápido de construir, tipado, ideal para datos/CRUD y reportes. |
| Modelo de datos | **DBML en dbdiagram.io** | Visualización y exportación SQL lista para MySQL. |
| CMS / panel web | **Vue 3 + Pinia + Vite** (o Next.js) | SPA limpia, responsive, fácil de temar con la paleta ACR. |
| Auth | JWT + roles/permisos | Cumple RNF de control de acceso y trazabilidad. |

> Estas decisiones son una recomendación inicial; el equipo puede ajustarlas antes de
> iniciar la Fase 3 (API) y Fase 4 (CMS).

## Fases del proyecto (ver `docs/00-ruta-de-construccion.md`)

- **Fase 1 (actual):** estructura, agentes, contexto, brief, documentación y manual.
- **Fase 2:** modelo de datos en dbdiagram.io.
- **Fase 3:** API (FastAPI).
- **Fase 4:** CMS / panel web.
- Cada fase tiene su propio **agente** (ver `AGENTS.md`).

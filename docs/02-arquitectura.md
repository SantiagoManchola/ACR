# Arquitectura — ACR

> Visión técnica de conjunto. Detalles por fase en `docs/03-modelo-datos.md`, `04-api.md`,
> `05-cms.md`.

---

## 1. Visión general

```
┌────────────────────┐      HTTPS / JSON      ┌──────────────────────┐
│  CMS / SPA web     │ ─────────────────────► │  API (FastAPI)       │
│  (Vue 3 + Pinia)   │ ◄───────────────────── │  - Auth JWT          │
│  Tema #2160AD/blanco│   tokens + datos      │  - Roles/permisos    │
└────────────────────┘                        │  - Lógica ACR        │
                                             └──────────┬───────────┘
                                                        │ SQL
                                                ┌───────▼────────┐
                                                │  MySQL    │
                                                │  (esquema DBML)│
                                                └────────────────┘
```

## 2. Capas

### CMS / SPA web (Fase 4)
- Interfaz para administrativo, operario y (vía administrativo) fontanero.
- Control de menús por rol.
- Formularios simples (RNF-08) y responsive (RNF-09).
- Tema azul `#2160AD` + blanco (`context/marca-acr.md`).

### API (Fase 3)
- FastAPI + Pydantic (validaciones = RNF-06 integridad).
- JWT auth + middleware de permisos por rol (RNF-03/RNF-04).
- Lógica de negocio ACR: cálculo de consumo/promedio, detección fuera de rango,
  soft delete, trazabilidad (`created_by`, `updated_by`, `created_at`, `updated_at`).
- Exportación de reportes (CSV/Excel/PDF).
- OpenAPI/Swagger automático.

### Datos (Fase 2)
- MySQL. Esquema definido en DBML (`datamodel/acr.dbml`), generado desde
  `docs/01-alcance.md`.
- Índices en campos de búsqueda/filtro (fecha, sector, micromedidor, parámetro).
- Respaldos programados (RNF-15) y punto de recuperación (RNF-16).

## 3. Seguridad y trazabilidad (transversal)
- Login con contraseñas hasheadas (bcrypt) + JWT.
- Middleware que inyecta el usuario actual en cada escritura → auditoría.
- La info de planta se protege con un permiso específico (regla de negocio 12).
- Soft delete en entidades críticas para no perder históricos (regla de negocio 14).

## 4. Escalabilidad (RNF-11)
- Índices y paginación en listados (lecturas, movimientos, parámetros crecen rápido).
- Separación API/CMS permite escalar el backend de forma independiente.
- Modelo pensado para pasar de ~1.124 a miles de micromedidores.

## 5. Sitio público (Fase 5)
- `web/` con **Astro 7** y salida estática: no depende del API en runtime.
- Consume `/publico/*` en build y se reconstruye con un deploy hook al publicar.
- El CMS existente gana un módulo **Contenido** con noticias, páginas y
  configuración del sitio. Las imágenes se almacenan en R2.
- Si el API no está disponible durante el build, se conserva la última versión
  publicada y se usa el contenido local de desarrollo como fallback.
- Plan: `docs/06-sitio-web.md`; herramientas: `docs/07-herramientas-y-referencias.md`.

## 6. Entornos
- Desarrollo: MySQL local (Docker) + SPA en dev server; sitio público en `web/`.
- Producción: mismo stack; variables de entorno separadas; HTTPS obligatorio;
  respaldos automáticos. (Detalles a definir en Fase 3/4/5.)

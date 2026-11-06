# Agente Fase 5 — Sitio web público

> Usado por el agente de código cuando toca construir o mantener el sitio público
> de ACR. Carpeta de trabajo: `web/`. Plan: `docs/06-sitio-web.md`.
> Depende de: Fase 3 (API) y Fase 4 (CMS). Consume `/publico/*` y administra
> contenido desde `/contenido/*`.

## Tu objetivo

Construir el sitio público del **Acueducto Comunitario Acuaricaurte**: rápido,
accesible, administrable y fiel a la marca azul `#2160AD` + blanco. El sitio debe
servir a personas con distintos niveles tecnológicos y conectividad.

## Paso a paso

1. Leé `AGENTS.md`, `context/marca-acr.md`, `docs/01-alcance.md`,
   `docs/06-sitio-web.md`, `docs/07-herramientas-y-referencias.md` y el contrato
   del API.
2. Verificá Node 22.23.4+ (ideal 24) y `npm install` en `web/`.
3. Revisá el sistema de diseño en `web/src/styles/tokens.css` y
   `web/src/styles/global.css`. No cambies la paleta sin autorización.
4. Si hay API: definí `ACR_API_URL` y `R2_PUBLIC_HOST` en `web/.env`; el
   adaptador está en `web/src/lib/content.ts`.
5. Si no hay API: usá `web/src/data/` como fallback de desarrollo, sin presentar
   el contenido demo como definitivo.
6. Construí o ajustá las páginas con HTML semántico, CSS propio y el mínimo JS.
7. Cargá imágenes con `<SmartImage>` (AVIF/WebP, alt obligatorio, sizes
   correctos). No uses `<img>` sueltos salvo casos justificados.
8. Verificá SEO: título, descripción, canonical, OG, JSON-LD, sitemap y RSS.
9. Verificá accesibilidad: teclado, foco, contraste, zoom 200 %, lector de
   pantalla, `prefers-reduced-motion`.
10. Corré `npm run check`, `npm run build` y `node scripts/check-overflow.mjs`.
11. Actualizá la documentación y el estado en `docs/06-sitio-web.md`.

## Stack

- Astro 7 + TypeScript.
- CSS propio con tokens (sin Tailwind en v1).
- Pagefind para búsqueda.
- `astro:assets` + Sharp para imágenes.
- Cloudflare Pages/Workers + R2.
- Vue 3 + Pinia solo en el CMS existente, no en el sitio público.

## Estructura de `web/`

```
web/
  src/
    assets/images/        # fotos locales (se importan para optimizar)
    components/           # Header, Footer, PageHeader, WaterMap, NewsRow, SEO…
    data/                 # contenido local de desarrollo (fallback)
    layouts/BaseLayout.astro
    lib/                  # api.ts, content.ts, format.ts, types.ts
    pages/                # rutas: /, /noticias, /quienes-somos, /nuestra-agua…
    scripts/ui.ts         # menú, accesibilidad, compartir, filtros
    styles/               # tokens.css, global.css
  public/                 # _headers, favicon, logo, OG, manifest
  scripts/                # generate-og.mjs, check-overflow.mjs
```

## Reglas de contenido

- No inventes cifras, fechas, nombres ni eventos.
- No publiques cifras de usuarios, facturación ni cobertura: la organización
  decidió no exponerlas en el sitio público.
- No publiques información operativa sensible de la planta.
- Las fotos de personas requieren consentimiento; no uses stock como si fuera
  Acuaricaurte.
- Los artículos demo deben marcarse como tales en `web/CONTENIDO-DEMO.md`.
- El tono es cercano, institucional, claro y sin sensacionalismo.

## Reglas técnicas

- Cero JS innecesario. Si una interacción se resuelve con HTML/CSS, hacelo así.
- No agregues dependencias sin justificar costo, licencia y mantenimiento.
- No dupliques lógica de negocio del API (consumos, parámetros, permisos).
- No guardes secretos en el frontend.
- No uses `dangerouslySetInnerHTML`/`set:html` con contenido sin sanitizar.
  El API debe sanitizar el HTML editorial con `nh3`.
- No cambies la paleta ni la tipografía base sin autorización.
- Mantené los textos en español de Colombia (`es-CO`).
- Los enlaces externos llevan `rel="noopener noreferrer"` y `target="_blank"`
  cuando corresponda.
- Los botones de WhatsApp usan `https://wa.me/<numero>?text=...` con el número
  en formato internacional.

## Calidad mínima

- `npm run check` sin errores.
- `npm run build` sin errores y con Pagefind generado.
- Sin desbordes horizontales en 390, 768 y 1440 px.
- Lighthouse móvil ≥ 95 en Performance, Accessibility, SEO y Best Practices.
- LCP < 2.0 s, JS inicial < 30 KB, CLS < 0.05.
- WCAG 2.2 AA: contraste, foco, teclado, alt, jerarquía, zoom 200 %.
- Sitemap, RSS, canonical, OG y JSON-LD correctos.
- Imágenes con alt, crédito y tamaños responsive.

## Criterio de aceptación

- [ ] Páginas v1 completas y responsive.
- [ ] Contenido administrable desde el CMS (noticias, páginas y configuración).
- [ ] Publicación → deploy automático; staging para revisión.
- [ ] Búsqueda, RSS, sitemap y 404.
- [ ] Accesibilidad y performance verificadas.
- [ ] Documentación y manual de contenido actualizados.
- [ ] Activos reales (logo, fotos, WhatsApp, redes) reemplazados.

## Lo que no tenés que hacer

- No construir pagos, PQR ni portal de usuarios en v1.
- No cambiar la arquitectura API/CMS sin decisión del equipo.
- No publicar contenido sin validación de la organización.
- No copiar diseño, código ni imágenes de ACUACAR, IBAL, EPM u otros sitios.
- No usar IA para simular fotos reales de la comunidad.

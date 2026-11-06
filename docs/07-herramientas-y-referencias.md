# Herramientas, repos y referencias para el sitio público ACR

> Snapshot: **29 de octubre de 2026**. Las estrellas de GitHub cambian a diario;
> se usan solo como señal de tracción, no como criterio único de adopción.
> Este documento registra qué se adoptó, qué se evaluó y qué se descartó para
> la Fase 5, con su justificación.

---

## 1. Criterios de selección

Antes de adoptar una herramienta se revisa:

1. **Encaje con el problema** (no moda).
2. **Licencia** y compatibilidad con una organización comunitaria.
3. **Mantenimiento** (actividad, issues, releases).
4. **Costo total** (hosting, licencias, operación).
5. **Lock-in** (¿se puede migrar?).
6. **Seguridad** y superficie de ataque.
7. **Accesibilidad** y calidad de la experiencia.
8. **Curva de aprendizaje** para el equipo que mantendrá el sitio.

Regla: una herramienta entra a producción solo si resuelve un problema real y
si el equipo puede mantenerla sin depender de una persona.

---

## 2. Proyectos trending de GitHub (29 oct 2026)

### 2.1 Agentes, skills y metodología

| Proyecto | Estrellas | Licencia | Estado en ACR | Uso |
|---|---:|---|---|---|
| [obra/superpowers](https://github.com/obra/superpowers) | ~308k | MIT | **Referencia** | Framework de skills y metodología para agentes. Inspira el flujo de trabajo, no es dependencia del sitio. |
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | ~95k | Apache-2.0 | **Adoptado como checklist** | Vocabulario de diseño y auditoría para evitar “AI slop”: crítica, pulido y revisión antes de entregar. |
| [elayadesign/ai-design-skills](https://github.com/elayadesign/ai-design-skills) | ~12k | MIT | **Referencia** | Skills de diseño para agentes. Se usa como inspiración para el design system y las revisiones. |
| `ui-ux-pro-max` | — | — | **Adoptado** (skill local) | Base para la dirección de diseño, accesibilidad y auditoría. |

> `superpowers`, `impeccable` y `ai-design-skills` son herramientas para el
> proceso de construcción. No se instalan en el runtime del sitio ni se envían
> al navegador.

### 2.2 Frameworks y CMS

| Proyecto | Estrellas | Licencia | Estado en ACR | Nota |
|---|---:|---|---|---|
| [withastro/astro](https://github.com/withastro/astro) | ~64k | MIT | **Adoptado** | Base del sitio. Cero JS por defecto, islas, contenido y build estático. |
| [payloadcms/payload](https://github.com/payloadcms/payload) | ~46k | MIT | **Evaluado — no v1** | Excelente CMS fullstack, pero duplica auth/DB y suma Node/Postgres. |
| [directus/directus](https://github.com/directus/directus) | ~39k | Source-available | **Evaluado — no v1** | Muy bueno sobre bases existentes, pero es otro servicio que operar. |
| [sanity-io/sanity](https://github.com/sanity-io/sanity) | ~6k | MIT (Studio) | **Evaluado — no v1** | Editor excelente; la data vive en su nube. |
| [strapi/strapi](https://github.com/strapi/strapi) | ~73k | MIT / enterprise | **Evaluado — no v1** | Popular y maduro, pero pesado para 5 páginas. |
| [tinacms/tinacms](https://github.com/tinacms/tinacms) | ~14k | Apache-2.0 | **Evaluado — no v1** | Edición visual sobre Git; requiere que los editores usen GitHub. |
| [decaporg/decap-cms](https://github.com/decaporg/decap-cms) | ~19k | MIT | **Evaluado — no v1** | CMS Git-based; mismo problema de flujo para la junta. |
| [vercel/next.js](https://github.com/vercel/next.js) | ~143k | MIT | **Descartado v1** | Más peso y complejidad para un sitio editorial pequeño. |
| [nuxt/nuxt](https://github.com/nuxt/nuxt) | ~61k | MIT | **Alternativa** | Útil si el equipo prefiere Vue fullstack; no es necesario aquí. |
| [vuejs/core](https://github.com/vuejs/core) | ~55k | MIT | **Ya usado** | CMS interno existente (Fase 4). |

### 2.3 UI, diseño y componentes

| Proyecto | Estrellas | Licencia | Estado en ACR | Uso |
|---|---:|---|---|---|
| [shadcn-ui/ui](https://github.com/shadcn-ui/ui) | ~127k | MIT | **Referencia** | Patrones de componentes accesibles; no se copia React al sitio Astro. |
| [tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss) | ~98k | MIT | **No usado v1** | Se prefirió CSS propio con tokens para un sitio pequeño y muy visual. |
| [radix-ui/primitives](https://github.com/radix-ui/primitives) | ~19k | MIT | **Referencia** | Comportamientos accesibles (menús, diálogos). |
| [tailwindlabs/headlessui](https://github.com/tailwindlabs/headlessui) | ~29k | MIT | **Referencia** | Patrones de interacción sin estilos. |
| [lucide-icons/lucide](https://github.com/lucide-icons/lucide) | ~25k | ISC | **Referencia** | Base de los trazos de iconos; el sitio usa SVG inline. |
| [motiondivision/motion](https://github.com/motiondivision/motion) | ~35k | MIT | **No usado v1** | Animaciones con CSS + IntersectionObserver; menos JS. |
| [greensock/GSAP](https://github.com/greensock/GSAP) | ~30k | Standard | **No usado v1** | Overkill para el nivel de movimiento del sitio. |
| [penpot/penpot](https://github.com/penpot/penpot) | ~62k | MPL-2.0 | **Alternativa de diseño** | Figma open source; útil si no se quiere depender de Figma. |
| [onlook-dev/onlook](https://github.com/onlook-dev/onlook) | ~27k | Apache-2.0 | **Exploración** | Edición visual de código; interesante, no producción. |
| [BuilderIO/builder](https://github.com/BuilderIO/builder) | ~9k | MIT | **Referencia** | Figma → código; se usa como inspiración, no como dependencia. |

### 2.4 Búsqueda, imágenes y performance

| Proyecto | Estrellas | Licencia | Estado en ACR | Uso |
|---|---:|---|---|---|
| [cloudcannon/pagefind](https://github.com/cloudcannon/pagefind) | ~5.5k | MIT | **Adoptado** | Búsqueda estática, sin servidor, índice en build. |
| [ascorbic/unpic](https://github.com/ascorbic/unpic) | ~0.4k | MIT | **Referencia** | Traductor de CDN de imágenes; Astro + Sharp cubre v1. |
| Astro `<Picture>` + Sharp | — | — | **Adoptado** | AVIF/WebP responsive en build. |
| Cloudflare Images | — | Servicio | **Evaluado** | Útil si crece el volumen o se necesita transformación en runtime. |

### 2.5 Infraestructura

| Proyecto | Estrellas | Licencia | Estado en ACR | Uso |
|---|---:|---|---|---|
| [cloudflare/workers-sdk](https://github.com/cloudflare/workers-sdk) | ~4.7k | Apache-2.0 | **Adoptado** | Wrangler/Workers para despliegue y funciones futuras. |
| Cloudflare Pages | — | Servicio | **Adoptado** | Hosting estático, CDN, previews y deploy hooks. |
| Cloudflare R2 | — | Servicio | **Ya usado** | Imágenes del CMS. |
| GitHub Actions | — | Servicio | **Adoptado** | CI del build del sitio. |

### 2.6 Plantillas Astro de referencia

| Proyecto | Estrellas | Licencia | Uso |
|---|---:|---|---|
| [satnaing/astro-paper](https://github.com/satnaing/astro-paper) | ~5.2k | MIT | Referencia de SEO, RSS y accesibilidad para blogs. No se copia el diseño. |
| [saicaca/fuwari](https://github.com/saicaca/fuwari) | ~5.1k | MIT | Referencia de estructura de blog estático. |
| [CuteLeaf/Firefly](https://github.com/CuteLeaf/Firefly) | ~2.4k | MIT | Referencia visual de themes Astro. |

> Las plantillas se usan para estudiar estructura y buenas prácticas. El diseño
> de Acuaricaurte es propio y parte de su identidad comunitaria.

---

## 3. Research e inspiración

### 3.1 Referencias de producto

| Fuente | Para qué |
|---|---|
| [Mobbin](https://mobbin.com/) | Flujos reales de apps y sitios; navegación, onboarding, estados. |
| [Refero](https://refero.design/) | Capturas de interfaces por tipo de producto. |
| [Page Flows](https://pageflows.com/) | Flujos de usuario paso a paso. |
| [Land-book](https://land-book.com/) | Galería de landing pages. |
| [Godly](https://godly.website/) | Referencias de diseño web de alto nivel. |
| [Awwwards](https://www.awwwards.com/) | Exploración visual; usar con criterio, no copiar. |
| [SaaSFrame](https://www.saasframe.io/) | Patrones de SaaS; menos relevante para ACR. |

### 3.2 Utilities y sitios de agua

| Sitio | Qué observar |
|---|---|
| [ACUACAR](https://www.acuacar.com/) | Accesos rápidos, canales, noticias, transparencia. |
| [IBAL](https://www.ibal.gov.co/) | Hero con banners, noticias, transparencia, accesibilidad. |
| [EPM](https://www.epm.com.co/) | Fotografía full-bleed, CTAs, módulo de noticias. |
| [California Water Service](https://www.calwater.com/) | Menú, atajos persistentes, alertas. |
| [Aquarion Water](https://www.aquarionwater.com/) | Claridad, fotografía cálida, tareas esenciales. |
| [Eagle River Water & Sanitation District](https://www.erwsd.org/) | Utilidad sin ruido, quick links, transparencia. |
| [El Paso Water](https://www.epwater.org/) | Formas suaves, storytelling del agua, servicios. |
| [Wilmington Water](https://www.wilmingtondewater.gov/) | Estructura de servicios y calidad del agua. |

**Qué copiar:** claridad de tareas, acceso a noticias, canales de contacto,
transparencia, accesibilidad.
**Qué no copiar:** mega menús, carruseles infinitos, cookies, peso técnico,
exceso de secciones.

### 3.3 Tendencias de diseño para utilities (2026)

- Paletas terrosas y azules calmados.
- Fotografía real de la comunidad y del territorio.
- Micro-animaciones sutiles que explican, no decoran.
- Formas orgánicas y bordes suaves.
- Accesibilidad como parte del diseño, no como widget.
- Contenido en lenguaje sencillo.
- Transparencia y rendición de cuentas.

Fuentes: [Powerful Web — Utility Website Design Trends 2026](https://www.powerfulweb.com/2026/02/utility-website-design-trends-for-2026),
[Inclind — Best Utility Website Examples](https://www.inclind.com/news/best-utility-website-examples).

---

## 4. IA para diseño

| Herramienta | Uso | Precaución |
|---|---|---|
| [Figma](https://www.figma.com/) + Figma Make / First Draft | Wireframes, variaciones, prototipos | Revisar todo; la IA no decide la marca |
| [v0](https://v0.dev/) | Explorar UI React/Tailwind | El output se traduce a componentes Astro; no se copia |
| [Lovable](https://lovable.dev/) | Prototipo rápido fullstack | No usar para producción de ACR |
| [Bolt](https://bolt.new/) | Prototipo rápido | Igual que Lovable |
| [Relume](https://www.relume.io/) | Sitemap y wireframes | Útil para estructurar, no para el diseño final |
| [Framer](https://www.framer.com/) | Prototipo navegable | Evaluar con la junta; no es el runtime elegido |
| [Penpot](https://penpot.app/) | Diseño open source | Alternativa a Figma |
| [Uizard](https://uizard.io/) / [Visily](https://www.visily.ai/) | Wireframes de baja fidelidad | Solo exploración |
| [Recraft](https://www.recraft.ai/) / [Ideogram](https://ideogram.ai/) | Moodboards y exploración de logo | El logo final se vectoriza y revisa humanamente |
| [Adobe Firefly](https://www.adobe.com/products/firefly.html) | Moodboards e imágenes con licencia comercial | No usar para simular fotos de la comunidad |
| [Midjourney](https://www.midjourney.com/) | Moodboards | Revisar licencia y no falsear la realidad |

**Regla ética:** la IA acelera la exploración. No reemplaza la fotografía real,
el consentimiento de las personas ni la identidad de la organización.

---

## 5. Reverse engineering (ético)

| Herramienta | Para qué | Límite |
|---|---|---|
| [Wappalyzer](https://www.wappalyzer.com/) | Identificar stacks (WordPress, AEM, etc.) | Solo análisis técnico |
| [BuiltWith](https://builtwith.com/) | Tecnologías y servicios de un sitio | No copiar implementación |
| Chrome DevTools | Espaciado, tipografía, responsive, performance | Uso normal de análisis |
| [CSS Peeper](https://csspeeper.com/) | Extraer estilos y jerarquía visual | Referencia, no copia |
| [VisBug](https://github.com/GoogleChromeLabs/visbug) | Inspección visual en el navegador | Referencia |
| [html.to.design](https://html.to.design/) | Importar un sitio a Figma para analizarlo | No reproducir la identidad |
| [screenshot-to-code](https://github.com/abi/screenshot-to-code) | Convertir capturas en prototipos | Solo prototipo; requiere revisión |
| [Anima](https://www.animaapp.com/) / [Locofy](https://www.locofy.ai/) | Figma → código | Scaffolding, no producción |
| [PageSpeed Insights](https://pagespeed.web.dev/) / [WebPageTest](https://www.webpagetest.org/) | Benchmarks reales | Comparar, no obsesionarse |

**Límite legal:** se analizan patrones y se aprende de ellos. No se copian
código, textos, imágenes, logotipos ni identidad visual de terceros.

---

## 6. Herramientas adoptadas en el sitio

| Herramienta | Rol |
|---|---|
| Astro 7 | Framework estático |
| TypeScript 6 | Tipado |
| CSS propio + tokens | Sistema de diseño |
| Archivo + Newsreader (Fontsource) | Tipografía auto-hospedada |
| Pagefind | Búsqueda |
| `@astrojs/sitemap` | Sitemap |
| `@astrojs/rss` | Feed |
| Astro `<Picture>` + Sharp | Imágenes AVIF/WebP |
| Cloudflare Pages | Hosting |
| Cloudflare R2 | Imágenes |
| Cloudflare Web Analytics | Analítica cookieless (opcional) |
| Puppeteer Core | QA visual y desbordes |
| Astro Check | Tipos |
| GitHub Actions | CI |

---

## 7. Herramientas evaluadas y no adoptadas en v1

| Herramienta | Por qué no |
|---|---|
| Payload / Directus / Sanity / Strapi | Duplican CMS/auth/DB; costo y operación extra |
| WordPress | Peso, seguridad y mantenimiento |
| Tailwind | El sitio es pequeño y muy visual; tokens CSS son suficientes |
| GSAP / Motion | El movimiento se resuelve con CSS e IntersectionObserver |
| Framer / Lovable / Bolt | Prototipos, no producción |
| Cloudflare Images | R2 + Sharp cubre v1; revisar si crece el volumen |
| Comentarios / foro | Fuera de alcance y riesgo de moderación |

---

## 8. Aplicación al rediseño de ACR

El rediseño “señalética pública + boletín” se auditó con estas herramientas:

| Herramienta | Antes | Después |
|---|---|---|
| **Impeccable detect** (home y páginas principales) | 32 hallazgos: 5 eyebrows, 22 textos < 11 px, 2 radial glows, 1 paleta IA | **0 hallazgos** |
| **UI Craft Detect** (fuente) | 80 warnings, 20 archivos | 88 warnings, en su mayoría `unit-mixing`/`no-focus-visible` por reglas estáticas; se corrigió el crítico de botón icon-only |
| **Lighthouse móvil** (home) | 95/100/100/100, LCP 2.9 s | **96/100/100/100, LCP 2.6 s** |
| **Smoke test** | 31/31 | **31/31** |

Decisiones tomadas a partir del research:

- Se eliminaron los eyebrows repetidos y los radial gradients.
- Se reemplazaron tarjetas y stat cards por tablas, listas, fichas y un mapa.
- Se subió el mínimo funcional a 12 px.
- Se pasó de Manrope + Inter a **Archivo + Newsreader**.
- Se cambió el fondo crema por un papel gris-verde más neutro.
- Se conservó el azul `#2160AD` y el logo real; la herramienta marcó “AI palette”
  por el azul, pero es la marca y se mantiene conscientemente.
- Se documentó que el contenido factual y las fotos siguen siendo placeholders.

## 9. Mantenimiento de este documento

- Revisar cada trimestre.
- Actualizar estrellas/versiones solo si se toma una decisión.
- Registrar nuevas herramientas con el mismo formato: **Adoptado / Evaluado /
  Referencia / Descartado**.
- No agregar dependencias al sitio sin pasar por los criterios de la sección 1.

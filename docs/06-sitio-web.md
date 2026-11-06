# Plan Fase 5 — Sitio web público de Acuaricaurte

> Entregable: `web/` (Astro 7 + TypeScript).
> Depende de: Fase 3 (API) y Fase 4 (CMS).
> Agente: `agents/web-agent.md`.
> **Estado: 🚧 en desarrollo.** La base visual, las páginas, el SEO técnico y la
> búsqueda están construidos con contenido local de demostración. Falta conectar
> el API público, el módulo de contenido del CMS y reemplazar los activos
> provisionales por los reales.

---

## 1. Objetivo

Construir el sitio público del **Acueducto Comunitario Acuaricaurte** como una
vitrina institucional ligera, rápida, accesible y administrable. El sitio debe:

1. Explicar quiénes somos y cómo se gestiona el agua.
2. Publicar noticias, avisos y contenido institucional sin depender de un desarrollador.
3. Dar canales de contacto claros, con WhatsApp como puerta principal.
4. Cargar rápido en celulares y conexiones lentas.
5. Servir de base para futuras ampliaciones (PQR, pagos, transparencia).

No es una tienda ni un portal transaccional. La complejidad está en la calidad
de la experiencia, no en la cantidad de funcionalidades.

---

## 2. Alcance v1

| Página | Propósito |
|---|---|
| `/` | Portada institucional, tablón de avisos, mapa del agua, archivo de noticias y acceso a la comisión |
| `/noticias` | Listado con destacada, filtros por categoría y búsqueda |
| `/noticias/[slug]` | Artículo con resumen fácil, compartir, relacionadas y SEO |
| `/quienes-somos` | Historia, misión, visión, valores e hitos |
| `/comision-empresarial` | Micrositio de una página con información de la Comisión Empresarial, delegada de la Junta de Acción Comunal |
| `/nuestra-agua` | Proceso de potabilización, consejos y preguntas frecuentes |
| `/contacto` | Formulario, ubicación, correo, WhatsApp, horario, redes y recomendaciones |
| `/buscar` | Búsqueda estática con Pagefind |
| `/privacidad` | Política base sujeta a revisión legal |
| `/404` | Error amable con navegación de rescate |
| `/rss.xml` | Feed de noticias |
| `/sitemap-index.xml` | Sitemap generado por Astro |
| `/robots.txt` | Reglas de indexación |

### Fuera de alcance v1

- Pagos o facturación en línea.
- PQR formales con radicado.
- Portal de usuarios.
- Multilenguaje.
- Monitoreo de calidad del agua en tiempo real.
- Feed automático de redes sociales.
- Comentarios o cuentas públicas.

---

## 3. Arquitectura

```
                         build-time
┌─────────────────┐   fetch /publico/*   ┌──────────────────┐
│  web/ (Astro 7) │ ◄─────────────────── │  API FastAPI      │
│  HTML estático  │                      │  + MySQL          │
│  Cloudflare     │                      │  /contenido/*     │
└────────┬────────┘                      └────────┬─────────┘
         │                                        │
         │ imágenes optimizadas                   │ admin
         ▼                                        ▼
   Cloudflare R2                          CMS Vue 3
   (originales)                           módulo "Contenido"
```

### Decisiones

1. **Astro estático**: cero JavaScript por defecto. Solo se hidrata lo necesario
   (menú, accesibilidad, compartir, filtros y búsqueda).
2. **El API existente es la fuente de contenido**: no se duplica autenticación,
   usuarios ni base de datos.
3. **El CMS existente administra el contenido**: se agrega un módulo "Contenido"
   con Noticias, Categorías, Páginas y Configuración.
4. **Sin banners**: la portada es una presentación institucional fija; las
   noticias y avisos se administran desde sus propios módulos.
5. **R2 para imágenes**: se reutiliza el almacenamiento que ya usa el sistema.
6. **Build por publicación**: al publicar, el API llama un deploy hook; el sitio
   se reconstruye. Si el API falla, la versión anterior sigue online.
7. **El sitio no consulta el API en runtime**: no hay dependencia de disponibilidad
   del backend para servir una página.

### Por qué no otras opciones

| Opción | Motivo para no usarla en v1 |
|---|---|
| Payload CMS | Duplica auth/DB y suma Node/Postgres; overkill para 5 páginas |
| Sanity | Otro SaaS, otro login y otro costo; los datos salen del sistema ACR |
| WordPress | Pesado, inseguro y difícil de mantener al nivel de performance |
| Decap/Keystatic | Obliga a los editores a usar GitHub; no es viable para la junta |
| Next.js | Más peso y complejidad para un sitio editorial pequeño |

---

## 4. Stack implementado

| Capa | Tecnología | Versión / nota |
|---|---|---|
| Framework | Astro | 7.4.x, salida estática |
| Lenguaje | TypeScript | 6.x |
| Estilos | CSS propio con tokens | Sin framework CSS |
| Fuentes | Archivo + Newsreader | Auto-hospedadas con Fontsource |
| Búsqueda | Pagefind | 1.5.x, índice en build |
| SEO | `@astrojs/sitemap`, `@astrojs/rss` | Sitemap + RSS |
| Imágenes | `astro:assets` + Sharp | AVIF + WebP responsive |
| Hosting | Vercel | Sitio estático + función Edge para el formulario |
| Imágenes | Cloudflare R2 | Originales; optimización en build |
| Analítica | Cloudflare Web Analytics | Opcional, cookieless |
| QA | Astro Check, Puppeteer, Lighthouse | Pendiente automatizar Lighthouse CI |

### Requisitos

- Node.js 22.23.4 o superior (se probó con Node 24).
- npm 10+.

---

## 5. Sistema de diseño

### Concepto

**Señalética pública + boletín comunitario.** El sitio se parece a un sistema de
información de servicio público: portada institucional, tablero de avisos, mapa del
sistema, directorio, fichas y reglas de 1 px. No es una landing de SaaS con
tarjetas y glows.

### Reglas anti-slop

- Sin `eyebrow`/kicker encima de cada título.
- Sin radial gradients, halos ni glows decorativos.
- Sin tarjetas idénticas con icono, título y texto como estructura principal.
- Sin pills en todos los botones: botones rectangulares de 2 px de radio.
- Sin sombras difusas: las superficies se separan con líneas.
- Sin microtexto funcional por debajo de 12 px.
- Sin animación de entrada en cada tarjeta: reveals puntuales.
- Copy específico: lugar, fecha, fuente, nombre o número; no eslóganes.
- Material real: fotos, mapas y testimonios de Acuaricaurte.

### Paleta

Se mantiene la marca **`#2160AD` + blanco**. El papel, la tinta y la señal son
materiales de comunicación, no un cambio de identidad.

| Token | Valor | Uso |
|---|---|---|
| `--acr-azul` | `#2160AD` | Marca |
| `--acr-azul-900` | `#0B2A46` | Header/footer, fondos profundos |
| `--acr-azul-700` | `#1A4F82` | Hover, énfasis |
| `--acr-azul-100` | `#E7EFF8` | Fondos suaves |
| `--acr-papel` | `#F2F4F0` | Fondo de página |
| `--acr-tinta` | `#111820` | Texto |
| `--acr-linea` | `#C9D0CA` | Reglas y bordes |
| `--acr-senal` | `#B45309` | Avisos y estados |
| `--acr-ok` / `--acr-alerta` | `#1F7A4D` / `#B42318` | Estados |

### Tipografía

- **Títulos/UI:** Archivo Variable (señalética, números, navegación).
- **Editorial:** Newsreader Variable (ledes, artículos, citas, notas).
- Escala fluida con `clamp()`; cuerpo base ~17 px.
- Mínimo funcional: 12 px.
- `font-display: swap` y subset latin.

### Componentes

- `Header` fijo con barra de utilidades, navegación y menú móvil.
- `PageHeader`: cabecera de página y portada institucional fija.
- `NoticeBoard`: tablón de avisos en filas, no tarjetas.
- `WaterMap`: mapa esquemático del sistema + estaciones accesibles.
- `NewsRow`: fila de archivo/noticia, con variante destacada.
- `PageHeader`, `SectionTitle`, `Breadcrumbs`, `SocialLinks`.
- `comision-empresarial`: micrositio de una página con ficha.
- `SEO`: canonical, Open Graph, Twitter Cards y JSON-LD.
- `SmartImage`: AVIF/WebP responsive con `Picture`.
- Logo ACR real (`cms/public/acr-logo.png`) con versiones para header, favicon,
  manifest y Open Graph.
- Reveal puntual con `IntersectionObserver`; respeta `prefers-reduced-motion`.

### Accesibilidad

- WCAG 2.2 AA como objetivo.
- Skip link, landmarks, foco visible, contraste 4.5:1, botones de 44×44 px.
- Control de tamaño de texto (100 / 112.5 / 125 %) y alto contraste persistidos
  en `localStorage`.
- Sin carrusel automático.
- `prefers-reduced-motion` respetado.
- Alt text obligatorio en el contenido.
- Sin overlays de accesibilidad de terceros.

### Performance

| Métrica | Objetivo | Resultado actual |
|---|---|---|
| Lighthouse móvil | ≥ 95 en las 4 categorías | 96 / 100 / 100 / 100 |
| LCP en 4G | < 2.5 s | 2.6 s |
| JS inicial | < 30 KB gzip | ~20 KB |
| CLS | < 0.05 | 0.001 |
| Imágenes | AVIF + WebP, responsive, lazy bajo el fold | OK |
| Fuentes | auto-hospedadas, subset latin | OK |

---

## 6. Modelo de contenido

### Tablas nuevas (pendiente de implementar)

| Tabla | Campos clave |
|---|---|
| `noticia_categorias` | `id`, `nombre`, `slug`, `orden`, `activo` |
| `noticias` | `id`, `slug`, `titulo`, `bajada`, `cuerpo_html`, `resumen_facil`, `categoria_id`, `imagen_url`, `imagen_alt`, `imagen_credito`, `destacada`, `estado`, `fecha_publicacion`, `seo_titulo`, `seo_descripcion`, `autor_id`, audit |
| `sitio_config` | WhatsApp, mensaje, redes, email, teléfono, dirección, horario, mapa, logo, favicon, footer |
| `paginas` | `slug`, `titulo`, `contenido_json`, SEO, estado, audit |
| `media` | `id`, `url`, `alt`, `mime`, `width`, `height`, `tamano`, `created_by`, timestamps |

### Reglas

- `noticias.estado`: `borrador | publicado | archivado` (enum propio).
- Fechas en `America/Bogota`.
- Slug único, estable; si cambia, redirect 301.
- Soft delete y auditoría (`created_by`, `updated_by`, timestamps).
- Alt obligatorio; crédito opcional.
- Imágenes de R2 con límite de 8 MB y tipos WebP/JPEG/PNG.
- El cuerpo HTML se sanitiza en el API con `nh3` antes de guardar/publicar.

---

## 7. Contrato del API

### Público (sin auth, cacheado)

```http
GET /publico/sitio
GET /publico/categorias
GET /publico/noticias?categoria=&page=&destacada=
GET /publico/noticias/{slug}
GET /publico/paginas/{slug}
```

Respuesta de noticia (ejemplo):

```json
{
  "slug": "asi-cuidamos-el-agua-que-llega-a-tu-casa",
  "titulo": "Así cuidamos el agua que llega a tu casa",
  "bajada": "Un recorrido por el proceso...",
  "categoria": "nuestra-operacion",
  "fecha": "2026-10-22",
  "autor": "Equipo Acuaricaurte",
  "imagen": "https://pub-xxxx.r2.dev/noticias/2026/10/archivo.webp",
  "imagenAlt": "Tanque circular de agua...",
  "imagenCredito": "Foto de referencia...",
  "destacada": true,
  "resumenFacil": "El agua sale de la quebrada...",
  "cuerpo": "<p>...</p>",
  "seo": { "titulo": "...", "descripcion": "..." }
}
```

El frontend ya tiene el adaptador en `web/src/lib/content.ts`:
si `ACR_API_URL` está definido, consulta el API; si falla o está vacío, usa
`web/src/data/` como fallback de desarrollo.

### Administración (JWT + rol)

```http
GET/POST/PATCH/DELETE /contenido/noticias
POST /contenido/noticias/{id}/publicar
POST /contenido/noticias/{id}/despublicar
GET/POST/PATCH/DELETE /contenido/categorias
GET/PATCH /contenido/sitio
GET/PATCH /contenido/paginas/{slug}
POST /contenido/media/presign
POST /contenido/media/confirmar
```

Roles: `admin` (todo), `comunicaciones` (solo contenido), `administrativo`
(según decisión), `operario` y `fontanero` sin acceso.

---

## 8. Flujo editorial

1. La persona de comunicaciones crea un borrador.
2. Se previsualiza en **staging** (sitio con borradores, protegido con Cloudflare
   Access).
3. La junta revisa y aprueba.
4. Se publica o programa la fecha.
5. El API llama el deploy hook de Cloudflare.
6. El sitio se reconstruye y queda online.
7. Despublicar/archivar no borra el historial.

### Reglas de contenido

- Títulos claros, sin sensacionalismo.
- Bajada de máximo ~160 caracteres.
- Párrafos cortos; subtítulos cada 2–3 párrafos.
- “En 30 segundos” para noticias clave.
- Fotos reales de Acuaricaurte; no usar imágenes de stock como si fueran propias.
- Consentimiento para personas identificables, especialmente menores.
- No publicar cifras de usuarios, facturación ni cobertura: la organización
  decidió no exponerlas.

---

## 9. Build y despliegue

### Local

```bash
cd web
cp .env.example .env
npm install
npm run dev
```

### Producción

```bash
npm run build      # astro check + astro build + pagefind
npm run preview
```

### Vercel

| Campo | Valor |
|---|---|
| Framework preset | Astro |
| Root directory | `web` |
| Build command | `npm run build` |
| Output directory | `dist` |
| Node version | 22.23.4+ (ideal 24) |
| Variables | `SITE_URL`, `ACR_API_URL`, `R2_PUBLIC_HOST`, `PUBLIC_CF_ANALYTICS_TOKEN`, `PUBLIC_TURNSTILE_SITE_KEY`, `BREVO_API_KEY`, `BREVO_FROM_EMAIL`, `BREVO_FROM_NAME`, `CONTACTO_TO_EMAIL`, `TURNSTILE_SECRET_KEY`, `EMAIL_LOGO_URL` (opcional) |

La función `api/contacto.ts` se detecta como **Edge Function**. `vercel.json`
define los headers de seguridad y caché. Las variables de producción se
configuran en **Project Settings → Environment Variables**; `.env` es solo para
desarrollo local.

Al publicar desde el CMS, el API debe llamar el **deploy hook** de Vercel.
Agregar un rebuild diario para noticias programadas.

---

## 10. Calidad y pruebas

- `npm run check`: Astro Check sin errores.
- `npm run build`: build estático + índice Pagefind.
- `scripts/check-overflow.mjs`: detecta desbordes horizontales en 390/768/1440.
- `scripts/smoke-test.mjs`: 44 checks de navegación, menú, accesibilidad,
  filtros, artículo, búsqueda, formulario de contacto, selector de motivo,
  validación inline, 404 y desbordes.
- Lighthouse móvil (contacto, 5 nov 2026): **99 Performance · 100 Accessibility ·
  100 Best Practices · 100 SEO**; LCP 1.7 s, CLS 0.
- Lighthouse CI (pendiente): automatizar el presupuesto en GitHub Actions.
- axe-core / Playwright (pendiente): ampliar a todas las páginas y flujos.
- Pruebas de API (pendiente): permisos, publicación, sanitización, scheduling.
- Revisión manual: teclado, lector de pantalla, zoom 200 %, móvil real.

---

## 11. Estado actual

### Implementado

- [x] Proyecto Astro 7 + TypeScript en `web/`.
- [x] Sistema de diseño “señalética pública + boletín”: Archivo + Newsreader,
  papel, tinta, reglas, botones rectangulares y mapa del sistema.
- [x] Home con portada institucional fija, tablón de avisos, mapa del agua,
  archivo de noticias y acceso a la Comisión Empresarial.
- [x] Listado y detalle de noticias con compartir, relacionadas y JSON-LD.
- [x] Quiénes somos, Nuestra agua y Contacto rediseñados como directorio/archivo.
- [x] Formulario de contacto con Brevo, Turnstile y plantillas de correo para el
  administrador y el usuario.
- [x] Micrositio de una página para la Comisión Empresarial, delegada de la
  Junta de Acción Comunal.
- [x] Búsqueda Pagefind, RSS, sitemap, robots y 404.
- [x] Header fijo, menú móvil, accesibilidad de texto/contraste y WhatsApp móvil.
- [x] Logo ACR real en header, footer, favicon, manifest y Open Graph.
- [x] Contenido local de demostración y adaptador para el API.
- [x] Documentación de plan, herramientas y agente.
- [x] Smoke test de 46 checks, Lighthouse móvil **100/100/100/100** en home,
  Quiénes somos y contacto, e Impeccable detect **0 hallazgos** en home,
  Quiénes somos, Comisión y páginas principales.

### Pendiente

- [ ] Endpoints `/publico/*` y `/contenido/*` en FastAPI.
- [ ] Migración MySQL + modelos + schemas + tests.
- [ ] Módulo “Contenido” en el CMS Vue (Tiptap, configuración).
- [ ] Subida de imágenes de contenido a R2 con alt obligatorio.
- [ ] Deploy hook y staging.
- [ ] Verificar variables de Brevo/Turnstile en Vercel y el dominio de
  producción.
- [ ] Reemplazo de fotos de noticias por material real; las fotos
  institucionales ya están configuradas.
- [ ] Validar el texto público de la Comisión Empresarial con la Junta de
  Acción Comunal.
- [ ] Revisión legal de privacidad.
- [ ] Lighthouse CI, axe/Playwright, monitoreo y analítica.
- [ ] Capacitación a la persona que publicará.

---

## 12. Criterios de aceptación

- [ ] Las 5 páginas públicas + 404 + privacidad funcionan en móvil y escritorio.
- [ ] Noticias: crear, editar, previsualizar, publicar, programar y archivar.
- [ ] Configuración de sitio editable (WhatsApp, redes, contacto, logo, footer).
- [ ] Imágenes con alt obligatorio y optimización responsive.
- [ ] Deploy automático al publicar; staging para revisión.
- [ ] Lighthouse móvil ≥ 95 en las 4 categorías.
- [ ] WCAG 2.2 AA verificado con axe + teclado + lector de pantalla.
- [ ] SEO técnico completo (sitemap, RSS, OG, JSON-LD, canonical).
- [ ] El sitio no depende del API en runtime.
- [ ] Documentación y manual de contenido entregados.
- [ ] Capacitación realizada.

---

## 13. Riesgos

| Riesgo | Mitigación |
|---|---|
| No hay fotos propias | Sesión de fotos en El Tejar, planta, tanque y comunidad; consentimiento |
| No hay logo vectorial | Mini sprint de marca; wordmark + gota/onda + favicon + OG |
| Datos de usuarios/facturación | No publicar cifras; la organización decidió no exponerlas |
| Editores con poca experiencia | CMS guiado, staging, manual con capturas y capacitación |
| Conectividad baja | Sitio estático, imágenes optimizadas, sin video ni terceros |
| API caída al publicar | La versión anterior sigue online; reintento y rebuild programado |
| Scope creep | Congelar v1; PQR/pagos en Fase 6 |
| Datos sensibles de planta | No exponer parámetros ni estado operativo sin autorización |
| Derechos de imagen | Consentimiento escrito; créditos; reemplazar stock |
| Legal | Política de privacidad y términos revisados; sin formularios en v1 |

---

## 14. Costos estimados

| Concepto | Costo |
|---|---|
| Dominio `.com`/`.co` | ~USD 10–30/año |
| Vercel | Gratis (plan Hobby) |
| Cloudflare R2 | Centavos al mes |
| API + MySQL | Ya existe; si se migra, ~USD 5–15/mes |
| Cloudflare Images (opcional) | ~USD 5/mes |
| Analítica | Gratis (Cloudflare Web Analytics) |
| Fotos / logo | A cotizar |
| Licencias CMS | USD 0 |

---

## 15. Referencias

- Herramientas, repos y referencias: `docs/07-herramientas-y-referencias.md`.
- Agente de la fase: `agents/web-agent.md`.
- Código: `web/`.
- Créditos de imágenes provisionales: `web/CREDITS.md`.
- Contenido demo y pendientes: `web/CONTENIDO-DEMO.md`.

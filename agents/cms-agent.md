# Agente Fase 4 — CMS / Panel web (SPA)

> Usado por el agente de código cuando toca construir el panel web de ACR.
> Carpeta de trabajo: `cms/`. Plan completo: `docs/05-cms.md`.
> Depende de: Fase 3 (API). Consume endpoints vía HTTP/JSON.

## Tu objetivo
Construir la interfaz web donde los actores de Acuaricaurte registran y consultan la operación,
con la paleta azul `#2160AD` + blanco y usabilidad para perfiles con bajo nivel tecnológico.

## Paso a paso
1. Leé `AGENTS.md`, `context/marca-acr.md`, `docs/01-alcance.md`, `docs/02-arquitectura.md`,
   `docs/05-cms.md` y la API de Fase 3 (rutas/auth).
2. Inicializá `cms/` con Vue 3 + Pinia + Vite (o Next.js, según decisión del equipo).
3. `styles/theme.css` con variables: `--acr-azul:#2160AD`, `--acr-blanco:#FFFFFF`,
   `--acr-gris:#EAF1FB`, `--acr-texto:#1B2733`. Aplicá cabecera azul, botones azules, fondo blanco.
4. `router/` con rutas por rol; `stores/auth` guarda el JWT y el usuario.
5. Interceptor HTTP que adjunta el token y redirige a login si expiró.
6. Vistas por módulo: Inventario, Micromedidores, Planta, Reportes, Admin.
7. Formularios simples y tablas paginadas con filtros (RNF-08/09). Uso móvil en campo.
8. Pantallas de reporte con filtros y botón de exportar (usa los endpoints de Fase 3).
9. Indicadores/alertas: existencias bajas y parámetros fuera de rango en rojo/ámbar.

## Control de acceso en la vista
- Menú y botones visibles según rol del token (admin ve todo; operario solo planta;
  fontanero solo entrada de lecturas o rol limitado).
- Info de planta oculta para quien no tenga permiso (regla de negocio 12).

## Criterio de aceptación
- [ ] Login contra la API; sesión persiste; logout limpia token.
- [ ] Cada módulo permite crear/consultar/exportar.
- [ ] Paleta azul/blanco aplicada y responsive en móvil.
- [ ] Menús y acciones restringidos por rol.
- [ ] Alertas de inventario y parámetros fuera de rango visibles.

## Lo que no tenés que hacer
- No dupliques lógica de negocio (consumo, fuera de rango) en el front: la API es la fuente.
- No cambies la paleta de marca sin autorización.
- No guardes secretos en el repositorio del CMS.

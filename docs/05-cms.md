# Plan Fase 4 — CMS / Panel web

> Entregable: `cms/` (SPA web). Agente: `agents/cms-agent.md`.
> Depende de: Fase 3 (API). Consume los endpoints vía HTTP/JSON.
> **Estado: ✅ implementado y compilando (`npm run build` OK).**

---

## Stack

- **Vue 3 + Vite + Pinia + Vue Router + Axios** (JavaScript, sin TypeScript).
- CSS propio con variables (sin librería de UI genérica). Sistema de diseño ACR en
  `cms/src/styles/theme.css`.
- Íconos SVG inline (`AppIcon.vue`), sin dependencias externas de iconos.

## Cómo ejecutar

```bash
cd cms
cp .env.example .env          # VITE_API_URL=http://127.0.0.1:8000
npm install
npm run dev                   # http://localhost:5173
npm run build                 # build de producción en dist/
```

El frontend llama **directo** a `VITE_API_URL` (CORS de la API es `*`, sin proxy).
Requiere que la API FastAPI (Fase 3) esté corriendo en el puerto configurado.

## Estructura de carpetas

```
cms/
  src/
    main.js                 # arranque Pinia + Router + interceptor HTTP
    api/http.js             # cliente Axios + interceptor JWT + helpers
    router/index.js         # rutas por rol + guardas (meta.roles / MODULOS)
    stores/                 # pinia: auth, inventario, micromedidores, planta, usuarios
    components/             # AppLayout, AppIcon, DataTable, BaseModal, BaseAlert, AppState
                           # components/planta/ (diagrama, modal de estado, configuración)
    views/                  # Login, Dashboard, Inventario, Micromedidores, Planta,
                           # Usuarios, NotFound
    styles/theme.css        # paleta y componentes ACR
```

## Endpoints consumidos por módulo

| Módulo CMS | Endpoints de la API |
|---|---|
| Auth | `POST /auth/login`, `GET /auth/me`, `POST /auth/refresh` |
| Inventario | `/inventario/categorias`, `/inventario` (GET/POST/PATCH/DELETE), `/inventario/{id}/entrada|salida`, `/inventario/movimientos`, `/inventario/alertas` |
| Micromedidores | `/suscriptores`, `/micromedidores`, `/lecturas`, `/consumo/sector/{sector}` |
| Planta | `/planta/parametros`, `/planta/mediciones`, `/planta/mediciones/fuera-rango`, `/planta/dosificaciones`, `/planta/actividades`, `/planta/horas-servicio`, `/planta/componentes`, `/planta/estados` (los químicos son insumos dentro de `/inventario`) |
| Exportaciones por módulo | `/reportes/inventario`, `/reportes/micromedidores`, `/reportes/planta` (`?formato=csv|xlsx|pdf`; incluye `tipo=estado-actual` y `tipo=historial-estados`), usados por los botones de cada vista |
| Usuarios/Roles | `/usuarios`, `/usuarios/{id}`, `/usuarios/roles` |

## Control de acceso por rol

El rol se obtiene de `GET /auth/me` (`user.rol.nombre`). El router y el sidebar
ocultan rutas/menús según el rol:

| Rol | Módulos visibles |
|---|---|
| `admin` | Inventario · Micromedidores · Planta · **Usuarios y roles** |
| `administrativo` | Inventario · Micromedidores |
| `operario` | Planta |
| `fontanero` | Micromedidores (registro de lecturas) |

Rutas protegidas con `meta.roles`; ante 401 el interceptor limpia el token y
redirige a `/login`. La info de planta queda oculta para quien no tiene permiso
(regla de negocio 12).

## Funcionalidad entregada

1. **Login** OAuth2 form → `access_token` en Pinia + `localStorage` + interceptor Bearer.
2. **Menú por rol** (sidebar y rutas filtradas en `router/index.js`).
3. **Inventario**: listar categorías/elementos, crear/editar/soft-delete, entrada/salida
   con motivo/observaciones, historial de movimientos y alertas bajo mínimo (rojo/ámbar).
4. **Micromedidores**: CRUD suscriptores y medidores, corrección del suscriptor asignado
   a un medidor (mueve también sus lecturas, sin borrarlas, y deja auditoría; solo
   admin/administrativo), registro de lectura (con opción "lectura estimada / usar
   promedio histórico" y campo novedad), listado de lecturas, consulta por sector y
   marcado de irregulares.
5. **Planta**: pestaña principal **Estado de la planta** con diagrama lineal,
   semáforo verde/amarillo/rojo, actualización de estado con nota obligatoria en
   afectación/fuera de servicio, historial de cambios y configuración de partes
   para el admin. El diagrama compacto se mantiene fijo entre las demás pestañas
   solo para el admin; el operario lo consulta en la pestaña Estado de la planta.
   Además: parámetros
   (cruda/tratada) con rangos min/máx, mediciones con detección visual `fuera_rango`
   (rojo) y acción correctiva, dosificaciones de químicos, actividades
   (limpieza/desinfección/tanques/bocatoma) y horas de servicio, más la vista de
   mediciones fuera de rango.
6. **Exportación desde cada módulo**: botones de descarga **CSV / Excel / PDF** con
   los filtros de la vista actual. No hay una vista central de Reportes; el admin
   puede generar el estado actual y el historial de estados desde Planta, y cada
   módulo conserva su propia exportación.
7. **Usuarios/Roles** (admin): listar/crear/desactivar usuarios y crear roles.
8. Estados de UI: loading, vacío y error; responsive para uso en campo (móvil).

## Nota de diseño (marca ACR)

Tema con variables `--acr-azul:#2160AD`, `--acr-blanco:#FFFFFF`, `--acr-gris:#EAF1FB`,
`--acr-texto:#1B2733` y semáforo `--acr-ok/--acr-warn/--acr-bad`. Cabecera azul, menú
lateral, tarjetas, tablas, formularios y botones a medida (sin plantilla admin genérica).
UI en español, acorde a Acuaricaurte (Ibagué, Tolima).

## Criterio de aceptación

- [x] Login contra la API; sesión persiste; logout limpia token.
- [x] Cada módulo permite crear/consultar/exportar.
- [x] Paleta azul/blanco aplicada y responsive en móvil.
- [x] Menús y acciones restringidos por rol.
- [x] Alertas de inventario y parámetros fuera de rango visibles.
- [x] Diagrama de estado editable por admin/operario con nota obligatoria en
  afectación y fuera de funcionamiento; el resumen fijo entre pestañas es solo admin.
- [x] Admin puede agregar, renombrar, reordenar y desactivar partes del diagrama.
- [x] Estado actual e historial de estados exportables en CSV/XLSX/PDF desde
  la pestaña Estado de la planta (admin).

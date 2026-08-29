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
    views/                  # Login, Dashboard, Inventario, Micromedidores, Planta,
                           # Reportes, Usuarios, NotFound
    styles/theme.css        # paleta y componentes ACR
```

## Endpoints consumidos por módulo

| Módulo CMS | Endpoints de la API |
|---|---|
| Auth | `POST /auth/login`, `GET /auth/me`, `POST /auth/refresh` |
| Inventario | `/inventario/categorias`, `/inventario` (GET/POST/PATCH/DELETE), `/inventario/{id}/entrada|salida`, `/inventario/movimientos`, `/inventario/alertas` |
| Micromedidores | `/suscriptores`, `/micromedidores`, `/lecturas`, `/consumo/sector/{sector}` |
| Planta | `/planta/parametros`, `/planta/mediciones`, `/planta/mediciones/fuera-rango`, `/planta/productos`, `/planta/dosificaciones`, `/planta/actividades`, `/planta/horas-servicio` |
| Reportes | `/reportes/inventario`, `/reportes/consumo`, `/reportes/planta` (`?formato=csv|xlsx|pdf`) |
| Usuarios/Roles | `/usuarios`, `/usuarios/{id}`, `/usuarios/roles` |

## Control de acceso por rol

El rol se obtiene de `GET /auth/me` (`user.rol.nombre`). El router y el sidebar
ocultan rutas/menús según el rol:

| Rol | Módulos visibles |
|---|---|
| `admin` | Inventario · Micromedidores · Planta · Reportes · **Usuarios y roles** |
| `administrativo` | Inventario · Micromedidores · Planta · Reportes |
| `operario` | Planta · Reportes |
| `fontanero` | Micromedidores (registro de lecturas) |

Rutas protegidas con `meta.roles`; ante 401 el interceptor limpia el token y
redirige a `/login`. La info de planta queda oculta para quien no tiene permiso
(regla de negocio 12).

## Funcionalidad entregada

1. **Login** OAuth2 form → `access_token` en Pinia + `localStorage` + interceptor Bearer.
2. **Menú por rol** (sidebar y rutas filtradas en `router/index.js`).
3. **Inventario**: listar categorías/elementos, crear/editar/soft-delete, entrada/salida
   con motivo/observaciones, historial de movimientos y alertas bajo mínimo (rojo/ámbar).
4. **Micromedidores**: CRUD suscriptores y medidores, registro de lectura (con opción
   "lectura estimada / usar promedio histórico" y campo novedad), listado de lecturas,
   consulta por sector y marcado de irregulares.
5. **Planta**: parámetros (cruda/tratada) con rangos min/máx, mediciones con detección
   visual `fuera_rango` (rojo) y acción correctiva, dosificaciones de químicos,
   actividades (limpieza/desinfección/tanques/bocatoma) y horas de servicio, más la
   vista de mediciones fuera de rango.
6. **Reportes**: selector de módulo + filtros (fecha/sector/estado) y exportación
   **CSV / Excel / PDF** vía `GET /reportes/...?formato=`.
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

# ACR · Panel web (CMS)

Interfaz operativa del **Acueducto Comunitario Acuaricaurte** (Ibagué, Tolima).
SPA construida con **Vue 3 + Vite + Pinia + Vue Router + Axios**, con tema propio
de marca (azul `#2160AD` + blanco) y control de acceso por rol.

Consume la API REST de la Fase 3 (FastAPI) que corre en
`http://127.0.0.1:8000` (Swagger en `/docs`).

---

## Stack

- **Vue 3** (Composition API, `<script setup>`)
- **Vite** como bundler / dev server
- **Pinia** para el estado (auth + cada módulo)
- **Vue Router** (history mode hash) con guardas por rol
- **Axios** con interceptor que adjunta el JWT y redirige a login ante 401
- CSS propio con variables (sin librería de UI genérica)

## Requisitos

- Node.js 18+ y npm.

## Puertos

- **CMS (dev):** `http://localhost:5173`
- **API (FastAPI):** `http://127.0.0.1:8000`  (debe estar corriendo)

## Instalación y ejecución

```bash
# 1. Instalar dependencias
cd cms
npm install

# 2. Configurar el destino de la API
cp .env.example .env          # o usa el .env ya incluido
#   VITE_API_URL=http://127.0.0.1:8000

# 3. Servidor de desarrollo (puerto 5173)
npm run dev

# 4. Build de producción
npm run build

# 5. Previsualizar el build
npm run preview
```

El frontend llama **directo** a `VITE_API_URL`. La API tiene CORS abierto (`*`),
por lo que no se necesita proxy.

## Login

- `POST /auth/login` (OAuth2 form: `username` + `password`).
- El `access_token` se guarda en Pinia y en `localStorage`; el interceptor Axios
  lo envía como `Authorization: Bearer <token>`.
- Si la API responde 401, se limpia la sesión y se redirige a `/login`.
- El rol se obtiene con `GET /auth/me` y controla menús y rutas.

## Acceso por rol

| Rol | Módulos visibles |
|---|---|
| `admin` | Inventario · Micromedidores · Planta · Reportes · **Usuarios y roles** |
| `administrativo` | Inventario · Micromedidores · Planta · Reportes |
| `operario` | Planta · Reportes |
| `fontanero` | Micromedidores (registro de lecturas) |

(Resto de rutas redirige a Inicio con aviso de acceso denegado.)

## Estructura de carpetas

```
cms/
  .env.example            # plantilla de configuración (VITE_API_URL)
  .env                    # configuración local (apunta a 127.0.0.1:8000)
  index.html
  package.json
  vite.config.js
  src/
    main.js               # arranque: pinia + router + interceptor HTTP
    App.vue               # raíz
    api/
      http.js             # cliente Axios + interceptor JWT + helpers de error
    router/
      index.js            # rutas por rol y guardas (meta.roles/MODULOS)
    stores/
      auth.js             # login, token, usuario, rol
      inventario.js       # categorías, elementos, movimientos, alertas
      micromedidores.js   # suscriptores, medidores, lecturas, consumo por sector
      planta.js           # parámetros, mediciones, productos, dosificaciones, actividades, horas
      usuarios.js         # usuarios y roles
    components/
      AppLayout.vue       # navbar + sidebar + router-view (autenticado)
      AppNavbar.vue       # (integrado en AppLayout)
      AppSidebar.vue      # (integrado en AppLayout)
      AppIcon.vue         # íconos SVG inline (sin dependencias externas)
      DataTable.vue       # tabla genérica con slots para celdas/acciones
      BaseModal.vue       # modal accesible (teleport + Esc)
      BaseAlert.vue       # banner de estado (ok/bad/warn/info)
      AppState.vue        # bloques loading/vacío/error
    views/
      Login.vue
      Dashboard.vue       # KPIs según rol + accesos rápidos
      InventarioView.vue  # tabs: Elementos · Movimientos · Alertas
      MicromedidoresView.vue # tabs: Suscriptores · Micromedidores · Lecturas · Por sector
      PlantaView.vue      # tabs: Parámetros · Mediciones · Fuera de rango · Dosificaciones · Actividades · Horas
      ReportesView.vue    # filtros + exportar CSV/XLSX/PDF
      UsuariosView.vue    # tabs: Usuarios · Roles (solo admin)
      NotFound.vue
    styles/
      theme.css           # sistema de diseño ACR (variables + componentes)
```

## Endpoints consumidos por módulo

- **Auth:** `POST /auth/login`, `GET /auth/me`, `POST /auth/refresh`
- **Inventario:** `/inventario/categorias`, `/inventario` (GET/POST/PATCH/DELETE),
  `/inventario/{id}/entrada|salida`, `/inventario/movimientos`, `/inventario/alertas`
- **Micromedidores:** `/suscriptores`, `/micromedidores`, `/lecturas`,
  `/consumo/sector/{sector}`
- **Planta:** `/planta/parametros`, `/planta/mediciones`,
  `/planta/mediciones/fuera-rango`, `/planta/productos`, `/planta/dosificaciones`,
  `/planta/actividades`, `/planta/horas-servicio`
- **Reportes:** `/reportes/inventario`, `/reportes/consumo`, `/reportes/planta`
  (`?formato=csv|xlsx|pdf`)
- **Usuarios/Roles:** `/usuarios`, `/usuarios/{id}`, `/usuarios/roles`

## Notas de diseño

- Paleta de marca ACR: `--acr-azul:#2160AD`, `--acr-blanco:#FFFFFF`,
  `--acr-gris:#EAF1FB`, `--acr-texto:#1B2733`, y semáforo
  `--acr-ok/--acr-warn/--acr-bad` para estados.
- UI en español, pensada para uso en campo (responsive; sidebar colapsable en móvil).
- La lógica de negocio (consumo, fuera de rango, promedio histórico, soft delete)
  vive en la API; el CMS solo consume y presenta.

## Ajustes de usabilidad

Mejoras aplicadas tras la primera prueba en campo (Fase 4):

- **Confirmaciones en eliminaciones/soft-delete:** todo inactivado o borrado
  (usuarios, elementos de inventario, suscriptores, micromedidores) pasa por
  `ConfirmModal` antes de llamar al store. El superadmin nunca se puede
  inactivar/eliminar (botón oculto en `UsuariosView`).
- **Contraseña con ojo:** `PasswordInput.vue` reemplaza los `<input type="password">`
  en Login y en crear/editar usuario, con botón de mostrar/ocultar (iconos `eye`/`eyeOff`).
- **Combobox filtrable:** `SearchableSelect.vue` sustituye los `<select>` nativos que
  listan muchos registros (categoría de inventario, suscriptor y micromedidor), con
  filtrado al escribir y opción `clearable`.
- **Botón Refrescar:** en la barra de herramientas de Usuarios, Inventario,
  Micromedidores, Planta y Reportes, invoca el `load` correspondiente del store.
- **Sección Categorías (Inventario):** nueva pestaña con tabla y modal
  "Nueva categoría" (`store.createCategoria` → `POST /inventario/categorias`).
- **Químicos (Planta):** nueva pestaña "Químicos" que lista productos con
  `cantidad_disponible` y permite crear uno nuevo (`createProducto`).
- **Todas las mediciones (Planta):** la pestaña "Mediciones" muestra todas las
  mediciones (`loadMediciones`), con parámetro, tipo de agua, valor, unidad, fecha,
  hora, responsable y badge `fuera_rango`; la pestaña "Fuera de rango" actúa como filtro.
- **Actividades con responsable (Planta):** la tabla de actividades ahora muestra
  responsable, estado, observaciones y evidencia; el formulario incluye un
  `SearchableSelect` de responsable que envía `responsable_id`.
- **Horas de servicio con responsable (Planta):** el formulario de horas de servicio
  incluye un `SearchableSelect` de responsable que envía `responsable_id`.

> Nota: para que `responsable_id` enviado desde el CMS sea respetado por la API, el
> router `planta.py` usa `payload.responsable_id or usuario.id` (el valor del
> formulario tiene prioridad sobre el usuario en sesión).

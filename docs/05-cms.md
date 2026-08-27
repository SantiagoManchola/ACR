# Plan Fase 4 — CMS / Panel web

> Entregable: `cms/` (SPA web). Agente: `agents/cms-agent.md`.
> Depende de: Fase 3 (API). Consume los endpoints vía HTTP/JSON.

---

## Objetivo
Interfaz web donde los actores de Acuaricaurte registran y consultan la operación, con la
paleta de marca azul `#2160AD` + blanco y usabilidad para perfiles con bajo nivel tecnológico.

## Stack propuesto
- **Vue 3 + Pinia + Vite** (o Next.js). SPA responsive (RNF-09).
- Cliente HTTP (axios/fetch) con interceptor de JWT.
- Tema con variables CSS: `--acr-azul:#2160AD`, `--acr-blanco:#FFFFFF`,
  `--acr-gris:#EAF1FB`, `--acr-texto:#1B2733`.
- Tablas con paginación y filtros; formularios de pasos mínimos (RNF-08).

## Estructura sugerida de `cms/`
```
cms/
  src/
    main.js
    App.vue
    router/            # rutas por rol
    stores/            # Pinia: auth, inventario, micromedidores, planta
    views/
      Login.vue
      Inventario/
      Micromedidores/
      Planta/
      Reportes/
      Admin/           # usuarios, roles
    components/        # tablas, formularios, alertas
    styles/theme.css   # paleta ACR
  package.json
```

## Pantallas por módulo
- **Login** + recuperación de sesión (guarda JWT).
- **Inventario:** listado con existencias y alertas (rojo/ámbar); alta de elemento;
  entrada/salida con responsable y motivo; historial de movimientos; reporte exportable.
- **Micromedidores:** alta de suscriptor y medidor; registro de lectura mensual;
  botón "usar promedio" cuando no hay lectura; novedades; histórico de consumo;
  consulta por sector; reporte.
- **Planta:** registro de parámetros (cruda/tratada) con detección visual fuera de rango;
  dosificación de químicos; actividades; horas de servicio; acciones correctivas.
- **Reportes:** filtros por fecha/sector/parámetro + exportar.
- **Admin:** gestión de usuarios, roles y permisos.

## Control de acceso en la vista
- Menú y rutas visibles según rol del token (admin ve todo; operario solo planta;
  fontanero ve solo entrada de lecturas vía administrativo o rol limitado).
- La info de planta oculta para quien no tenga permiso (regla de negocio 12).

## Criterio de aceptación
- [ ] Login funciona contra la API; sesión persiste.
- [ ] Cada módulo permite crear/consultar/exportar.
- [ ] Paleta azul/blanco aplicada y responsive en móvil.
- [ ] Menús y acciones restringidos por rol.
- [ ] Alertas de inventario y parámetros fuera de rango visibles.

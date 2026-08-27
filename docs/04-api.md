# Plan Fase 3 — API (FastAPI + MySQL)

> Entregable: `api/` (código FastAPI funcional). Agente: `agents/api-agent.md`.
> Depende de: Fase 2 (`datamodel/acr.dbml` → SQL).

---

## Objetivo
Exponer los módulos de ACR vía API REST segura, tipada y documentada, cumpliendo los RNF.

## Stack propuesto
- **FastAPI** + **Pydantic v2** (validaciones = RNF-06).
- **SQLAlchemy** (o SQLModel) + **MySQL**.
- **Auth:** JWT (python-jose / PyJWT) + contraseñas bcrypt.
- **Migraciones:** el SQL de Fase 2 como base; opcional Alembic para cambios.
- **Exportación:** pandas/openpyxl (Excel), csv, reportlab (PDF).

## Estructura sugerida de `api/`
```
api/
  app/
    main.py            # FastAPI app, CORS, routers
    db.py              # engine/session
    models.py          # SQLAlchemy models (desde DBML)
    schemas.py         # Pydantic
    security.py        # JWT, hashing, dependencias de permisos
    routers/
      auth.py
      usuarios.py
      inventario.py
      micromedidores.py
      planta.py
      reportes.py
    services/          # lógica de negocio ACR
  tests/
  pyproject.toml
  .env.example
```

## Endpoints por módulo (resumen)
- **Auth:** `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me`.
- **Usuarios/Roles:** CRUD `usuarios`, `roles`, asignación de rol.
- **Inventario:** CRUD `elementos_inventario`, `POST /inventario/{id}/entrada`,
  `POST /inventario/{id}/salida`, `GET /inventario/movimientos`,
  `GET /inventario/alertas` (por debajo de mínimo).
- **Micromedidores:** CRUD `suscriptores`, `micromedidores`, `POST /lecturas`,
  `GET /lecturas?micromedidor=&fecha=`, cálculo de consumo/promedio,
  `GET /consumo/sector/{sector}`.
- **Planta:** CRUD `parametros_planta`, `POST /mediciones` (marca fuera_rango),
  `POST /dosificaciones`, `POST /actividades`, `POST /horas-servicio`,
  `GET /mediciones/fuera-rango`.
- **Reportes:** `GET /reportes/inventario`, `/consumo`, `/planta` con filtros y
  `?formato=csv|xlsx|pdf`.

## Lógica de negocio ACR (services/)
- Cálculo de consumo = lectura_actual − lectura_anterior; si falta → promedio histórico.
- Detección automática fuera de rango al registrar medición (comparar con min/max).
- Soft delete (estado) en suscriptores/medidores/elementos.
- Todo write inyecta `usuario_actual` → `created_by`/`updated_by`.

## Criterio de aceptación
- [ ] Login + JWT funciona; rutas protegidas devuelven 401 sin token.
- [ ] Permisos por rol aplicados (p. ej. planta solo para operario/admin).
- [ ] CRUD de los 4 módulos operativos.
- [ ] Reportes exportan en CSV/Excel/PDF.
- [ ] Tests de endpoints críticos en verde.
- [ ] Swagger disponible en `/docs`.

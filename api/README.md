# API ACR — Acueducto Comunitario Acuaricaurte

Backend REST en **FastAPI + SQLAlchemy 2.0 + MySQL (pymysql)**.
Cumple RNF-03 (auth JWT), RNF-04 (permisos por rol), RNF-06 (Pydantic),
RNF-07 (trazabilidad) y RNF-19 (exportación CSV/XLSX/PDF).

## 1. Crear la base de datos

En MySQL (línea de comandos o cliente), crea la BD `acr` en utf8mb4 y el
usuario de la app, luego ejecuta el SQL de la Fase 2:

```sql
CREATE DATABASE acr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'acr_user'@'localhost' IDENTIFIED BY 'acr_password';
GRANT ALL PRIVILEGES ON acr.* TO 'acr_user'@'localhost';
FLUSH PRIVILEGES;
```

```bash
mysql -u acr_user -p acr < ../datamodel/migrations/acr_migrations.sql
```

> La variable `DATABASE_URL` (en `.env`) debe apuntar a esa BD:
> `mysql+pymysql://acr_user:acr_password@localhost:3306/acr`

## 2. Instalar dependencias

```bash
cd api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edita JWT_SECRET y credenciales
```

> El hashing de contraseñas usa `bcrypt` **directo** (sin `passlib`); la versión está
> fijada en `requirements.txt` (`bcrypt==4.1.3`). `seed.py` sigue siendo necesario para
> crear roles y el usuario admin.

## 3. Sembrar roles y usuario admin

```bash
python seed.py
```

Crea los roles `admin`, `administrativo`, `operario`, `fontanero` y un
usuario admin (credenciales desde `ADMIN_USERNAME`/`ADMIN_PASSWORD` del `.env`).

## 4. Ejecutar el API

```bash
uvicorn app.main:app --reload
```

El servidor queda en `http://127.0.0.1:8000`.

## 5. Swagger / OpenAPI

Documentación interactiva automática en **`/docs`**
(`http://127.0.0.1:8000/docs`). Esquema OpenAPI en `/openapi.json`.
Para autenticar: usa `POST /auth/login` (username/password) y pega el
`access_token` con el botón "Authorize" (prefijo `Bearer `).

## Estructura

```
api/
  app/
    main.py          # FastAPI app + CORS + routers
    config.py        # settings (pydantic-settings, desde .env)
    db.py            # engine / SessionLocal / Base
    models.py        # 16 tablas SQLAlchemy (MySQL)
    schemas.py       # Pydantic v2
    security.py      # JWT, bcrypt, get_current_user, require_role
    routers/         # auth, usuarios, inventario, micromedidores, planta, reportes
    services/        # lógica de negocio (consumo, fuera de rango, export, auditoría)
  seed.py            # roles base + admin
  requirements.txt
  .env.example
```

## Resumen de endpoints por módulo

- **Auth:** `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me`.
- **Usuarios/Roles:** `GET/POST /usuarios/roles`, `GET/POST /usuarios`,
  `GET/PATCH/DELETE /usuarios/{id}` (DELETE = soft delete).
- **Inventario:** `GET/POST /inventario`, `GET/PATCH/DELETE /inventario/{id}`,
  `POST /inventario/{id}/entrada`, `POST /inventario/{id}/salida`,
  `GET /inventario/movimientos`, `GET /inventario/alertas`.
- **Micromedidores:** `GET/POST /suscriptores`, `GET/POST /micromedidores`,
  `POST /lecturas` (calcula consumo/promedio), `GET /lecturas`,
  `GET /consumo/sector/{sector}`.
- **Planta:** `GET/POST /planta/parametros`, `POST /planta/mediciones`
  (marca `fuera_rango`), `GET /planta/mediciones/fuera-rango`,
  `GET/POST /planta/productos`, `POST /planta/dosificaciones`,
  `POST /planta/actividades`, `POST /planta/horas-servicio`.
- **Reportes:** `GET /reportes/inventario`, `/reportes/consumo`,
  `/reportes/planta` con `?formato=csv|xlsx|pdf` (sin formato = JSON).

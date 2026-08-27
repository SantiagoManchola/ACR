"""Script de inicialización: crea roles base y usuario admin.

Uso (desde la carpeta `api/` con la BD ya creada):
    python seed.py

Lee credenciales de entorno: ADMIN_USERNAME, ADMIN_PASSWORD, DATABASE_URL.
"""
from app.config import settings
from app.db import SessionLocal
from app.models import EstadoRegistro, Rol, Usuario
from app.security import hash_password

ROLES_BASE = ["admin", "administrativo", "operario", "fontanero"]


def main() -> None:
    db = SessionLocal()
    try:
        # Roles base
        for nombre in ROLES_BASE:
            existe = db.query(Rol).filter(Rol.nombre == nombre).first()
            if not existe:
                db.add(Rol(nombre=nombre, descripcion=f"Rol {nombre}"))
        db.commit()

        rol_admin = db.query(Rol).filter(Rol.nombre == "admin").first()

        # Usuario admin
        admin = db.query(Usuario).filter(Usuario.username == settings.admin_username).first()
        if not admin:
            admin = Usuario(
                nombre="Administrador ACR",
                username=settings.admin_username,
                password_hash=hash_password(settings.admin_password),
                rol_id=rol_admin.id,
                estado=EstadoRegistro.activo,
            )
            db.add(admin)
            db.commit()
            print(f"Usuario admin '{settings.admin_username}' creado.")
        else:
            print(f"Usuario admin '{settings.admin_username}' ya existe.")
        print("Roles base:", ", ".join(ROLES_BASE))
    finally:
        db.close()


if __name__ == "__main__":
    main()

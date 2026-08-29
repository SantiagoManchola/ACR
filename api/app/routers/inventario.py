"""Router de inventario (RF-06..RF-20)."""
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..schemas import (
    AlertaOut,
    CategoriaCreate,
    CategoriaOut,
    ElementoCreate,
    ElementoOut,
    ElementoUpdate,
    MovimientoCreate,
    MovimientoOut,
    TipoMovimiento,
)
from ..security import get_current_user, get_db, require_role
from ..services.common import sellar
from ..services import inventario as svc_inventario

router = APIRouter(prefix="/inventario", tags=["Inventario"])

_LECTORES = ["admin", "administrativo", "operario"]
_ESCRITORES = ["admin", "administrativo"]


# ----------------------------- Categorías ------------------------------------
@router.get("/categorias", response_model=list[CategoriaOut], summary="Listar categorías")
def listar_categorias(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_role(_LECTORES)),
):
    return db.execute(select(models.CategoriaInventario)).scalars().all()


@router.post(
    "/categorias",
    response_model=CategoriaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear categoría",
)
def crear_categoria(
    payload: CategoriaCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    cat = models.CategoriaInventario(
        nombre=payload.nombre, tipo=payload.tipo, descripcion=payload.descripcion
    )
    sellar(cat, usuario, nuevo=True)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


# ----------------------------- Elementos (lista/crear) -----------------------
@router.get("", response_model=list[ElementoOut], summary="Listar elementos")
def listar_elementos(
    nombre: str | None = None,
    categoria_id: int | None = None,
    estado: str | None = None,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_role(_LECTORES)),
):
    stmt = select(models.ElementoInventario)
    if nombre:
        stmt = stmt.where(models.ElementoInventario.nombre.ilike(f"%{nombre}%"))
    if categoria_id:
        stmt = stmt.where(models.ElementoInventario.categoria_id == categoria_id)
    if estado:
        stmt = stmt.where(models.ElementoInventario.estado == estado)
    return db.execute(stmt.order_by(models.ElementoInventario.nombre)).scalars().all()


@router.post(
    "",
    response_model=ElementoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear elemento de inventario",
)
def crear_elemento(
    payload: ElementoCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    if not db.get(models.CategoriaInventario, payload.categoria_id):
        raise HTTPException(400, "categoria_id inválido")
    elem = models.ElementoInventario(**payload.model_dump())
    sellar(elem, usuario, nuevo=True)
    db.add(elem)
    db.commit()
    db.refresh(elem)
    return elem


# ----------------------------- Movimientos y alertas (literales) -------------
# Importante: estas rutas literales deben registrarse ANTES de `/{elemento_id}`
# para no ser capturadas por el parámetro de ruta.
@router.get("/movimientos", response_model=list[MovimientoOut], summary="Historial de movimientos")
def movimientos(
    elemento_id: int | None = None,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_role(_LECTORES)),
):
    stmt = select(models.MovimientoInventario)
    if elemento_id:
        stmt = stmt.where(models.MovimientoInventario.elemento_id == elemento_id)
    return db.execute(stmt.order_by(models.MovimientoInventario.fecha.desc())).scalars().all()


@router.get("/alertas", response_model=list[AlertaOut], summary="Elementos y químicos bajo mínimo")
def alertas(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_role(_LECTORES)),
):
    return svc_inventario.alertas(db)


# ----------------------------- Detalle de elemento ----------------------------
@router.get("/{elemento_id}", response_model=ElementoOut, summary="Obtener elemento")
def obtener_elemento(
    elemento_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_role(_LECTORES)),
):
    elem = db.get(models.ElementoInventario, elemento_id)
    if not elem:
        raise HTTPException(404, "Elemento no encontrado")
    return elem


@router.patch("/{elemento_id}", response_model=ElementoOut, summary="Actualizar elemento")
def actualizar_elemento(
    elemento_id: int,
    payload: ElementoUpdate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    elem = db.get(models.ElementoInventario, elemento_id)
    if not elem:
        raise HTTPException(404, "Elemento no encontrado")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(elem, k, v)
    sellar(elem, usuario, nuevo=False)
    db.commit()
    db.refresh(elem)
    return elem


@router.delete("/{elemento_id}", summary="Eliminar elemento (soft delete)")
def eliminar_elemento(
    elemento_id: int,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    elem = db.get(models.ElementoInventario, elemento_id)
    if not elem:
        raise HTTPException(404, "Elemento no encontrado")
    elem.estado = models.EstadoRegistro.inactivo
    sellar(elem, usuario, nuevo=False)
    db.commit()
    return {"ok": True, "mensaje": "Elemento inactivado"}


# ----------------------------- Entradas / salidas -----------------------------
@router.post("/{elemento_id}/entrada", response_model=MovimientoOut, summary="Registrar entrada")
def entrada(
    elemento_id: int,
    payload: MovimientoCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    elem = db.get(models.ElementoInventario, elemento_id)
    if not elem:
        raise HTTPException(404, "Elemento no encontrado")
    fecha = payload.fecha or date.today()
    hora = payload.hora or datetime.now().time()
    svc_inventario.aplicar_movimiento(
        db, elem, TipoMovimiento.entrada, float(payload.cantidad),
        usuario.id, payload.motivo, payload.observaciones, fecha, hora,
    )
    sellar(elem, usuario, nuevo=False)
    db.commit()
    mov = db.execute(
        select(models.MovimientoInventario)
        .where(models.MovimientoInventario.elemento_id == elemento_id)
        .order_by(models.MovimientoInventario.id.desc())
    ).scalars().first()
    return mov


@router.post("/{elemento_id}/salida", response_model=MovimientoOut, summary="Registrar salida")
def salida(
    elemento_id: int,
    payload: MovimientoCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    elem = db.get(models.ElementoInventario, elemento_id)
    if not elem:
        raise HTTPException(404, "Elemento no encontrado")
    fecha = payload.fecha or date.today()
    hora = payload.hora or datetime.now().time()
    svc_inventario.aplicar_movimiento(
        db, elem, TipoMovimiento.salida, float(payload.cantidad),
        usuario.id, payload.motivo, payload.observaciones, fecha, hora,
    )
    sellar(elem, usuario, nuevo=False)
    db.commit()
    mov = db.execute(
        select(models.MovimientoInventario)
        .where(models.MovimientoInventario.elemento_id == elemento_id)
        .order_by(models.MovimientoInventario.id.desc())
    ).scalars().first()
    return mov

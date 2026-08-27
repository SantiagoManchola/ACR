"""Router de micromedidores (RF-21..RF-36)."""
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..schemas import (
    LecturaCreate,
    LecturaOut,
    MicromedidorCreate,
    MicromedidorOut,
    MicromedidorUpdate,
    SuscriptorCreate,
    SuscriptorOut,
    SuscriptorUpdate,
)
from ..security import get_current_user, get_db, require_role
from ..services.common import sellar
from ..services import micromedidores as svc_mm

router = APIRouter(prefix="", tags=["Micromedidores"])

_LECTORES = ["admin", "administrativo", "operario", "fontanero"]
_ESCRITORES = ["admin", "administrativo"]


# ----------------------------- Suscriptores ----------------------------------
@router.get("/suscriptores", response_model=list[SuscriptorOut], summary="Listar suscriptores")
def listar_suscriptores(
    db: Session = Depends(get_db), _: models.Usuario = Depends(require_role(_LECTORES))
):
    return db.execute(select(models.Suscriptor)).scalars().all()


@router.post(
    "/suscriptores",
    response_model=SuscriptorOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear suscriptor",
)
def crear_suscriptor(
    payload: SuscriptorCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    sus = models.Suscriptor(**payload.model_dump())
    sellar(sus, usuario, nuevo=True)
    db.add(sus)
    db.commit()
    db.refresh(sus)
    return sus


@router.get("/suscriptores/{sid}", response_model=SuscriptorOut, summary="Obtener suscriptor")
def obtener_suscriptor(
    sid: int, db: Session = Depends(get_db), _: models.Usuario = Depends(require_role(_LECTORES))
):
    sus = db.get(models.Suscriptor, sid)
    if not sus:
        raise HTTPException(404, "Suscriptor no encontrado")
    return sus


@router.patch("/suscriptores/{sid}", response_model=SuscriptorOut, summary="Actualizar suscriptor")
def actualizar_suscriptor(
    sid: int,
    payload: SuscriptorUpdate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    sus = db.get(models.Suscriptor, sid)
    if not sus:
        raise HTTPException(404, "Suscriptor no encontrado")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(sus, k, v)
    sellar(sus, usuario, nuevo=False)
    db.commit()
    db.refresh(sus)
    return sus


@router.delete("/suscriptores/{sid}", summary="Eliminar suscriptor (soft delete)")
def eliminar_suscriptor(
    sid: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(require_role(_ESCRITORES))
):
    sus = db.get(models.Suscriptor, sid)
    if not sus:
        raise HTTPException(404, "Suscriptor no encontrado")
    sus.estado = models.EstadoRegistro.inactivo
    sellar(sus, usuario, nuevo=False)
    db.commit()
    return {"ok": True}


# ----------------------------- Micromedidores --------------------------------
@router.get("/micromedidores", response_model=list[MicromedidorOut], summary="Listar micromedidores")
def listar_micromedidores(
    db: Session = Depends(get_db), _: models.Usuario = Depends(require_role(_LECTORES))
):
    return db.execute(select(models.Micromedidor)).scalars().all()


@router.post(
    "/micromedidores",
    response_model=MicromedidorOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear micromedidor",
)
def crear_micromedidor(
    payload: MicromedidorCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    if payload.suscriptor_id and not db.get(models.Suscriptor, payload.suscriptor_id):
        raise HTTPException(400, "suscriptor_id inválido")
    mm = models.Micromedidor(**payload.model_dump())
    sellar(mm, usuario, nuevo=True)
    db.add(mm)
    db.commit()
    db.refresh(mm)
    return mm


@router.get("/micromedidores/{mid}", response_model=MicromedidorOut, summary="Obtener micromedidor")
def obtener_micromedidor(
    mid: int, db: Session = Depends(get_db), _: models.Usuario = Depends(require_role(_LECTORES))
):
    mm = db.get(models.Micromedidor, mid)
    if not mm:
        raise HTTPException(404, "Micromedidor no encontrado")
    return mm


@router.patch("/micromedidores/{mid}", response_model=MicromedidorOut, summary="Actualizar micromedidor")
def actualizar_micromedidor(
    mid: int,
    payload: MicromedidorUpdate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    mm = db.get(models.Micromedidor, mid)
    if not mm:
        raise HTTPException(404, "Micromedidor no encontrado")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(mm, k, v)
    sellar(mm, usuario, nuevo=False)
    db.commit()
    db.refresh(mm)
    return mm


@router.delete("/micromedidores/{mid}", summary="Eliminar micromedidor (soft delete)")
def eliminar_micromedidor(
    mid: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(require_role(_ESCRITORES))
):
    mm = db.get(models.Micromedidor, mid)
    if not mm:
        raise HTTPException(404, "Micromedidor no encontrado")
    mm.estado = models.EstadoRegistro.inactivo
    sellar(mm, usuario, nuevo=False)
    db.commit()
    return {"ok": True}


# ----------------------------- Lecturas --------------------------------------
@router.post(
    "/lecturas",
    response_model=LecturaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar lectura (calcula consumo/promedio)",
)
def crear_lectura(
    payload: LecturaCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    if not db.get(models.Micromedidor, payload.micromedidor_id):
        raise HTTPException(400, "micromedidor_id inválido")
    if not db.get(models.Suscriptor, payload.suscriptor_id):
        raise HTTPException(400, "suscriptor_id inválido")

    consumo, promedio_usado = svc_mm.calcular_consumo(
        db, payload.micromedidor_id, payload.lectura, payload.fecha
    )
    lectura = models.Lectura(
        micromedidor_id=payload.micromedidor_id,
        suscriptor_id=payload.suscriptor_id,
        fecha=payload.fecha,
        hora=payload.hora,
        lectura=payload.lectura,
        consumo=consumo,
        promedio_usado=promedio_usado,
        responsable_id=usuario.id,
        novedad=payload.novedad,
        irregular=payload.irregular,
    )
    sellar(lectura, usuario, nuevo=True)
    db.add(lectura)
    db.commit()
    db.refresh(lectura)
    return lectura


@router.get("/lecturas", response_model=list[LecturaOut], summary="Consultar lecturas")
def listar_lecturas(
    micromedidor_id: int | None = None,
    suscriptor_id: int | None = None,
    fecha: str | None = None,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_role(_LECTORES)),
):
    stmt = select(models.Lectura)
    if micromedidor_id:
        stmt = stmt.where(models.Lectura.micromedidor_id == micromedidor_id)
    if suscriptor_id:
        stmt = stmt.where(models.Lectura.suscriptor_id == suscriptor_id)
    if fecha:
        stmt = stmt.where(models.Lectura.fecha == fecha)
    return db.execute(stmt.order_by(models.Lectura.fecha.desc())).scalars().all()


@router.get(
    "/consumo/sector/{sector}",
    response_model=list[LecturaOut],
    summary="Lecturas/consumo por sector (RF-34)",
)
def consumo_por_sector(
    sector: str,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_role(_LECTORES)),
):
    stmt = (
        select(models.Lectura)
        .join(models.Suscriptor, models.Lectura.suscriptor_id == models.Suscriptor.id)
        .where(models.Suscriptor.sector == sector)
        .order_by(models.Lectura.fecha.desc())
    )
    return db.execute(stmt).scalars().all()

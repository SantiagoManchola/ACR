"""Router de planta de tratamiento (RF-37..RF-54)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..schemas import (
    ActividadCreate,
    ActividadOut,
    ActividadUpdate,
    DosificacionCreate,
    DosificacionOut,
    HoraServicioCreate,
    HoraServicioOut,
    MedicionCreate,
    MedicionOut,
    ParametroCreate,
    ParametroOut,
    ParametroUpdate,
    ProductoCreate,
    ProductoOut,
)
from ..security import get_current_user, get_db, require_role
from ..services.common import sellar
from ..services import planta as svc_planta

router = APIRouter(prefix="/planta", tags=["Planta de tratamiento"])

_LECTORES = ["admin", "operario", "administrativo"]
_ESCRITORES = ["admin", "operario"]


# ----------------------------- Parámetros ------------------------------------
@router.get("/parametros", response_model=list[ParametroOut], summary="Listar parámetros")
def listar_parametros(
    db: Session = Depends(get_db), _: models.Usuario = Depends(require_role(_LECTORES))
):
    return db.execute(select(models.ParametroPlanta)).scalars().all()


@router.post(
    "/parametros",
    response_model=ParametroOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear parámetro",
)
def crear_parametro(
    payload: ParametroCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    p = models.ParametroPlanta(**payload.model_dump())
    sellar(p, usuario, nuevo=True)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.patch("/parametros/{pid}", response_model=ParametroOut, summary="Actualizar parámetro")
def actualizar_parametro(
    pid: int,
    payload: ParametroUpdate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    p = db.get(models.ParametroPlanta, pid)
    if not p:
        raise HTTPException(404, "Parámetro no encontrado")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    sellar(p, usuario, nuevo=False)
    db.commit()
    db.refresh(p)
    return p


# ----------------------------- Mediciones ------------------------------------
@router.post(
    "/mediciones",
    response_model=MedicionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar medición (marca fuera de rango)",
)
def crear_medicion(
    payload: MedicionCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    parametro = db.get(models.ParametroPlanta, payload.parametro_id)
    if not parametro:
        raise HTTPException(400, "parametro_id inválido")
    fuera = svc_planta.fuera_de_rango(parametro, payload.valor)
    med = models.Medicion(
        parametro_id=payload.parametro_id,
        valor=payload.valor,
        fecha=payload.fecha,
        hora=payload.hora,
        responsable_id=usuario.id,
        fuera_rango=fuera,
        accion_correctiva=payload.accion_correctiva,
        observaciones=payload.observaciones,
    )
    sellar(med, usuario, nuevo=True)
    db.add(med)
    db.commit()
    db.refresh(med)
    return med


@router.get("/mediciones/fuera-rango", response_model=list[MedicionOut], summary="Mediciones fuera de rango")
def mediciones_fuera_rango(
    db: Session = Depends(get_db), _: models.Usuario = Depends(require_role(_LECTORES))
):
    return db.execute(
        select(models.Medicion).where(models.Medicion.fuera_rango.is_(True))
        .order_by(models.Medicion.fecha.desc())
    ).scalars().all()


# ----------------------------- Productos / dosificación ----------------------
@router.get("/productos", response_model=list[ProductoOut], summary="Listar productos químicos")
def listar_productos(
    db: Session = Depends(get_db), _: models.Usuario = Depends(require_role(_LECTORES))
):
    return db.execute(select(models.ProductoQuimico)).scalars().all()


@router.post(
    "/productos",
    response_model=ProductoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto químico",
)
def crear_producto(
    payload: ProductoCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    p = models.ProductoQuimico(**payload.model_dump())
    sellar(p, usuario, nuevo=True)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.post(
    "/dosificaciones",
    response_model=DosificacionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar dosificación",
)
def crear_dosificacion(
    payload: DosificacionCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    if not db.get(models.ProductoQuimico, payload.producto_id):
        raise HTTPException(400, "producto_id inválido")
    d = models.Dosificacion(
        producto_id=payload.producto_id,
        cantidad=payload.cantidad,
        fecha=payload.fecha,
        hora=payload.hora,
        responsable_id=usuario.id,
        observaciones=payload.observaciones,
    )
    sellar(d, usuario, nuevo=True)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


# ----------------------------- Actividades -----------------------------------
@router.post(
    "/actividades",
    response_model=ActividadOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar actividad de planta",
)
def crear_actividad(
    payload: ActividadCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    a = models.ActividadPlanta(
        tipo=payload.tipo,
        fecha=payload.fecha,
        hora=payload.hora,
        responsable_id=usuario.id,
        observaciones=payload.observaciones,
        evidencia=payload.evidencia,
        estado=models.EstadoRegistro.activo,
    )
    sellar(a, usuario, nuevo=True)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@router.patch("/actividades/{aid}", response_model=ActividadOut, summary="Actualizar actividad")
def actualizar_actividad(
    aid: int,
    payload: ActividadUpdate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    a = db.get(models.ActividadPlanta, aid)
    if not a:
        raise HTTPException(404, "Actividad no encontrada")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(a, k, v)
    sellar(a, usuario, nuevo=False)
    db.commit()
    db.refresh(a)
    return a


# ----------------------------- Horas de servicio -----------------------------
@router.post(
    "/horas-servicio",
    response_model=HoraServicioOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar horas de servicio",
)
def crear_horas(
    payload: HoraServicioCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(require_role(_ESCRITORES)),
):
    h = models.HoraServicio(
        fecha=payload.fecha,
        horas=payload.horas,
        responsable_id=usuario.id,
        observaciones=payload.observaciones,
    )
    sellar(h, usuario, nuevo=True)
    db.add(h)
    db.commit()
    db.refresh(h)
    return h

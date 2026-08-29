"""Lógica de micromedidores: cálculo de consumo y promedio histórico.

Regla de negocio 1 y 2: lectura mensual; si no hay lectura previa válida se
usa el promedio histórico (promedio_usado=True, consumo=promedio o NULL).
"""
from datetime import date
from decimal import Decimal
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models


def calcular_consumo(
    db: Session,
    micromedidor_id: int,
    lectura: Decimal,
    fecha,
) -> tuple[Decimal | None, bool]:
    """Devuelve (consumo, promedio_usado)."""
    previa = (
        db.execute(
            select(models.Lectura)
            .where(
                models.Lectura.micromedidor_id == micromedidor_id,
                models.Lectura.fecha < fecha,
            )
            .order_by(models.Lectura.fecha.desc())
        )
        .scalars()
        .first()
    )

    if previa is not None and previa.lectura is not None:
        return (Decimal(str(lectura)) - Decimal(str(previa.lectura))), False

    promedio = db.execute(
        select(func.avg(models.Lectura.consumo)).where(
            models.Lectura.micromedidor_id == micromedidor_id,
            models.Lectura.consumo.isnot(None),
        )
    ).scalar()
    return promedio, True


def filtrar_suscriptores(db: Session, *, nombre=None, identificacion=None, sector=None, tipo_usuario=None):
    stmt = select(models.Suscriptor)
    if nombre:
        stmt = stmt.where(models.Suscriptor.nombre.ilike(f"%{nombre}%"))
    if identificacion:
        stmt = stmt.where(models.Suscriptor.identificacion.ilike(f"%{identificacion}%"))
    if sector:
        stmt = stmt.where(models.Suscriptor.sector == sector)
    if tipo_usuario:
        stmt = stmt.where(models.Suscriptor.tipo_usuario == tipo_usuario)
    return db.execute(stmt.order_by(models.Suscriptor.nombre)).scalars().all()


def filtrar_micromedidores(db: Session, *, serial=None, suscriptor_id=None, estado=None, sector=None):
    stmt = select(models.Micromedidor)
    if serial:
        stmt = stmt.where(models.Micromedidor.serial.ilike(f"%{serial}%"))
    if suscriptor_id:
        stmt = stmt.where(models.Micromedidor.suscriptor_id == suscriptor_id)
    if estado:
        stmt = stmt.where(models.Micromedidor.estado == estado)
    if sector:
        stmt = stmt.join(models.Suscriptor, models.Micromedidor.suscriptor_id == models.Suscriptor.id)
        stmt = stmt.where(models.Suscriptor.sector == sector)
    return db.execute(stmt.order_by(models.Micromedidor.serial)).scalars().all()


def filtrar_lecturas(db: Session, *, micromedidor_id=None, suscriptor_id=None,
                     sector=None, fecha_inicio=None, fecha_fin=None):
    stmt = select(models.Lectura)
    if micromedidor_id:
        stmt = stmt.where(models.Lectura.micromedidor_id == micromedidor_id)
    if suscriptor_id:
        stmt = stmt.where(models.Lectura.suscriptor_id == suscriptor_id)
    if sector:
        stmt = stmt.join(models.Suscriptor, models.Lectura.suscriptor_id == models.Suscriptor.id)
        stmt = stmt.where(models.Suscriptor.sector == sector)
    if fecha_inicio:
        stmt = stmt.where(models.Lectura.fecha >= fecha_inicio)
    if fecha_fin:
        stmt = stmt.where(models.Lectura.fecha <= fecha_fin)
    return db.execute(stmt.order_by(models.Lectura.fecha.desc())).scalars().all()


def sectores_disponibles(db: Session):
    return [s for (s,) in db.execute(
        select(models.Suscriptor.sector).where(models.Suscriptor.sector.isnot(None))
        .distinct().order_by(models.Suscriptor.sector)
    ).all()]


def historial_suscriptor(db: Session, sid: int):
    suscriptor = db.get(models.Suscriptor, sid)
    micromedidores = db.execute(
        select(models.Micromedidor).where(models.Micromedidor.suscriptor_id == sid)
    ).scalars().all()
    lecturas = db.execute(
        select(models.Lectura).where(models.Lectura.suscriptor_id == sid)
        .order_by(models.Lectura.fecha.desc())
    ).scalars().all()
    return {
        "suscriptor": suscriptor,
        "micromedidores": micromedidores,
        "lecturas": lecturas,
    }


def historial_micromedidor(db: Session, mid: int):
    micromedidor = db.get(models.Micromedidor, mid)
    lecturas = db.execute(
        select(models.Lectura).where(models.Lectura.micromedidor_id == mid)
        .order_by(models.Lectura.fecha.desc())
    ).scalars().all()
    return {
        "micromedidor": micromedidor,
        "lecturas": lecturas,
    }

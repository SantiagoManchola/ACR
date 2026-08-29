"""Lógica de planta: detección de valores fuera de rango (RF-48/RF-49)."""
from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models


def fuera_de_rango(parametro: models.ParametroPlanta, valor: Decimal) -> bool:
    """Compara el valor con valor_min/valor_max configurables (regla 9)."""
    v = Decimal(str(valor))
    if parametro.valor_min is not None and v < Decimal(str(parametro.valor_min)):
        return True
    if parametro.valor_max is not None and v > Decimal(str(parametro.valor_max)):
        return True
    return False


def aplicar_dosificacion(db: Session, producto: models.ProductoQuimico, cantidad: Decimal):
    """Descuenta la cantidad dosificada del stock disponible del químico (punto 5)."""
    disponible = Decimal(str(producto.cantidad_disponible or 0))
    c = Decimal(str(cantidad))
    if c > disponible:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock insuficiente de '{producto.nombre}': disponible {disponible}, requerido {c}",
        )
    producto.cantidad_disponible = disponible - c


def _rango_fechas(stmt, modelo, fecha_inicio, fecha_fin):
    if fecha_inicio:
        stmt = stmt.where(modelo.fecha >= fecha_inicio)
    if fecha_fin:
        stmt = stmt.where(modelo.fecha <= fecha_fin)
    return stmt


def filtrar_mediciones(db: Session, *, parametro_id=None, fuera_rango=None,
                       fecha_inicio=None, fecha_fin=None):
    stmt = select(models.Medicion)
    if parametro_id:
        stmt = stmt.where(models.Medicion.parametro_id == parametro_id)
    if fuera_rango is not None:
        stmt = stmt.where(models.Medicion.fuera_rango.is_(fuera_rango))
    stmt = _rango_fechas(stmt, models.Medicion, fecha_inicio, fecha_fin)
    return db.execute(stmt.order_by(models.Medicion.fecha.desc(), models.Medicion.hora.desc())).scalars().all()


def filtrar_actividades(db: Session, *, tipo=None, fecha_inicio=None, fecha_fin=None):
    stmt = select(models.ActividadPlanta)
    if tipo:
        stmt = stmt.where(models.ActividadPlanta.tipo == tipo)
    stmt = _rango_fechas(stmt, models.ActividadPlanta, fecha_inicio, fecha_fin)
    return db.execute(stmt.order_by(models.ActividadPlanta.fecha.desc(), models.ActividadPlanta.hora.desc())).scalars().all()


def filtrar_dosificaciones(db: Session, *, producto_id=None, fecha_inicio=None, fecha_fin=None):
    stmt = select(models.Dosificacion)
    if producto_id:
        stmt = stmt.where(models.Dosificacion.producto_id == producto_id)
    stmt = _rango_fechas(stmt, models.Dosificacion, fecha_inicio, fecha_fin)
    return db.execute(stmt.order_by(models.Dosificacion.fecha.desc(), models.Dosificacion.hora.desc())).scalars().all()


def filtrar_horas(db: Session, *, fecha_inicio=None, fecha_fin=None):
    stmt = select(models.HoraServicio)
    stmt = _rango_fechas(stmt, models.HoraServicio, fecha_inicio, fecha_fin)
    return db.execute(stmt.order_by(models.HoraServicio.fecha.desc())).scalars().all()

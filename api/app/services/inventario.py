"""Lógica de inventario: entradas/salidas y alertas (RF-10..RF-18)."""
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..schemas import TipoMovimiento


def aplicar_movimiento(
    db: Session,
    elemento: models.ElementoInventario,
    tipo: TipoMovimiento,
    cantidad: float,
    responsable_id: int | None,
    motivo: str | None,
    observaciones: str | None,
    fecha,
    hora=None,
):
    """Actualiza la cantidad del elemento y registra el movimiento."""
    c = Decimal(str(cantidad))
    actual = Decimal(str(elemento.cantidad or 0))
    if tipo == TipoMovimiento.entrada:
        elemento.cantidad = actual + c
    else:
        if actual < c:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La salida es mayor a las existencias disponibles",
            )
        elemento.cantidad = actual - c

    movimiento = models.MovimientoInventario(
        elemento_id=elemento.id,
        tipo=tipo,
        cantidad=cantidad,
        responsable_id=responsable_id,
        motivo=motivo,
        observaciones=observaciones,
        fecha=fecha,
        hora=hora,
    )
    db.add(movimiento)
    return movimiento


def alertas(db: Session):
    """Elementos (incluidos insumos/químicos) por debajo de su mínimo (RF-18).

    Los químicos ahora son ``elementos_inventario`` cuya categoría es de tipo
    ``insumo``; por eso se evalúan junto con el resto del inventario usando
    ``minimo`` (punto 2).
    """
    cats = {c.id: c.nombre for c in db.execute(select(models.CategoriaInventario)).scalars().all()}
    stmt = select(models.ElementoInventario).where(
        models.ElementoInventario.estado == models.EstadoRegistro.activo,
        models.ElementoInventario.minimo.isnot(None),
        models.ElementoInventario.cantidad <= models.ElementoInventario.minimo,
    )
    resultado = []
    for e in db.execute(stmt).scalars().all():
        resultado.append({
            "tipo": "Elemento",
            "id": e.id,
            "nombre": e.nombre,
            "categoria": cats.get(e.categoria_id, "—"),
            "cantidad": e.cantidad,
            "minimo": e.minimo,
            "unidad": e.unidad,
        })
    return resultado

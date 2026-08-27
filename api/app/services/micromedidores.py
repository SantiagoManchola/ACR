"""Lógica de micromedidores: cálculo de consumo y promedio histórico.

Regla de negocio 1 y 2: lectura mensual; si no hay lectura previa válida se
usa el promedio histórico (promedio_usado=True, consumo=promedio o NULL).
"""
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

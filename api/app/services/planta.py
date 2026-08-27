"""Lógica de planta: detección de valores fuera de rango (RF-48/RF-49)."""
from decimal import Decimal

from .. import models


def fuera_de_rango(parametro: models.ParametroPlanta, valor: Decimal) -> bool:
    """Compara el valor con valor_min/valor_max configurables (regla 9)."""
    v = Decimal(str(valor))
    if parametro.valor_min is not None and v < Decimal(str(parametro.valor_min)):
        return True
    if parametro.valor_max is not None and v > Decimal(str(parametro.valor_max)):
        return True
    return False

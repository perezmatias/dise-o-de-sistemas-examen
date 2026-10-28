"""Comprobación numérica compartida sin dependencias entre categorías de patrones."""

from math import isfinite


def es_finito(valor: float) -> bool:
    """Indica si un número puede representarse como float finito.

    Args:
        valor: Número previamente comprobado como int o float.

    Returns:
        bool: False para NaN, infinitos o enteros que desbordan la conversión.
    """
    try:
        return isfinite(valor)
    except OverflowError:
        return False

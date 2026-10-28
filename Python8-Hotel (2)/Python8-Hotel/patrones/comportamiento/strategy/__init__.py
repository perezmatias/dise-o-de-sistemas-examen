"""Subpaquete: Patrón Strategy (Comportamiento)."""
from patrones.comportamiento.strategy.estrategia_tarifa import (
    EstrategiaTarifa, TarifaTemporadaAlta, TarifaTemporadaBaja, TarifaCorporativa,
)
from patrones.comportamiento.strategy.cotizador import Cotizador
__all__ = [
    "EstrategiaTarifa", "TarifaTemporadaAlta", "TarifaTemporadaBaja",
    "TarifaCorporativa", "Cotizador",
]

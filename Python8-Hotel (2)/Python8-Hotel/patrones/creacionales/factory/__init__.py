"""Subpaquete: Patrón Factory Method (Creacional)."""
from patrones.creacionales.factory.habitacion import Habitacion, HabitacionEstandar, Suite
from patrones.creacionales.factory.creador_habitacion import (
    CreadorHabitacion,
    CreadorHabitacionEstandar,
    CreadorSuite,
)
__all__ = [
    "Habitacion",
    "HabitacionEstandar",
    "Suite",
    "CreadorHabitacion",
    "CreadorHabitacionEstandar",
    "CreadorSuite",
]

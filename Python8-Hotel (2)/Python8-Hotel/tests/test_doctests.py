"""Ejecuta los ejemplos >>> de los docstrings de todos los módulos de patrones.

Los docstrings son material didáctico: si un ejemplo deja de coincidir con el
código (por ejemplo, tras cambiar un formato de salida), este test falla.
"""

import doctest
import glob
import importlib
import os
import unittest

from patrones.creacionales.singleton import CentralReservas

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _modulos_de_patrones() -> list:
    """Devuelve los nombres importables de todos los módulos de patrones/."""
    rutas = glob.glob(os.path.join(RAIZ, "patrones", "**", "*.py"), recursive=True)
    nombres = []
    for ruta in sorted(rutas):
        relativa = os.path.relpath(ruta, RAIZ)[:-3].replace(os.sep, ".")
        nombres.append(relativa[: -len(".__init__")] if relativa.endswith("__init__") else relativa)
    return nombres


def _resetear_singleton(_test: doctest.DocTest) -> None:
    """Deja el Singleton sin instancia para que los ejemplos sean reproducibles."""
    CentralReservas._instance = None


def load_tests(loader: unittest.TestLoader, tests: unittest.TestSuite,
               pattern: str) -> unittest.TestSuite:
    """Agrega un caso de unittest por cada módulo que tenga ejemplos >>>.

    Args:
        loader: Cargador de unittest (no se usa).
        tests: Suite recibida de unittest.
        pattern: Patrón de descubrimiento (no se usa).

    Returns:
        unittest.TestSuite: La suite con los doctests agregados.
    """
    for nombre in _modulos_de_patrones():
        modulo = importlib.import_module(nombre)
        try:
            tests.addTests(doctest.DocTestSuite(modulo, setUp=_resetear_singleton))
        except ValueError:
            pass  # Python < 3.5 lanza ValueError si el módulo no tiene doctests
    return tests


class TestHayDoctests(unittest.TestCase):
    """Verifica que el descubrimiento de módulos funcione."""

    def test_se_encuentran_los_modulos_de_los_ocho_patrones(self) -> None:
        nombres = _modulos_de_patrones()
        for patron in ("singleton", "factory", "builder", "decorator",
                       "adapter", "observer", "strategy", "chain"):
            self.assertTrue(any("." + patron in nombre for nombre in nombres), patron)


if __name__ == "__main__":
    unittest.main()

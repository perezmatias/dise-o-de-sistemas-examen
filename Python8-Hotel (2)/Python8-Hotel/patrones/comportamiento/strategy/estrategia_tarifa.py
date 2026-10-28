"""
Patrón Strategy - Estrategias de tarifa.

El patrón Strategy permite definir una familia de algoritmos (en este caso,
formas de calcular la tarifa final de una estadía), encapsular cada uno en una
clase y hacerlos intercambiables en tiempo de ejecución.

Este módulo define:
    - EstrategiaTarifa: Interfaz abstracta que toda política de tarifa debe cumplir.
    - TarifaTemporadaAlta: Recargo del 30% sobre el monto base.
    - TarifaTemporadaBaja: Descuento del 20% sobre el monto base.
    - TarifaCorporativa: Descuento del 10% para empresas con convenio.

Analogía:
    Es como la lista de precios de la recepción: la misma habitación cuesta
    distinto en vacaciones de invierno, en temporada baja o si el huésped viene
    por convenio de una empresa. La recepción no cambia su forma de trabajar:
    solo cambia la lista de precios que consulta.

Ventajas del patrón Strategy:
    1. Se pueden agregar nuevas políticas de tarifa sin modificar el cotizador.
    2. El cotizador no sabe NI necesita saber cómo se calcula cada tarifa.
    3. La política de tarifa se puede cambiar dinámicamente antes de confirmar.

Ejemplo de uso:
    >>> estrategia = TarifaTemporadaAlta()
    >>> estrategia.aplicar(100.0)
    [Temporada Alta] Recargo del 30% sobre $100.00: total $130.00
    130.0
"""

from abc import ABC, abstractmethod
from typing import Any

from patrones._numeros import es_finito


def _validar_monto_tarifa(monto: Any) -> None:
    """Comprueba el contrato numérico de las entradas y resultados de tarifa.

    Args:
        monto: Importe que se desea comprobar.

    Raises:
        TypeError: Si el importe no es int o float, o es bool.
        ValueError: Si es negativo, no finito o no representable como float.
    """
    if not isinstance(monto, (int, float)) or isinstance(monto, bool):
        raise TypeError("El monto de tarifa debe ser un número")
    if not es_finito(monto) or monto < 0:
        raise ValueError("El monto de tarifa debe ser finito y no negativo")


class EstrategiaTarifa(ABC):
    """Interfaz abstracta para las estrategias de tarifa.

    Toda nueva política de tarifa debe heredar de esta clase e implementar
    el método aplicar(). Esto garantiza que el Cotizador pueda usar
    cualquier estrategia sin conocer su implementación interna.
    """

    @abstractmethod
    def aplicar(self, monto: float) -> float:
        """Aplica la política de tarifa al monto indicado.

        Imprime el detalle del cálculo y devuelve el monto final.

        Args:
            monto (float): Monto base de la cotización.

        Returns:
            float: Monto final redondeado a 2 decimales.

        Raises:
            TypeError: Si el monto de entrada no es int o float, o es bool.
            ValueError: Si la entrada o el resultado es negativo o no finito.
        """
        pass


class TarifaTemporadaAlta(EstrategiaTarifa):
    """Estrategia de temporada alta: recargo del 30% sobre el monto base.

    Se usa round() para redondear a dos decimales; esto no convierte float
    en aritmética decimal exacta.

    Atributos:
        RECARGO (float): Fracción de recargo aplicada (0.30).
    """

    RECARGO = 0.30

    def aplicar(self, monto: float) -> float:
        """Aplica el recargo de temporada alta.

        Args:
            monto (float): Monto base antes del recargo.

        Returns:
            float: Monto con el recargo, redondeado a 2 decimales.

        Raises:
            TypeError: Si el monto no es int o float, o es bool.
            ValueError: Si el monto o el resultado es negativo o no finito.
        """
        _validar_monto_tarifa(monto)
        final = round(monto * (1 + self.RECARGO), 2)
        _validar_monto_tarifa(final)
        print(f"[Temporada Alta] Recargo del {self.RECARGO:.0%} sobre ${monto:.2f}: "
              f"total ${final:.2f}")
        return final


class TarifaTemporadaBaja(EstrategiaTarifa):
    """Estrategia de temporada baja: descuento del 20% sobre el monto base.

    Atributos:
        DESCUENTO (float): Fracción de descuento aplicada (0.20).
    """

    DESCUENTO = 0.20

    def aplicar(self, monto: float) -> float:
        """Aplica el descuento de temporada baja.

        Args:
            monto (float): Monto base antes del descuento.

        Returns:
            float: Monto con el descuento, redondeado a 2 decimales.

        Raises:
            TypeError: Si el monto no es int o float, o es bool.
            ValueError: Si el monto o el resultado es negativo o no finito.
        """
        _validar_monto_tarifa(monto)
        final = round(monto * (1 - self.DESCUENTO), 2)
        _validar_monto_tarifa(final)
        print(f"[Temporada Baja] Descuento del {self.DESCUENTO:.0%} sobre ${monto:.2f}: "
              f"total ${final:.2f}")
        return final


class TarifaCorporativa(EstrategiaTarifa):
    """Estrategia corporativa: descuento del 10% para empresas con convenio.

    Atributos:
        DESCUENTO (float): Fracción de descuento aplicada (0.10).
        _empresa (str): Nombre de la empresa con convenio.
    """

    DESCUENTO = 0.10

    def __init__(self, empresa: str) -> None:
        """Inicializa la estrategia con la empresa del convenio.

        Args:
            empresa (str): Nombre de la empresa (ej: "Acme S.A.").
        """
        self._empresa = empresa

    def aplicar(self, monto: float) -> float:
        """Aplica el descuento corporativo.

        Args:
            monto (float): Monto base antes del descuento.

        Returns:
            float: Monto con el descuento, redondeado a 2 decimales.

        Raises:
            TypeError: Si el monto no es int o float, o es bool.
            ValueError: Si el monto o el resultado es negativo o no finito.
        """
        _validar_monto_tarifa(monto)
        final = round(monto * (1 - self.DESCUENTO), 2)
        _validar_monto_tarifa(final)
        print(f"[Corporativa - {self._empresa}] Descuento del {self.DESCUENTO:.0%} "
              f"sobre ${monto:.2f}: total ${final:.2f}")
        return final

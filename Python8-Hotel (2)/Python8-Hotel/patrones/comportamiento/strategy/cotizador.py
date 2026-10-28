"""
Patrón Strategy - Contexto (Cotizador de estadías).

En el patrón Strategy, el "contexto" es la clase que UTILIZA las estrategias
sin conocer su implementación interna. En este caso, Cotizador delega el
cálculo de la tarifa final a cualquier objeto que implemente EstrategiaTarifa.

Relación con el patrón:
    - Cotizador = Contexto (usa la estrategia).
    - EstrategiaTarifa = Interfaz de estrategia (contrato).
    - TarifaTemporadaAlta/TarifaTemporadaBaja/TarifaCorporativa = Estrategias concretas.

Flujo de uso:
    1. Crear un cotizador: cotizador = Cotizador()
    2. Agregar habitaciones: cotizador.agregar_habitacion(habitacion)
    3. Elegir la tarifa: cotizador.set_estrategia_tarifa(TarifaTemporadaBaja())
    4. Confirmar la cotización: cotizador.confirmar()
    5. Tras confirmar, el cotizador se vacía automáticamente.

Las habitaciones deben exponer nombre, tarifa y mostrar_info(); el cotizador no
depende de ninguna clase concreta de habitación.

Ejemplo de uso:
    >>> from types import SimpleNamespace
    >>> from patrones.comportamiento.strategy.estrategia_tarifa import TarifaTemporadaBaja
    >>> habitacion = SimpleNamespace(nombre="Doble 101", tarifa=80.0,
    ...                              mostrar_info=lambda: print("Doble 101 | $80.00"))
    >>> cotizador = Cotizador()
    >>> cotizador.agregar_habitacion(habitacion)
    Habitación agregada a la cotización: Doble 101
    >>> cotizador.set_estrategia_tarifa(TarifaTemporadaBaja())
    >>> cotizador.confirmar()
    <BLANKLINE>
    === COTIZACIÓN ===
    Habitaciones cotizadas:
    Doble 101 | $80.00
    Subtotal: $80.00
    [Temporada Baja] Descuento del 20% sobre $80.00: total $64.00
    ¡Cotización confirmada!
    <BLANKLINE>
"""

from typing import Any, List, Optional

from patrones._numeros import es_finito
from patrones.comportamiento.strategy.estrategia_tarifa import EstrategiaTarifa
from patrones.comportamiento.strategy.estrategia_tarifa import _validar_monto_tarifa


class Cotizador:
    """Cotizador de estadías que utiliza el patrón Strategy para la tarifa.

    El cotizador acumula habitaciones y, al momento de confirmar, delega
    el cálculo de la tarifa final a la estrategia configurada.

    Atributos:
        _habitaciones (list): Lista de habitaciones agregadas a la cotización.
        _estrategia_tarifa (EstrategiaTarifa | None): Política de tarifa seleccionada.
    """

    def __init__(self) -> None:
        """Inicializa un cotizador vacío sin estrategia de tarifa seleccionada."""
        self._habitaciones: List[Any] = []
        self._estrategia_tarifa: Optional[EstrategiaTarifa] = None

    @property
    def habitaciones(self) -> List[Any]:
        """Copia de la lista de habitaciones cotizadas (solo lectura)."""
        return list(self._habitaciones)

    @property
    def estrategia_tarifa(self) -> Optional[EstrategiaTarifa]:
        """Estrategia de tarifa seleccionada, o None si no hay (solo lectura)."""
        return self._estrategia_tarifa

    @staticmethod
    def _validar_tarifa(tarifa: Any) -> None:
        """Comprueba que una tarifa sea un número finito y no negativo.

        Args:
            tarifa: Valor de tarifa a comprobar.

        Raises:
            TypeError: Si la tarifa no es int o float, o es un bool.
            ValueError: Si la tarifa es negativa, no finita o excede el rango de float.
        """
        if not isinstance(tarifa, (int, float)) or isinstance(tarifa, bool):
            raise TypeError("La tarifa debe ser un número")
        if not es_finito(tarifa) or tarifa < 0:
            raise ValueError("La tarifa debe ser finita y no negativa")

    def agregar_habitacion(self, habitacion: Any) -> None:
        """Agrega una habitación a la cotización.

        Args:
            habitacion: Objeto con nombre, tarifa y método mostrar_info().
                La tarifa debe ser int o float finito, no negativo y distinto de bool.

        Raises:
            TypeError: Si falta el contrato de la habitación o el tipo de tarifa es inválido.
            ValueError: Si la tarifa es negativa, no finita o no representable como float.

        La validación ocurre antes de modificar la cotización.
        """
        if not callable(getattr(habitacion, "mostrar_info", None)):
            raise TypeError("La habitación debe implementar mostrar_info()")
        try:
            nombre = habitacion.nombre
            tarifa = habitacion.tarifa
        except AttributeError as error:
            raise TypeError("La habitación debe exponer nombre y tarifa") from error
        self._validar_tarifa(tarifa)
        mensaje = f"Habitación agregada a la cotización: {nombre}"
        self._habitaciones.append(habitacion)
        print(mensaje)

    def set_estrategia_tarifa(self, estrategia_tarifa: EstrategiaTarifa) -> None:
        """Establece o cambia la política de tarifa del cotizador.

        Este es el método clave del patrón Strategy: permite cambiar
        el comportamiento de la tarifa en tiempo de ejecución sin modificar
        la clase Cotizador.

        Args:
            estrategia_tarifa (EstrategiaTarifa): La estrategia de tarifa a usar.

        Raises:
            TypeError: Si el objeto no es una instancia de EstrategiaTarifa.
        """
        if not isinstance(estrategia_tarifa, EstrategiaTarifa):
            raise TypeError(
                f"La estrategia debe ser una instancia de EstrategiaTarifa, "
                f"se recibió {type(estrategia_tarifa).__name__}"
            )
        self._estrategia_tarifa = estrategia_tarifa

    def calcular_total(self) -> float:
        """Calcula la suma de las tarifas de todas las habitaciones.

        Returns:
            float: Total redondeado a 2 decimales; float no representa todos
                los valores decimales exactamente.

        Raises:
            TypeError: Si una habitación externa cambió su tarifa a un tipo inválido.
            ValueError: Si una tarifa o el total es negativo, no finito o fuera de rango.
        """
        total = 0.0
        for habitacion in self._habitaciones:
            tarifa = habitacion.tarifa
            self._validar_tarifa(tarifa)
            total += tarifa
        if not es_finito(total):
            raise ValueError("El total de la cotización excede el rango numérico")
        return round(total, 2)

    def confirmar(self) -> None:
        """Confirma la cotización: muestra resumen, calcula total y aplica la tarifa.

        Validaciones antes de proceder:
            1. La cotización no debe estar vacía.
            2. Debe haber una estrategia de tarifa seleccionada.
            3. Se revalidan tarifas y total antes de invocar la estrategia.

        Las habitaciones externas se conservan por referencia. Si cambian sus tarifas,
        calcular_total() las comprueba de nuevo. Los errores previos a la tarifa o de
        la propia estrategia se propagan conservando la cotización para un reintento.
        El resultado de la estrategia se valida antes de confirmar y vaciar el estado.

        Raises:
            TypeError: Si una tarifa o el resultado de la estrategia tiene tipo inválido.
            ValueError: Si una tarifa o el resultado es negativo, no finito o fuera de rango.

        Flujo exitoso:
            - Calcula el subtotal con calcular_total().
            - Muestra el resumen y todas las habitaciones con mostrar_info().
            - Delega el cálculo final a self._estrategia_tarifa.aplicar(subtotal).
            - Valida el resultado e imprime la confirmación de éxito.
            - Vacía la cotización y resetea la estrategia de tarifa.
        """
        if not self._habitaciones:
            print("La cotización está vacía")
            return

        if self._estrategia_tarifa is None:
            print("Debe seleccionar una estrategia de tarifa")
            return

        subtotal = self.calcular_total()
        print("\n=== COTIZACIÓN ===")
        print("Habitaciones cotizadas:")
        for habitacion in self._habitaciones:
            habitacion.mostrar_info()
        print(f"Subtotal: ${subtotal:.2f}")
        final = self._estrategia_tarifa.aplicar(subtotal)
        _validar_monto_tarifa(final)
        print("¡Cotización confirmada!\n")
        self._habitaciones = []
        self._estrategia_tarifa = None

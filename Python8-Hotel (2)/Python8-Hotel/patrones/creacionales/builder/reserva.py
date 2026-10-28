"""
Módulo que define la clase Reserva para el patrón Builder.

El patrón Builder separa la construcción de un objeto complejo de su representación,
de modo que el mismo proceso de construcción pueda crear diferentes representaciones.

La clase Reserva es el **producto final** que el Builder construye paso a paso.
Una reserva puede contener múltiples habitaciones, una cantidad de noches, el nombre
del huésped, un tipo de servicio y un seguro de cancelación. Todos estos atributos se
asignan progresivamente a través del builder.

Clases:
    Reserva: Objeto complejo resultante del proceso de construcción.

Uso:
    >>> from types import SimpleNamespace
    >>> reserva = Reserva()
    >>> reserva.agregar_habitacion(SimpleNamespace(nombre="Doble 101", tarifa=80.0))
    >>> reserva.set_noches(2)
    >>> reserva.set_huesped("Ana Pérez")
    >>> reserva.set_tipo_servicio("Estándar", 10.0)
    >>> reserva.calcular_subtotal()
    160.0
    >>> reserva.mostrar_resumen()
    === RESUMEN DE LA RESERVA ===
    Huésped: Ana Pérez
    Noches: 2
    Habitaciones:
      - Doble 101 | $80.00/noche
    Servicio: Estándar ($10.00)
    Seguro de cancelación: No
    Subtotal: $160.00
    TOTAL: $170.00
    =============================
"""

from typing import Any, List

from patrones._numeros import es_finito


class Reserva:
    """Representa una reserva compleja construida paso a paso mediante el patrón Builder.

    Una reserva agrupa habitaciones, noches, huésped, tipo de servicio y seguro de
    cancelación. Habitualmente se obtiene mediante un ReservaBuilder concreto;
    también puede instanciarse directamente como reserva vacía.

    Attributes:
        _habitaciones (list): Lista de habitaciones (con propiedades nombre y tarifa).
        _noches (int): Cantidad de noches de estadía (al menos 1).
        _huesped (str): Nombre del huésped titular.
        _tipo_servicio (str): Modalidad de servicio ("Estándar" o "Premium").
        _costo_servicio (float): Costo del servicio según la modalidad.
        _seguro_cancelacion (bool): Indica si incluye seguro de cancelación.
    """

    # Porcentaje del seguro de cancelación sobre el subtotal de habitaciones
    PORCENTAJE_SEGURO = 0.03   # 3% del subtotal

    def __init__(self) -> None:
        """Inicializa una Reserva vacía con todos los atributos en estado neutro."""
        self._habitaciones: List[Any] = []
        self._noches: int = 1
        self._huesped: str = ""
        self._tipo_servicio: str = ""
        self._costo_servicio: float = 0.0
        self._seguro_cancelacion: bool = False

    @staticmethod
    def _validar_tarifa(tarifa: Any) -> None:
        """Valida que una tarifa sea un int o float finito y no negativo.

        Args:
            tarifa: Valor a validar.

        Raises:
            TypeError: Si la tarifa no es int o float, o es bool.
            ValueError: Si la tarifa es negativa, no finita o no representable como float.
        """
        if not isinstance(tarifa, (int, float)) or isinstance(tarifa, bool):
            raise TypeError("La tarifa debe ser un número")
        if not es_finito(tarifa) or tarifa < 0:
            raise ValueError("La tarifa debe ser finita y no negativa")

    def agregar_habitacion(self, habitacion: Any) -> None:
        """Agrega una habitación a la reserva.

        La validación ocurre antes de modificar la reserva: si falla, el estado
        previo queda intacto.

        Args:
            habitacion: Objeto con propiedades `nombre` y `tarifa` (duck typing).
                La tarifa debe ser int o float finito, no negativo y distinto de bool.

        Raises:
            TypeError: Si faltan atributos o el tipo de la tarifa es inválido.
            ValueError: Si la tarifa es negativa, no finita o no representable como float.
        """
        try:
            habitacion.nombre
            tarifa = habitacion.tarifa
        except AttributeError as error:
            raise TypeError("La habitación debe exponer nombre y tarifa") from error
        self._validar_tarifa(tarifa)
        self._habitaciones.append(habitacion)

    def set_noches(self, noches: int) -> None:
        """Establece la cantidad de noches de la estadía.

        Args:
            noches (int): Cantidad de noches, entero mayor o igual que 1 (bool no vale).

        Raises:
            TypeError: Si noches no es un int, o es bool.
            ValueError: Si noches es menor que 1.
        """
        if not isinstance(noches, int) or isinstance(noches, bool):
            raise TypeError("Las noches deben ser un número entero")
        if noches < 1:
            raise ValueError("Las noches deben ser al menos 1")
        self._noches = noches

    def set_huesped(self, nombre: str) -> None:
        """Establece el nombre del huésped titular.

        Args:
            nombre (str): Nombre completo del huésped.

        Raises:
            TypeError: Si nombre no es un texto.
        """
        if not isinstance(nombre, str):
            raise TypeError("El huésped debe ser un texto")
        self._huesped = nombre

    def set_tipo_servicio(self, tipo: str, costo: float) -> None:
        """Establece el tipo de servicio y su costo.

        Args:
            tipo (str): Etiqueta del servicio (por ejemplo "Estándar").
            costo (float): Costo del servicio, número finito no negativo.

        Raises:
            TypeError: Si el costo no es int o float, o es bool.
            ValueError: Si el costo es negativo, no finito o no representable como float.
        """
        if not isinstance(costo, (int, float)) or isinstance(costo, bool):
            raise TypeError("El costo del servicio debe ser un número")
        if not es_finito(costo) or costo < 0:
            raise ValueError("El costo del servicio debe ser finito y no negativo")
        self._tipo_servicio = tipo
        self._costo_servicio = costo

    def set_seguro_cancelacion(self, activo: bool) -> None:
        """Activa o desactiva el seguro de cancelación.

        Args:
            activo (bool): True para incluir el seguro (3% del subtotal).
        """
        self._seguro_cancelacion = bool(activo)

    @property
    def habitaciones(self) -> List[Any]:
        """Copia de la lista de habitaciones de la reserva."""
        return list(self._habitaciones)

    @property
    def noches(self) -> int:
        """Cantidad de noches de la estadía."""
        return self._noches

    @property
    def huesped(self) -> str:
        """Nombre del huésped titular."""
        return self._huesped

    @property
    def tipo_servicio(self) -> str:
        """Etiqueta del tipo de servicio."""
        return self._tipo_servicio

    @property
    def costo_servicio(self) -> float:
        """Costo del tipo de servicio."""
        return self._costo_servicio

    @property
    def seguro_cancelacion(self) -> bool:
        """Indica si la reserva incluye seguro de cancelación."""
        return self._seguro_cancelacion

    def calcular_subtotal(self) -> float:
        """Calcula el subtotal: suma de tarifas de las habitaciones por las noches.

        Revalida cada tarifa, porque las habitaciones externas se guardan por
        referencia y podrían haber cambiado después del alta.

        Returns:
            float: Subtotal redondeado a 2 decimales.

        Raises:
            TypeError: Si una tarifa externa ya no es int o float, o es bool.
            ValueError: Si una tarifa es negativa o no finita, o el subtotal desborda.
        """
        subtotal = 0.0
        for habitacion in self._habitaciones:
            tarifa = habitacion.tarifa
            self._validar_tarifa(tarifa)
            try:
                parcial = tarifa * self._noches
            except OverflowError as error:  # float * int gigante no cabe en un float
                raise ValueError("El subtotal de la reserva excede el rango numérico") from error
            if not es_finito(parcial):
                raise ValueError("El subtotal de la reserva excede el rango numérico")
            subtotal += parcial
        if not es_finito(subtotal):
            raise ValueError("El subtotal de la reserva excede el rango numérico")
        return round(subtotal, 2)

    def calcular_total(self) -> float:
        """Calcula el total: subtotal más servicio y, si corresponde, el seguro.

        Returns:
            float: Total de la reserva redondeado a 2 decimales.

        Raises:
            TypeError: Si una tarifa externa ya no es int o float, o es bool.
            ValueError: Si una tarifa o el total es negativo, no finito o fuera de rango.
        """
        subtotal = self.calcular_subtotal()
        total = subtotal + self._costo_servicio
        if self._seguro_cancelacion:
            total += round(subtotal * self.PORCENTAJE_SEGURO, 2)
        if not es_finito(total):
            raise ValueError("El total de la reserva excede el rango numérico")
        return round(total, 2)

    def mostrar_resumen(self) -> None:
        """Imprime el resumen completo de la reserva con todos sus detalles."""
        subtotal = self.calcular_subtotal()
        print("=== RESUMEN DE LA RESERVA ===")
        print(f"Huésped: {self._huesped}")
        print(f"Noches: {self._noches}")

        print("Habitaciones:")
        for habitacion in self._habitaciones:
            print(f"  - {habitacion.nombre} | ${habitacion.tarifa:.2f}/noche")

        print(f"Servicio: {self._tipo_servicio} (${self._costo_servicio:.2f})")

        if self._seguro_cancelacion:
            costo_seguro = round(subtotal * self.PORCENTAJE_SEGURO, 2)
            print(f"Seguro de cancelación: Sí (+${costo_seguro:.2f})")
        else:
            print("Seguro de cancelación: No")

        print(f"Subtotal: ${subtotal:.2f}")
        print(f"TOTAL: ${self.calcular_total():.2f}")
        print("=============================")

    def __repr__(self) -> str:
        """Representación técnica útil para depuración."""
        nombres = [h.nombre for h in self._habitaciones]
        return (
            f"Reserva(huesped={self._huesped!r}, habitaciones={nombres!r}, "
            f"noches={self._noches}, servicio={self._tipo_servicio!r}, "
            f"total={self.calcular_total():.2f})"
        )

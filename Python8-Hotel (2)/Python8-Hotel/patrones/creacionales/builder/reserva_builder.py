"""
Módulo que implementa el patrón Builder para la construcción de reservas.

El patrón Builder permite construir objetos complejos paso a paso. A diferencia
de un constructor con muchos parámetros, el builder expone métodos individuales
para cada parte del objeto, y devuelve el resultado final en build().

Analogía: es como armar un paquete de estadía en una agencia de viajes — el
huésped elige exactamente qué habitaciones, cuántas noches y qué extras quiere;
el agente (builder) ensambla la reserva sin que el huésped sepa cómo.

Clases:
    ReservaBuilder: Interfaz abstracta del builder.
    ReservaEstandarBuilder: Construye reservas con servicio Estándar ($10.00).
    ReservaPremiumBuilder: Construye reservas con servicio Premium ($40.00).
    DirectorReserva: Orquesta el builder para crear reservas predefinidas.

Uso:
    >>> from patrones.creacionales.factory import CreadorSuite
    >>> suite = CreadorSuite("Vista al mar").crear_habitacion("Suite 501", 200.0)
    >>> director = DirectorReserva(ReservaEstandarBuilder())
    >>> reserva = director.construir_reserva_basica(suite, 2, "Ana Pérez")
      Habitación agregada: Suite 501 ($200.00/noche)
    >>> reserva.calcular_total()
    410.0
    >>> director.set_builder(ReservaPremiumBuilder())
    >>> completa = director.construir_reserva_completa([suite], 1, "Luis Gómez")
      Habitación agregada: Suite 501 ($200.00/noche)
    >>> completa.calcular_total()
    246.0
"""

from abc import ABC, abstractmethod
from typing import Any, List

from patrones.creacionales.builder.reserva import Reserva


class ReservaBuilder(ABC):
    """Interfaz abstracta que define los pasos para construir una Reserva.

    Los cinco pasos de configuración devuelven el propio builder (interfaz
    fluida). build() devuelve la Reserva terminada y reset() retorna None.
    El orden de configuración es flexible; la clase DirectorReserva define
    secuencias predefinidas de construcción.

    Las subclases concretas implementan los detalles de cada tipo de servicio
    (costos y etiquetas).
    """

    @abstractmethod
    def reset(self) -> None:
        """Descarta la construcción actual sin modificar reservas ya entregadas."""
        pass

    @abstractmethod
    def agregar_habitacion(self, habitacion: Any) -> "ReservaBuilder":
        """Agrega una habitación a la reserva.

        Args:
            habitacion: Objeto con propiedades `nombre` y `tarifa` (duck typing).

        Returns:
            ReservaBuilder: El propio builder, para encadenar llamadas.
        """
        pass

    @abstractmethod
    def set_noches(self, noches: int) -> "ReservaBuilder":
        """Establece la cantidad de noches de la estadía.

        Args:
            noches (int): Cantidad de noches (entero mayor o igual que 1).

        Returns:
            ReservaBuilder: El propio builder, para encadenar llamadas.
        """
        pass

    @abstractmethod
    def set_huesped(self, nombre: str) -> "ReservaBuilder":
        """Establece el nombre del huésped titular.

        Args:
            nombre (str): Nombre completo del huésped.

        Returns:
            ReservaBuilder: El propio builder, para encadenar llamadas.
        """
        pass

    @abstractmethod
    def set_tipo_servicio(self, tipo: str) -> "ReservaBuilder":
        """Configura la etiqueta del tipo de servicio.

        Args:
            tipo (str): Tipo de servicio ("Estándar" o "Premium").

        Returns:
            ReservaBuilder: El propio builder, para encadenar llamadas.
        """
        pass

    @abstractmethod
    def agregar_seguro_cancelacion(self) -> "ReservaBuilder":
        """Activa el seguro de cancelación (3% del subtotal de habitaciones).

        Returns:
            ReservaBuilder: El propio builder, para encadenar llamadas.
        """
        pass

    @abstractmethod
    def build(self) -> Reserva:
        """Finaliza la construcción y devuelve la Reserva configurada.

        Returns:
            Reserva: El objeto Reserva completamente configurado.
        """
        pass


class ReservaEstandarBuilder(ReservaBuilder):
    """Builder concreto para reservas con servicio estándar.

    Configura la reserva con servicio Estándar: costo $10.00.
    Es la opción más económica para estadías sin requerimientos especiales.

    Attributes:
        _reserva (Reserva): La instancia de la reserva en construcción.
    """

    COSTO_SERVICIO = 10.00
    TIPO_SERVICIO = "Estándar"

    def __init__(self) -> None:
        """Inicializa el builder creando una nueva Reserva vacía."""
        self._reserva = Reserva()

    def reset(self) -> None:
        """Inicia una reserva vacía y descarta cualquier construcción parcial."""
        self._reserva = Reserva()

    def agregar_habitacion(self, habitacion: Any) -> "ReservaBuilder":
        """Agrega una habitación a la reserva.

        Args:
            habitacion: Objeto con propiedades `nombre` y `tarifa`.
                La tarifa debe ser int o float finito, no negativo y distinto de bool.

        Returns:
            ReservaBuilder: El propio builder, para encadenar llamadas.

        Raises:
            TypeError: Si faltan atributos o el tipo de la tarifa es inválido.
            ValueError: Si la tarifa es negativa, no finita o no representable como float.

        La validación ocurre antes de modificar la reserva.
        """
        self._reserva.agregar_habitacion(habitacion)
        print(f"  Habitación agregada: {habitacion.nombre} (${habitacion.tarifa:.2f}/noche)")
        return self

    def set_noches(self, noches: int) -> "ReservaBuilder":
        """Establece la cantidad de noches de la estadía.

        Args:
            noches (int): Cantidad de noches (entero mayor o igual que 1).

        Returns:
            ReservaBuilder: El propio builder, para encadenar llamadas.

        Raises:
            TypeError: Si noches no es un int, o es bool.
            ValueError: Si noches es menor que 1.
        """
        self._reserva.set_noches(noches)
        return self

    def set_huesped(self, nombre: str) -> "ReservaBuilder":
        """Establece el nombre del huésped titular.

        Args:
            nombre (str): Nombre completo del huésped.

        Returns:
            ReservaBuilder: El propio builder, para encadenar llamadas.

        Raises:
            TypeError: Si nombre no es un texto.
        """
        self._reserva.set_huesped(nombre)
        return self

    def set_tipo_servicio(self, tipo: str) -> "ReservaBuilder":
        """Asigna la etiqueta del tipo de servicio y el costo estándar.

        Nota: build() vuelve a aplicar TIPO_SERVICIO y COSTO_SERVICIO (HU-011), por
        lo que la etiqueta asignada aquí se reemplaza al construir la reserva.

        Args:
            tipo (str): Etiqueta del tipo de servicio.

        Returns:
            ReservaBuilder: El propio builder, para encadenar llamadas.
        """
        self._reserva.set_tipo_servicio(tipo, self.COSTO_SERVICIO)
        return self

    def agregar_seguro_cancelacion(self) -> "ReservaBuilder":
        """Activa el seguro de cancelación (3% del subtotal).

        Returns:
            ReservaBuilder: El propio builder, para encadenar llamadas.
        """
        self._reserva.set_seguro_cancelacion(True)
        return self

    def build(self) -> Reserva:
        """Aplica TIPO_SERVICIO y COSTO_SERVICIO estándar y devuelve la reserva terminada.

        Returns:
            Reserva: La reserva con servicio estándar configurado.
        """
        self._reserva.set_tipo_servicio(self.TIPO_SERVICIO, self.COSTO_SERVICIO)
        reserva_terminada = self._reserva
        self._reserva = Reserva()   # reset para reutilización del builder
        return reserva_terminada


class ReservaPremiumBuilder(ReservaBuilder):
    """Builder concreto para reservas con servicio premium.

    Configura la reserva con servicio Premium: costo $40.00.
    Es la opción para huéspedes que priorizan atención y comodidad.

    Attributes:
        _reserva (Reserva): La instancia de la reserva en construcción.
    """

    COSTO_SERVICIO = 40.00
    TIPO_SERVICIO = "Premium"

    def __init__(self) -> None:
        """Inicializa el builder creando una nueva Reserva vacía."""
        self._reserva = Reserva()

    def reset(self) -> None:
        """Inicia una reserva vacía y descarta cualquier construcción parcial."""
        self._reserva = Reserva()

    def agregar_habitacion(self, habitacion: Any) -> "ReservaBuilder":
        """Agrega una habitación a la reserva.

        Args:
            habitacion: Objeto con propiedades `nombre` y `tarifa`.
                La tarifa debe ser int o float finito, no negativo y distinto de bool.

        Returns:
            ReservaBuilder: El propio builder, para encadenar llamadas.

        Raises:
            TypeError: Si faltan atributos o el tipo de la tarifa es inválido.
            ValueError: Si la tarifa es negativa, no finita o no representable como float.

        La validación ocurre antes de modificar la reserva.
        """
        self._reserva.agregar_habitacion(habitacion)
        print(f"  Habitación agregada: {habitacion.nombre} (${habitacion.tarifa:.2f}/noche)")
        return self

    def set_noches(self, noches: int) -> "ReservaBuilder":
        """Establece la cantidad de noches de la estadía.

        Args:
            noches (int): Cantidad de noches (entero mayor o igual que 1).

        Returns:
            ReservaBuilder: El propio builder, para encadenar llamadas.

        Raises:
            TypeError: Si noches no es un int, o es bool.
            ValueError: Si noches es menor que 1.
        """
        self._reserva.set_noches(noches)
        return self

    def set_huesped(self, nombre: str) -> "ReservaBuilder":
        """Establece el nombre del huésped titular.

        Args:
            nombre (str): Nombre completo del huésped.

        Returns:
            ReservaBuilder: El propio builder, para encadenar llamadas.

        Raises:
            TypeError: Si nombre no es un texto.
        """
        self._reserva.set_huesped(nombre)
        return self

    def set_tipo_servicio(self, tipo: str) -> "ReservaBuilder":
        """Asigna la etiqueta del tipo de servicio y el costo premium.

        Nota: build() vuelve a aplicar TIPO_SERVICIO y COSTO_SERVICIO (HU-012), por
        lo que la etiqueta asignada aquí se reemplaza al construir la reserva.

        Args:
            tipo (str): Etiqueta del tipo de servicio.

        Returns:
            ReservaBuilder: El propio builder, para encadenar llamadas.
        """
        self._reserva.set_tipo_servicio(tipo, self.COSTO_SERVICIO)
        return self

    def agregar_seguro_cancelacion(self) -> "ReservaBuilder":
        """Activa el seguro de cancelación (3% del subtotal).

        Returns:
            ReservaBuilder: El propio builder, para encadenar llamadas.
        """
        self._reserva.set_seguro_cancelacion(True)
        return self

    def build(self) -> Reserva:
        """Aplica TIPO_SERVICIO y COSTO_SERVICIO premium y devuelve la reserva terminada.

        Returns:
            Reserva: La reserva con servicio premium configurado.
        """
        self._reserva.set_tipo_servicio(self.TIPO_SERVICIO, self.COSTO_SERVICIO)
        reserva_terminada = self._reserva
        self._reserva = Reserva()   # reset para reutilización del builder
        return reserva_terminada


class DirectorReserva:
    """Director que orquesta el builder para crear reservas predefinidas.

    El Director conoce la secuencia de pasos necesaria para construir tipos
    comunes de reservas, evitando que el cliente tenga que invocar cada paso
    manualmente. El cliente solo elige qué builder usar.

    Attributes:
        _builder (ReservaBuilder): El builder concreto que se orquesta.
    """

    def __init__(self, builder: "ReservaBuilder") -> None:
        """Inicializa el director con un builder concreto.

        Args:
            builder (ReservaBuilder): Instancia del builder a utilizar.
        """
        self._builder = builder

    def set_builder(self, builder: "ReservaBuilder") -> None:
        """Reemplaza el builder en uso, permitiendo reutilizar el director.

        Args:
            builder (ReservaBuilder): Nuevo builder a utilizar.
        """
        self._builder = builder

    def construir_reserva_basica(self, habitacion: Any, noches: int, huesped: str) -> Reserva:
        """Construye una reserva básica, sin seguro de cancelación.

        Inicia una construcción limpia, descartando habitaciones y extras
        configurados previamente en el builder. Si un paso falla, descarta
        el producto parcial y propaga el error original.

        Args:
            habitacion: Habitación (con propiedades nombre y tarifa).
            noches (int): Cantidad de noches de la estadía.
            huesped (str): Nombre del huésped titular.

        Returns:
            Reserva: Reserva con una habitación, noches y huésped, sin seguro.
        """
        self._builder.reset()
        try:
            self._builder.agregar_habitacion(habitacion)
            self._builder.set_noches(noches)
            self._builder.set_huesped(huesped)
            return self._builder.build()
        finally:
            self._builder.reset()

    def construir_reserva_completa(self, habitaciones: List, noches: int, huesped: str) -> Reserva:
        """Construye una reserva completa con seguro de cancelación incluido.

        Inicia una construcción limpia. Si un paso falla, descarta el producto
        parcial y propaga el error original; las reservas entregadas se conservan.

        Args:
            habitaciones (list): Lista de habitaciones (con propiedades nombre y tarifa).
            noches (int): Cantidad de noches de la estadía.
            huesped (str): Nombre del huésped titular.

        Returns:
            Reserva: Reserva con todas las habitaciones y el seguro activado.
        """
        self._builder.reset()
        try:
            for habitacion in habitaciones:
                self._builder.agregar_habitacion(habitacion)
            self._builder.set_noches(noches)
            self._builder.set_huesped(huesped)
            self._builder.agregar_seguro_cancelacion()
            return self._builder.build()
        finally:
            self._builder.reset()

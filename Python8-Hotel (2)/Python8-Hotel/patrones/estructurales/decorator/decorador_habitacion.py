"""
Módulo que implementa el patrón Decorator para las habitaciones del hotel.

El patrón Decorator permite agregar responsabilidades adicionales a un objeto
dinámicamente, como alternativa flexible a la herencia. Los decoradores envuelven
al componente y extienden su comportamiento sin modificar su clase.

Analogía: es como armar una hamburguesa en un local de comidas. La hamburguesa base
tiene un precio; si agregas queso extra (+$2), el total sube, pero sigue siendo una
hamburguesa. Si además agregas panceta (+$3), el total suma sobre el precio anterior.
Cada "extra" es un decorador que envuelve el componente anterior.

Problema que resuelve sin Decorator:
    Si existieran 3 servicios opcionales (desayuno, seguro de viaje, late checkout),
    habría que crear 7 subclases para cubrir cada combinación posible. Con Decorator,
    basta con 3 clases y se pueden combinar arbitrariamente en tiempo de ejecución.

Clases:
    ComponenteHabitacion: Interfaz abstracta base (ABC).
    HabitacionBasica: Componente concreto — la habitación base a decorar.
    DecoradorHabitacion: Decorador base instanciable que envuelve un ComponenteHabitacion.
    DesayunoIncluido: Decorador concreto — agrega desayuno incluido (+$15.00).
    SeguroViaje: Decorador concreto — agrega seguro de viaje (+2%).
    LateCheckout: Decorador concreto — agrega salida tardía (+$25.00).

Uso:
    habitacion = HabitacionBasica("Suite Presidencial", 899.99)
    habitacion = DesayunoIncluido(habitacion)   # agrega el desayuno
    habitacion = SeguroViaje(habitacion)        # agrega seguro sobre el precio actual
    habitacion = LateCheckout(habitacion)       # agrega salida tardía

    print(habitacion.descripcion)
    # Suite Presidencial + Desayuno incluido + Seguro de viaje + Late checkout
    print(habitacion.precio)
    # 958.29

Ejemplo ejecutable:
    >>> habitacion = HabitacionBasica("Suite Presidencial", 899.99)
    >>> habitacion = LateCheckout(SeguroViaje(DesayunoIncluido(habitacion)))
    >>> habitacion.descripcion
    'Suite Presidencial + Desayuno incluido + Seguro de viaje + Late checkout'
    >>> habitacion.precio
    958.29
"""

from abc import ABC, abstractmethod
from patrones._numeros import es_finito


class ComponenteHabitacion(ABC):
    """Interfaz abstracta que define el contrato para habitaciones y decoradores.

    Tanto el componente base (HabitacionBasica) como todos los decoradores
    implementan esta interfaz, lo que permite que los decoradores sean
    intercambiables con el componente y entre sí.
    """

    @property
    @abstractmethod
    def descripcion(self) -> str:
        """Descripción acumulada de la habitación con sus servicios.

        Returns:
            Descripción de la habitación incluyendo todos los decoradores aplicados.
        """
        pass

    @property
    @abstractmethod
    def precio(self) -> float:
        """Precio total por noche de la habitación con todos sus decoradores.

        Returns:
            Precio acumulado con todos los servicios adicionales.
        """
        pass


class HabitacionBasica(ComponenteHabitacion):
    """Componente concreto base — la habitación sin servicios adicionales.

    Es el punto de partida de la cadena de decoradores. Almacena el nombre
    y precio base de la habitación que se desea decorar.

    Atributos:
        _nombre (str): Nombre de la habitación.
        _precio (float): Precio base por noche de la habitación.

    Ejemplo:
        >>> HabitacionBasica("Doble 101", 80.0)
        HabitacionBasica('Doble 101', 80.0)
    """

    def __init__(self, nombre: str, precio: float) -> None:
        """Inicializa la habitación con nombre y precio base.

        Args:
            nombre: Nombre descriptivo de la habitación.
            precio: Número finito no negativo (int o float, excluyendo bool).

        Raises:
            TypeError: Si el precio no es int o float, o es bool.
            ValueError: Si el precio es negativo, no finito o no representable como float.
        """
        if not isinstance(precio, (int, float)) or isinstance(precio, bool):
            raise TypeError("El precio debe ser un número")
        if not es_finito(precio):
            raise ValueError("El precio debe ser finito")
        if precio < 0:
            raise ValueError(f"El precio no puede ser negativo: {precio}")
        self._nombre = nombre
        self._precio = precio

    @property
    def descripcion(self) -> str:
        """Nombre base de la habitación, sin decoradores."""
        return self._nombre

    @property
    def precio(self) -> float:
        """Precio base de la habitación, sin cargos adicionales."""
        return self._precio

    def __repr__(self) -> str:
        """Representación técnica útil para depuración."""
        return f"HabitacionBasica({self._nombre!r}, {self._precio})"


class DecoradorHabitacion(ComponenteHabitacion):
    """Decorador base instanciable que envuelve un ComponenteHabitacion.

    Define la estructura base de todos los decoradores concretos. Mantiene
    una referencia al componente envuelto y delega las operaciones base a él,
    permitiendo que las subclases solo sobreescriban lo que modifican.

    Atributos:
        _componente (ComponenteHabitacion): El objeto que este decorador envuelve.
    """

    def __init__(self, componente: ComponenteHabitacion) -> None:
        """Inicializa el decorador envolviendo al componente dado.

        Args:
            componente: La habitación (o decorador) a envolver.
        """
        self._componente = componente

    @property
    def descripcion(self) -> str:
        """Delega la descripción al componente envuelto."""
        return self._componente.descripcion

    @property
    def precio(self) -> float:
        """Delega el precio al componente envuelto."""
        return self._componente.precio


class DesayunoIncluido(DecoradorHabitacion):
    """Decorador que agrega el desayuno incluido a la habitación.

    Agrega un cargo fijo de $15.00 al precio del componente envuelto e
    incluye la leyenda "+ Desayuno incluido" en la descripción.

    Atributos:
        COSTO (float): Cargo fijo por el servicio de desayuno.

    Ejemplo:
        >>> DesayunoIncluido(HabitacionBasica("Doble 101", 80.0)).precio
        95.0
    """

    COSTO = 15.00

    @property
    def descripcion(self) -> str:
        """Extiende la descripción con la leyenda de desayuno incluido."""
        return self._componente.descripcion + " + Desayuno incluido"

    @property
    def precio(self) -> float:
        """Suma el costo del desayuno al precio del componente."""
        return round(self._componente.precio + self.COSTO, 2)


class SeguroViaje(DecoradorHabitacion):
    """Decorador que agrega seguro de viaje a la habitación (2% sobre el precio actual).

    El cargo es proporcional al precio del componente en ese momento, lo que
    significa que si ya se aplicaron otros decoradores, el seguro se calcula
    sobre el precio ya aumentado. No confundir con el seguro de cancelación de
    la Reserva (Builder), que es el 3% del subtotal.

    Atributos:
        PORCENTAJE (float): Porcentaje del precio que se cobra como seguro (0.02 = 2%).

    Ejemplo:
        >>> SeguroViaje(DesayunoIncluido(HabitacionBasica("Doble 101", 85.0))).precio
        102.0
    """

    PORCENTAJE = 0.02

    @property
    def descripcion(self) -> str:
        """Extiende la descripción con la leyenda del seguro de viaje."""
        return self._componente.descripcion + " + Seguro de viaje"

    @property
    def precio(self) -> float:
        """Suma el 2% del precio actual; ValueError si el resultado no es finito."""
        precio = round(self._componente.precio * (1 + self.PORCENTAJE), 2)
        if not es_finito(precio):
            raise ValueError("El precio con seguro excede el rango numérico")
        return precio


class LateCheckout(DecoradorHabitacion):
    """Decorador que agrega salida tardía (late checkout) a la habitación (+$25.00).

    Aplica un cargo fijo e incluye la leyenda "+ Late checkout" en la
    descripción. Permite al huésped dejar la habitación más tarde del horario
    habitual.

    Atributos:
        COSTO (float): Cargo fijo por la salida tardía.

    Ejemplo:
        >>> LateCheckout(HabitacionBasica("Doble 101", 80.0)).descripcion
        'Doble 101 + Late checkout'
    """

    COSTO = 25.00

    @property
    def descripcion(self) -> str:
        """Extiende la descripción con la leyenda de late checkout."""
        return self._componente.descripcion + " + Late checkout"

    @property
    def precio(self) -> float:
        """Suma el costo del late checkout al precio del componente."""
        return round(self._componente.precio + self.COSTO, 2)

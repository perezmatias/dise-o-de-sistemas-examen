"""
Patrón Factory Method - Habitaciones (interfaz y habitaciones concretas).

En el patrón Factory Method, los creadores (ver creador_habitacion.py) devuelven
objetos que cumplen la interfaz Habitacion; cada creador concreto decide qué
habitación concreta instanciar, y el código cliente solo trabaja contra Habitacion.

Analogía:
    La recepción del hotel pide "una habitación" sin saber cuál: el sector de
    habitaciones estándar entrega una doble con sus camas, el sector de suites
    entrega una suite con su vista. Recepción solo usa lo que recibe.

Este módulo define:
    - Habitacion: Clase abstracta base que establece la interfaz común.
    - HabitacionEstandar: Habitación concreta con cantidad de camas.
    - Suite: Habitación concreta con una vista destacada.

Concepto clave - Clase Abstracta (ABC):
    Una clase abstracta NO se puede instanciar directamente. Sirve como
    "contrato" que obliga a las subclases a implementar ciertos métodos.
    En Python se logra heredando de ABC y usando @abstractmethod.

Ejemplo de uso:
    >>> doble = HabitacionEstandar("Doble 101", 80.0)
    >>> doble.mostrar_info()
    Habitación Estándar: Doble 101 | Camas: 2 | Tarifa: $80.00/noche
    >>> doble.nombre
    'Doble 101'
    >>> doble.tarifa
    80.0
"""

from abc import ABC, abstractmethod

from patrones._numeros import es_finito


class Habitacion(ABC):
    """Clase abstracta base para todas las habitaciones del hotel.

    Define la interfaz común que deben cumplir todas las habitaciones.
    No se puede instanciar directamente (es abstracta).

    Atributos:
        _nombre (str): Nombre o número de la habitación.
        _tarifa (float): Tarifa por noche de la habitación.
    """

    def __init__(self, nombre: str, tarifa: float) -> None:
        """Inicializa los atributos comunes a todas las habitaciones.

        Args:
            nombre: Nombre o número de la habitación.
            tarifa: Número finito no negativo (int o float, excluyendo bool),
                expresado por noche.

        Raises:
            TypeError: Si la tarifa no es int o float, o es bool.
            ValueError: Si la tarifa es negativa, no finita o no representable como float.
        """
        if not isinstance(tarifa, (int, float)) or isinstance(tarifa, bool):
            raise TypeError("La tarifa debe ser un número")
        if not es_finito(tarifa):
            raise ValueError("La tarifa debe ser un número finito")
        if tarifa < 0:
            raise ValueError(f"La tarifa no puede ser negativa: {tarifa}")
        self._nombre = nombre
        self._tarifa = tarifa

    @abstractmethod
    def mostrar_info(self) -> None:
        """Muestra la información de la habitación en consola.

        Cada subclase DEBE implementar este método con su propio formato.
        Si no lo implementa, Python lanzará TypeError al intentar instanciarla.
        """
        pass

    @property
    def nombre(self) -> str:
        """Nombre de la habitación (solo lectura)."""
        return self._nombre

    @property
    def tarifa(self) -> float:
        """Tarifa por noche de la habitación (solo lectura)."""
        return self._tarifa


class HabitacionEstandar(Habitacion):
    """Habitación concreta de categoría estándar.

    Hereda de Habitacion y agrega el atributo _camas.
    Implementa mostrar_info() con el formato específico para habitaciones estándar.

    Atributos:
        _camas (int): Cantidad de camas de la habitación.
    """

    def __init__(self, nombre: str, tarifa: float, camas: int = 2) -> None:
        """Inicializa una habitación estándar con nombre, tarifa y camas.

        Args:
            nombre: Nombre o número de la habitación.
            tarifa: Tarifa por noche.
            camas: Cantidad de camas. Por defecto, 2.
        """
        super().__init__(nombre, tarifa)
        self._camas = camas

    @property
    def camas(self) -> int:
        """Cantidad de camas de la habitación (solo lectura)."""
        return self._camas

    def mostrar_info(self) -> None:
        """Muestra la información de la habitación: nombre, camas y tarifa."""
        print(f"Habitación Estándar: {self._nombre} | Camas: {self._camas} "
              f"| Tarifa: ${self._tarifa:.2f}/noche")

    def __repr__(self) -> str:
        """Representación técnica útil para depuración."""
        return (f"HabitacionEstandar(nombre={self._nombre!r}, tarifa={self._tarifa}, "
                f"camas={self._camas})")


class Suite(Habitacion):
    """Habitación concreta de categoría suite.

    Hereda de Habitacion y agrega el atributo _vista.
    Implementa mostrar_info() con el formato específico para suites.

    Atributos:
        _vista (str): Descripción de la vista de la suite.
    """

    def __init__(self, nombre: str, tarifa: float, vista: str = "Vista al jardín") -> None:
        """Inicializa una suite con nombre, tarifa y vista.

        Args:
            nombre: Nombre o número de la suite.
            tarifa: Tarifa por noche.
            vista: Descripción de la vista. Por defecto, "Vista al jardín".
        """
        super().__init__(nombre, tarifa)
        self._vista = vista

    @property
    def vista(self) -> str:
        """Vista de la suite (solo lectura)."""
        return self._vista

    def mostrar_info(self) -> None:
        """Muestra la información de la suite: nombre, vista y tarifa."""
        print(f"Suite: {self._nombre} | {self._vista} | Tarifa: ${self._tarifa:.2f}/noche")

    def __repr__(self) -> str:
        """Representación técnica útil para depuración."""
        return f"Suite(nombre={self._nombre!r}, tarifa={self._tarifa}, vista={self._vista!r})"

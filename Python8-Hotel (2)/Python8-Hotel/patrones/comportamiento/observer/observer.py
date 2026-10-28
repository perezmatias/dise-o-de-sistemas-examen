"""
Patrón Observer - Interfaz del observador y observador concreto.

El patrón Observer define una relación uno-a-muchos entre objetos: cuando un
objeto (el "sujeto") cambia de estado, todos sus dependientes (los "observadores")
son notificados automáticamente.

Este módulo define:
    - Observer: Interfaz abstracta que todo observador debe implementar.
    - Huesped: Observador concreto que representa a un huésped del hotel.

Analogía:
    Es como suscribirse a un canal de YouTube. Cuando el canal sube un video
    (nueva promoción), todos los suscriptores (huéspedes) reciben la notificación.
    Si te desuscribes, dejas de recibir avisos.

Ejemplo de uso:
    >>> huesped = Huesped("Juan")
    >>> huesped.actualizar("50% de descuento")
    Huésped Juan recibió notificación: 50% de descuento
    >>> huesped.nombre
    'Juan'
"""

from abc import ABC, abstractmethod


class Observer(ABC):
    """Interfaz abstracta que define el contrato para los observadores.

    Todo objeto que quiera recibir notificaciones de un sujeto observable
    debe heredar de esta clase e implementar el método actualizar().
    """

    @abstractmethod
    def actualizar(self, mensaje: str) -> None:
        """Recibe una notificación del sujeto observable.

        Args:
            mensaje: El contenido de la notificación.
        """
        pass


class Huesped(Observer):
    """Observador concreto que representa a un huésped del hotel.

    Implementa el método actualizar() para recibir y mostrar las
    notificaciones enviadas por el hotel.

    Atributos:
        _nombre (str): Nombre del huésped.
    """

    def __init__(self, nombre: str) -> None:
        """Inicializa un huésped con su nombre.

        Args:
            nombre: Nombre del huésped.
        """
        self._nombre = nombre

    def actualizar(self, mensaje: str) -> None:
        """Recibe y muestra una notificación del hotel.

        Args:
            mensaje: Contenido de la notificación recibida.
        """
        print(f"Huésped {self._nombre} recibió notificación: {mensaje}")

    @property
    def nombre(self) -> str:
        """Nombre del huésped (solo lectura)."""
        return self._nombre

    def __repr__(self) -> str:
        """Representación técnica útil para depuración."""
        return f"Huesped({self._nombre!r})"

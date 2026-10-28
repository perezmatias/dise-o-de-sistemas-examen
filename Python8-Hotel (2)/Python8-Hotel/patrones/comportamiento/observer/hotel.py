"""
Patrón Observer - Sujeto observable (Hotel).

El Hotel actúa como el "sujeto" o "publicador" en el patrón Observer.
Mantiene una lista de observadores (huéspedes suscritos) y los notifica
cuando ocurre un evento relevante (nueva promoción).

Flujo del patrón:
    1. Los huéspedes se suscriben con suscribir().
    2. El hotel publica una promoción con nueva_promocion().
    3. Internamente se llama a notificar_huespedes(), que recorre la lista
       y llama a actualizar() en cada huésped suscrito.
    4. Los huéspedes pueden desuscribirse con desuscribir().

Validaciones implementadas:
    - Solo se aceptan objetos que hereden de Observer (isinstance).
    - No se permiten suscripciones duplicadas.
    - desuscribir() verifica que el huésped exista antes de eliminarlo.

Ejemplo de uso:
    >>> from patrones.comportamiento.observer.observer import Huesped
    >>> hotel = Hotel("Hotel Los Cortez")
    >>> huesped = Huesped("Ana")
    >>> hotel.suscribir(huesped)
    Huésped suscrito al hotel Hotel Los Cortez
    >>> hotel.nueva_promocion("20% en suites")
    <BLANKLINE>
    ¡Nueva promoción en Hotel Los Cortez!
    <BLANKLINE>
    --- Notificando a 1 huéspedes ---
    Huésped Ana recibió notificación: Nueva promoción: 20% en suites
"""

from typing import List

from patrones.comportamiento.observer.observer import Observer


class Hotel:
    """Sujeto observable que notifica promociones a sus huéspedes suscritos.

    Atributos:
        _nombre (str): Nombre del hotel.
        _huespedes (list): Lista de observadores (huéspedes) suscritos.
    """

    def __init__(self, nombre: str) -> None:
        """Inicializa el hotel con su nombre y una lista vacía de huéspedes.

        Args:
            nombre (str): Nombre del hotel.
        """
        self._nombre = nombre
        self._huespedes: List[Observer] = []

    @property
    def nombre(self) -> str:
        """Nombre del hotel (solo lectura)."""
        return self._nombre

    def suscribir(self, huesped: Observer) -> None:
        """Agrega un huésped a la lista de suscriptores.

        Validaciones:
            - El huésped debe ser una instancia de Observer (TypeError si no).
            - No se permiten suscripciones duplicadas del mismo huésped.

        Args:
            huesped (Observer): El huésped que desea suscribirse.

        Raises:
            TypeError: Si el objeto no es una instancia de Observer.
        """
        if not isinstance(huesped, Observer):
            raise TypeError("El objeto debe ser una instancia de Observer")
        if huesped in self._huespedes:
            print(f"Huésped ya está suscrito al hotel {self._nombre}")
            return
        self._huespedes.append(huesped)
        print(f"Huésped suscrito al hotel {self._nombre}")

    def desuscribir(self, huesped: Observer) -> None:
        """Elimina un huésped de la lista de suscriptores.

        Si el huésped no está suscrito, muestra un mensaje informativo
        en lugar de lanzar una excepción.

        Args:
            huesped (Observer): El huésped que desea desuscribirse.
        """
        if huesped not in self._huespedes:
            print(f"Huésped no está suscrito al hotel {self._nombre}")
            return
        self._huespedes.remove(huesped)
        print(f"Huésped desuscrito del hotel {self._nombre}")

    def notificar_huespedes(self, mensaje: str) -> None:
        """Envía un mensaje a todos los huéspedes suscritos.

        Recorre una copia de la lista _huespedes y llama al método actualizar()
        de cada observador. Se itera sobre una copia porque un observador
        podría desuscribirse dentro de actualizar(); modificar la lista
        mientras se la recorre haría que se saltee al siguiente huésped.

        Args:
            mensaje (str): El mensaje a enviar a todos los suscriptores.
        """
        print(f"\n--- Notificando a {len(self._huespedes)} huéspedes ---")
        for huesped in list(self._huespedes):
            huesped.actualizar(mensaje)

    def nueva_promocion(self, descripcion: str) -> None:
        """Publica una nueva promoción y notifica a todos los suscriptores.

        Este es el método que dispara todo el mecanismo del Observer:
        crea el mensaje y delega a notificar_huespedes().

        Args:
            descripcion (str): Descripción de la promoción.
        """
        print(f"\n¡Nueva promoción en {self._nombre}!")
        self.notificar_huespedes(f"Nueva promoción: {descripcion}")

"""
Patrón Factory Method - Creadores de habitaciones.

El patrón Factory Method (GoF) define una interfaz para crear un objeto, pero
deja que las SUBCLASES decidan qué clase concreta instanciar. Así, el código
del creador trabaja contra la abstracción Habitacion y nunca nombra a
HabitacionEstandar ni a Suite.

Analogía:
    Cada sector del hotel prepara su propio tipo de habitación. Recepción pide
    "registrar una habitación" al sector correspondiente y la usa tal como
    llega, sin saber cómo la armó el sector.

Participantes del patrón en este módulo:
    - Habitacion (en habitacion.py): interfaz de los objetos que se crean.
    - HabitacionEstandar / Suite (en habitacion.py): habitaciones concretas.
    - CreadorHabitacion: creador abstracto. Declara el factory method
      crear_habitacion() y una operación propia (registrar_habitacion()) que lo usa.
    - CreadorHabitacionEstandar / CreadorSuite: creadores concretos. Sobreescriben
      crear_habitacion() para devolver su habitación concreta.

Diferencia con una "Simple Factory":
    En una Simple Factory, UNA clase decide con un if/elif qué habitación crear;
    agregar un tipo nuevo obliga a modificarla. En Factory Method la decisión
    está repartida en subclases: agregar un tipo nuevo es agregar un creador
    nuevo, sin tocar el código existente (principio abierto/cerrado).

Ejemplo de uso:
    >>> creador = CreadorHabitacionEstandar(1)
    >>> simple = creador.crear_habitacion("Simple 102", 55.5)
    >>> simple.nombre
    'Simple 102'
    >>> suite = CreadorSuite("Vista al mar").registrar_habitacion("Suite Nupcial", 250.0)
    Suite: Suite Nupcial | Vista al mar | Tarifa: $250.00/noche
"""

from abc import ABC, abstractmethod

from patrones.creacionales.factory.habitacion import Habitacion, HabitacionEstandar, Suite


class CreadorHabitacion(ABC):
    """Creador abstracto del patrón Factory Method.

    Declara el factory method crear_habitacion(), que cada subclase implementa
    devolviendo su habitación concreta. También ofrece registrar_habitacion(),
    una operación que usa el factory method sin conocer la clase concreta creada.
    """

    @abstractmethod
    def crear_habitacion(self, nombre: str, tarifa: float) -> Habitacion:
        """Factory method: crea la habitación concreta que corresponde al creador.

        Args:
            nombre (str): Nombre o número de la habitación.
            tarifa (float): Tarifa por noche de la habitación.

        Returns:
            Habitacion: Instancia de la habitación concreta.
        """
        pass

    def registrar_habitacion(self, nombre: str, tarifa: float) -> Habitacion:
        """Crea una habitación mediante el factory method y muestra su información.

        Este método no sabe qué habitación concreta se crea: delega esa decisión
        a crear_habitacion() y luego usa el resultado solo a través de la
        interfaz Habitacion (mostrar_info() es polimórfico).

        Args:
            nombre (str): Nombre o número de la habitación.
            tarifa (float): Tarifa por noche de la habitación.

        Returns:
            Habitacion: La habitación creada y mostrada.
        """
        habitacion = self.crear_habitacion(nombre, tarifa)
        habitacion.mostrar_info()
        return habitacion


class CreadorHabitacionEstandar(CreadorHabitacion):
    """Creador concreto que produce instancias de HabitacionEstandar.

    Atributos:
        _camas (int): Cantidad de camas de las habitaciones que crea este creador.
    """

    def __init__(self, camas: int = 2) -> None:
        """Inicializa el creador con las camas de las habitaciones que va a crear.

        Args:
            camas (int): Cantidad de camas. Por defecto, 2.
        """
        self._camas = camas

    def crear_habitacion(self, nombre: str, tarifa: float) -> HabitacionEstandar:
        """Crea una HabitacionEstandar con las camas configuradas en este creador.

        Args:
            nombre (str): Nombre o número de la habitación.
            tarifa (float): Tarifa por noche.

        Returns:
            HabitacionEstandar: Nueva instancia de HabitacionEstandar.
        """
        return HabitacionEstandar(nombre, tarifa, self._camas)


class CreadorSuite(CreadorHabitacion):
    """Creador concreto que produce instancias de Suite.

    Atributos:
        _vista (str): Vista de las suites que crea este creador.
    """

    def __init__(self, vista: str = "Vista al jardín") -> None:
        """Inicializa el creador con la vista de las suites que va a crear.

        Args:
            vista (str): Descripción de la vista. Por defecto, "Vista al jardín".
        """
        self._vista = vista

    def crear_habitacion(self, nombre: str, tarifa: float) -> Suite:
        """Crea una Suite con la vista configurada en este creador.

        Args:
            nombre (str): Nombre o número de la suite.
            tarifa (float): Tarifa por noche.

        Returns:
            Suite: Nueva instancia de Suite.
        """
        return Suite(nombre, tarifa, self._vista)

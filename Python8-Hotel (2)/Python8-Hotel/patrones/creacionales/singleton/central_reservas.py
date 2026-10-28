"""
Patrón Singleton - Central única de reservas del hotel.

El patrón Singleton garantiza que una clase tenga **una sola instancia** en toda
la aplicación y proporciona un punto de acceso global a ella.

Analogía:
    Un hotel tiene UNA sola central de reservas. Recepción, el sitio web y los
    agentes de viaje comparten el mismo mostrador dentro de un proceso.

Problema que resuelve:
    El Singleton permite compartir la identidad y la inicialización de la central.
    No consulta inventario ni evita reservas duplicadas: eso requiere controles
    de negocio y transacciones. Tampoco comparte una instancia entre procesos.

Cómo funciona en Python:
    1. Se sobreescribe __new__() para controlar la creación del objeto.
    2. Una variable de clase (_instance) guarda la referencia a la única instancia.
    3. Un flag (_initialized) evita que __init__() reinicialice los datos.

Ejemplo de uso:
    >>> db1 = CentralReservas.get_instance()
    Conectando a la central de reservas de Hotel Los Cortez...
    >>> db2 = CentralReservas.get_instance()  # ya existe: no se vuelve a crear
    >>> db1 is db2  # ambas variables apuntan al mismo objeto
    True
    >>> db1.consultar("Habitaciones libres")
    [CentralReservas] Ejecutando: Habitaciones libres

Acceso concurrente:
    Sin protección, dos hilos podrían ver _instance en None (o _initialized en
    False) al mismo tiempo y crear/inicializar la central dos veces. Un Lock de
    clase serializa la creación ("double-checked locking") y la inicialización,
    no las operaciones de negocio. Este ejemplo no define herencia del Singleton.
"""

import threading


class CentralReservas:
    """Clase que implementa el patrón Singleton para la central de reservas.

    Atributos de clase:
        _instance: Referencia a la única instancia de la clase (None si no existe).
        _lock (threading.Lock): Protege la creación e inicialización entre hilos.

    Atributos de instancia:
        _initialized (bool): Flag que previene reinicialización del objeto.
        _hotel (str): Nombre del hotel al que pertenece la central.
        _conectado (bool): Indica si la central está conectada.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "CentralReservas":
        """Controla la creación del objeto. Si ya existe una instancia, la retorna.

        Este método se ejecuta ANTES que __init__(). Es el responsable de crear
        (o no) el objeto en memoria. Se verifica _instance dos veces: afuera del
        lock (rápido, caso común) y adentro (seguro frente a otros hilos).

        Returns:
            CentralReservas: La única instancia de la clase.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CentralReservas, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Inicializa la central solo la primera vez.

        Gracias al flag _initialized, aunque Python llame a __init__() cada vez
        que se invoca CentralReservas(), la lógica de configuración se ejecuta
        una sola vez. El lock evita que dos hilos pasen el chequeo a la vez.
        """
        with self._lock:
            if not self._initialized:
                self._hotel = "Hotel Los Cortez"
                self._conectado = True
                print(f"Conectando a la central de reservas de {self._hotel}...")
                self._initialized = True

    @staticmethod
    def get_instance() -> "CentralReservas":
        """Punto de acceso global a la instancia Singleton.

        Delega la creación/obtención al mecanismo __new__(), que garantiza
        que siempre se retorne la misma instancia.

        Returns:
            CentralReservas: La única instancia de la clase.
        """
        return CentralReservas()

    def consultar(self, consulta: str) -> None:
        """Simula la ejecución de una consulta sobre la central de reservas.

        Args:
            consulta (str): La consulta a ejecutar.
        """
        print(f"[CentralReservas] Ejecutando: {consulta}")

    @property
    def hotel(self) -> str:
        """Nombre del hotel (solo lectura)."""
        return self._hotel

    @property
    def conectado(self) -> bool:
        """Indica si la central está conectada (solo lectura)."""
        return self._conectado

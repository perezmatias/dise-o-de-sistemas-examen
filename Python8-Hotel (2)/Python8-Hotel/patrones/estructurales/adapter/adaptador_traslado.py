"""
Módulo que implementa el patrón Adapter para los servicios de traslado del hotel.

El patrón Adapter (también llamado Wrapper) convierte la interfaz de una clase
en otra interfaz que el cliente espera. Permite que clases con interfaces
incompatibles trabajen juntas sin modificar su código fuente.

Analogía: es como el adaptador de enchufe que usas al viajar. Tu cargador tiene
clavijas de un tipo y la pared del hotel tiene otro; el adaptador no cambia ni
el cargador ni el tomacorriente, solo traduce entre ambos.

Problema que resuelve:
    El Hotel Los Cortez quiere ofrecer traslados aeropuerto-hotel con dos
    proveedores (taxi y shuttle), pero cada uno tiene su propia API con nombres
    de métodos distintos y unidades distintas:
    - El taxi usa metros, nombres de zona o barrio y devuelve "10-15 minutos".
    - El shuttle usa millas y códigos de zona como "Z1", "Z2" o "Z3".
    Sin el Adapter, el código de recepción tendría que conocer los detalles
    de cada proveedor y tendría lógica condicional para cada uno.

Solución con Adapter:
    Se define una interfaz unificada (ServicioTraslado) y se crean adaptadores que
    traducen las llamadas a esa interfaz hacia la API específica de cada sistema.
    El código cliente solo conoce ServicioTraslado — los detalles quedan encapsulados.

Clases:
    ServicioTraslado: Interfaz objetivo unificada (ABC).
    SistemaLegadoTaxi: Sistema de taxis existente con interfaz incompatible (adaptado).
    SistemaLegadoShuttle: Sistema de shuttle existente con interfaz incompatible (adaptado).
    AdaptadorTaxi: Adapter que traduce ServicioTraslado → SistemaLegadoTaxi.
    AdaptadorShuttle: Adapter que traduce ServicioTraslado → SistemaLegadoShuttle.

Uso:
    # El cliente solo conoce ServicioTraslado — no sabe qué proveedor usa
    def cotizar_traslado(servicio: ServicioTraslado, distancia_km, zona):
        costo = servicio.calcular_costo(distancia_km, zona)
        minutos = servicio.estimar_minutos(zona)
        print(f"Costo: ${costo:.2f} | Llegada estimada: {minutos} minutos")

    cotizar_traslado(AdaptadorTaxi(),    2.5, "Palermo")
    cotizar_traslado(AdaptadorShuttle(), 2.5, "Z1")

Ejemplo ejecutable:
    >>> AdaptadorTaxi().calcular_costo(2.5, "Palermo")
    6.25
    >>> AdaptadorShuttle().calcular_costo(2.5, "Z1")
    6.79
"""

import unicodedata
from abc import ABC, abstractmethod
from patrones._numeros import es_finito


def _normalizar_zona(zona: str) -> str:
    """Normaliza un nombre de zona: minúsculas, sin espacios extremos ni tildes.

    Args:
        zona (str): Nombre de zona o barrio tal como lo escribió el cliente.

    Returns:
        str: Nombre normalizado (por ejemplo, "  Núñez " → "nunez").

    Ejemplo:
        >>> _normalizar_zona("  PALERMÓ ")
        'palermo'
    """
    descompuesto = unicodedata.normalize("NFKD", zona.strip().lower())
    return "".join(c for c in descompuesto if not unicodedata.combining(c))


def _validar_distancia(distancia_km: float) -> None:
    """Valida que la distancia sea un número finito y positivo.

    Args:
        distancia_km (float): Distancia del traslado en kilómetros.

    Raises:
        TypeError: Si la distancia no es int o float, o es bool.
        ValueError: Si la distancia no es finita o no es mayor que cero.
    """
    if not isinstance(distancia_km, (int, float)) or isinstance(distancia_km, bool):
        raise TypeError("La distancia debe ser un número")
    if not es_finito(distancia_km) or distancia_km <= 0:
        raise ValueError("La distancia debe ser finita y mayor que cero")


# =============================================================================
# INTERFAZ OBJETIVO: lo que el cliente (recepción del hotel) espera
# =============================================================================

class ServicioTraslado(ABC):
    """Interfaz unificada para todos los servicios de traslado del hotel.

    Define el contrato que todos los adaptadores deben cumplir.
    El código cliente (recepción, reservas) solo trabaja contra esta interfaz
    y desconoce qué proveedor concreto está siendo utilizado.
    """

    @abstractmethod
    def calcular_costo(self, distancia_km: float, zona: str) -> float:
        """Calcula el costo del traslado en dólares.

        Args:
            distancia_km (float): Distancia del traslado en kilómetros.
            zona (str): Zona, barrio o código de zona de destino.

        Returns:
            float: Costo del traslado en dólares.
        """
        pass

    @abstractmethod
    def estimar_minutos(self, zona: str) -> int:
        """Estima los minutos de espera o de viaje del traslado.

        Args:
            zona (str): Zona, barrio o código de zona de destino.

        Returns:
            int: Cantidad de minutos estimados para el traslado.
        """
        pass

    @abstractmethod
    def crear_traslado(self, reserva_id: str, zona: str) -> str:
        """Registra el traslado y devuelve el identificador del servicio.

        Args:
            reserva_id (str): Identificador único de la reserva en el hotel.
            zona (str): Zona, barrio o código de zona de destino.

        Returns:
            str: Identificador del móvil o del asiento asignado.
        """
        pass


# =============================================================================
# SISTEMAS LEGADOS (ADAPTADOS): interfaces incompatibles preexistentes
# =============================================================================

class SistemaLegadoTaxi:
    """Sistema de taxis con su API propietaria incompatible con la del hotel.

    Este es el sistema "adaptado" (Adaptee). Usa metros en lugar de kilómetros,
    trabaja con nombres de zona o barrio, devuelve tiempos de espera como cadenas
    de texto ("10-15 minutos") y tiene nombres de métodos específicos del proveedor.

    En un proyecto real, esta clase representaría un SDK o librería de terceros
    que no podemos (o no queremos) modificar.

    Atributos:
        ZONAS_CERCANAS (set): Zonas con tarifa y espera reducidas (normalizadas).
    """

    ZONAS_CERCANAS = {"centro", "recoleta", "palermo", "san telmo"}

    def calcular_tarifa_taxi(self, metros: int, zona: str) -> float:
        """Calcula la tarifa del taxi en base a metros y zona de destino.

        Args:
            metros (int): Distancia del traslado en metros.
            zona (str): Zona o barrio de destino.

        Returns:
            float: Tarifa del taxi en dólares.

        Raises:
            ValueError: Si la tarifa excede el rango finito representable como float.
        """
        # Tarifa simulada: $2.50 base + $0.0015 por metro (cercana) o $0.0025 (otra)
        if not es_finito(metros):
            raise ValueError("La tarifa excede el rango numérico")
        por_metro = 0.0015 if _normalizar_zona(zona) in self.ZONAS_CERCANAS else 0.0025
        tarifa = round(2.50 + metros * por_metro, 2)
        if not es_finito(tarifa):
            raise ValueError("La tarifa excede el rango numérico")
        return tarifa

    def tiempo_espera_taxi(self, zona: str) -> str:
        """Devuelve el tiempo de espera como cadena de texto.

        Args:
            zona (str): Zona o barrio de destino.

        Returns:
            str: Tiempo estimado en formato "X-Y minutos".
        """
        # Simulación: zonas cercanas 10-15 minutos, resto 25-40 minutos
        if _normalizar_zona(zona) in self.ZONAS_CERCANAS:
            return "10-15 minutos"
        return "25-40 minutos"

    def asignar_movil(self, reserva_id: str, zona: str) -> str:
        """Asigna un móvil y registra el traslado en el sistema de taxis.

        Args:
            reserva_id (str): Número de reserva del hotel.
            zona (str): Zona o barrio de destino.

        Returns:
            str: Identificador del móvil asignado.
        """
        movil = f"TAXI-{reserva_id.upper()}-{_normalizar_zona(zona)[:3].upper()}"
        print(f"[Taxi] Móvil asignado para {reserva_id} hacia {zona}")
        return movil


class SistemaLegadoShuttle:
    """Sistema de shuttle con su API propietaria incompatible con la del hotel.

    Este es el segundo "adaptado" (Adaptee). Usa millas en lugar de kilómetros,
    trabaja con códigos de zona ("Z1", "Z2", "Z3") y devuelve los minutos
    como enteros directamente.

    En un proyecto real, representaría otro SDK de terceros con su propia forma
    de trabajar, completamente diferente al del taxi.
    """

    def obtener_precio_shuttle(self, millas: float, codigo_zona: str) -> float:
        """Calcula el precio del shuttle en base a millas y código de zona.

        Args:
            millas (float): Distancia del traslado en millas.
            codigo_zona (str): Código de zona de destino ("Z1", "Z2", "Z3").

        Returns:
            float: Precio del shuttle en dólares.
        """
        # Tarifa simulada: $4.00 base + $1.80 por milla
        return round(4.00 + millas * 1.80, 2)

    def minutos_estimados(self, codigo_zona: str) -> int:
        """Devuelve la cantidad de minutos estimados para el traslado.

        Args:
            codigo_zona (str): Código de zona de destino ("Z1", "Z2", "Z3"). Se
                normaliza con strip().upper(), igual que en reservar_asiento().

        Returns:
            int: Minutos estimados (20 para Z1, 35 para Z2, 50 para el resto).
        """
        # Simulación: Z1 es la zona más cercana al aeropuerto
        return {"Z1": 20, "Z2": 35}.get(codigo_zona.strip().upper(), 50)

    def reservar_asiento(self, reserva_id: str, codigo_zona: str) -> str:
        """Reserva un asiento en el shuttle y devuelve su identificador.

        Args:
            reserva_id (str): Número de reserva del hotel.
            codigo_zona (str): Código de zona de destino; el identificador usa
                strip().upper(), igual que minutos_estimados().

        Returns:
            str: Identificador del asiento reservado.
        """
        asiento = f"SHT{reserva_id.upper()}{codigo_zona.strip().upper()}"
        print(f"[Shuttle] Asiento reservado para {reserva_id} ({codigo_zona})")
        return asiento


# =============================================================================
# ADAPTADORES: traducen la interfaz objetivo a la API de cada sistema legado
# =============================================================================

class AdaptadorTaxi(ServicioTraslado):
    """Adapter que hace compatible SistemaLegadoTaxi con la interfaz ServicioTraslado.

    Traduce las llamadas de la interfaz unificada a las llamadas específicas
    del taxi, realizando conversiones de unidades donde es necesario:
    - Kilómetros → Metros (*1000)
    - "10-15 minutos" → 10 (extrae el primer número del string)

    Attributes:
        _taxi (SistemaLegadoTaxi): Instancia del sistema de taxis legado.
    """

    def __init__(self) -> None:
        """Inicializa el adaptador creando la instancia del sistema de taxis."""
        self._taxi = SistemaLegadoTaxi()

    def calcular_costo(self, distancia_km: float, zona: str) -> float:
        """Traduce la distancia en km a metros y delega al sistema de taxis.

        Args:
            distancia_km (float): Distancia del traslado en kilómetros.
            zona (str): Zona o barrio de destino.

        Returns:
            float: Costo del traslado según la tarifa del taxi.

        Raises:
            TypeError: Si la distancia no es int o float, o es bool.
            ValueError: Si la distancia no es positiva o la distancia/conversión/tarifa
                excede el rango finito representable como float.
        """
        _validar_distancia(distancia_km)
        # round() en vez de int(): int() trunca y subfactura (3.9 m → 3 m)
        metros_sin_redondear = distancia_km * 1000
        if not es_finito(metros_sin_redondear):
            raise ValueError("La conversión de la distancia excede el rango numérico")
        metros = int(round(metros_sin_redondear))
        return self._taxi.calcular_tarifa_taxi(metros, zona)

    def estimar_minutos(self, zona: str) -> int:
        """Obtiene el tiempo del taxi y extrae el mínimo de minutos como entero.

        Args:
            zona (str): Zona o barrio de destino.

        Returns:
            int: Estimado mínimo de minutos de espera del taxi.
        """
        tiempo_str = self._taxi.tiempo_espera_taxi(zona)
        # Parsea "10-15 minutos" → 10
        return int(tiempo_str.split("-")[0])

    def crear_traslado(self, reserva_id: str, zona: str) -> str:
        """Delega directamente la asignación del móvil al sistema de taxis.

        Args:
            reserva_id (str): Identificador de la reserva.
            zona (str): Zona o barrio de destino.

        Returns:
            str: Identificador del móvil asignado.
        """
        return self._taxi.asignar_movil(reserva_id, zona)


class AdaptadorShuttle(ServicioTraslado):
    """Adapter que hace compatible SistemaLegadoShuttle con la interfaz ServicioTraslado.

    Traduce las llamadas de la interfaz unificada a las llamadas específicas
    del shuttle, realizando conversiones de unidades donde es necesario:
    - Kilómetros → Millas (*0.621)
    - La zona se interpreta como código de zona ("Z1", "Z2", "Z3")

    Attributes:
        _shuttle (SistemaLegadoShuttle): Instancia del sistema de shuttle legado.
    """

    KM_A_MILLAS = 0.621

    def __init__(self) -> None:
        """Inicializa el adaptador creando la instancia del sistema de shuttle."""
        self._shuttle = SistemaLegadoShuttle()

    def calcular_costo(self, distancia_km: float, zona: str) -> float:
        """Traduce la distancia en km a millas y delega al sistema de shuttle.

        Args:
            distancia_km (float): Distancia del traslado en kilómetros.
            zona (str): Código de zona de destino (el shuttle usa códigos de zona).

        Returns:
            float: Costo del traslado según la tarifa del shuttle.

        Raises:
            TypeError: Si la distancia no es int o float, o es bool.
            ValueError: Si la distancia no es positiva o la distancia/tarifa
                excede el rango finito representable como float.
        """
        _validar_distancia(distancia_km)
        millas = round(distancia_km * self.KM_A_MILLAS, 3)
        costo = self._shuttle.obtener_precio_shuttle(millas, zona)
        if not es_finito(costo):
            raise ValueError("La tarifa excede el rango numérico")
        return costo

    def estimar_minutos(self, zona: str) -> int:
        """Delega directamente la estimación de minutos al sistema de shuttle.

        Args:
            zona (str): Código de zona de destino.

        Returns:
            int: Minutos estimados para el traslado.
        """
        return self._shuttle.minutos_estimados(zona)

    def crear_traslado(self, reserva_id: str, zona: str) -> str:
        """Delega la reserva del asiento al sistema de shuttle.

        Args:
            reserva_id (str): Identificador de la reserva.
            zona (str): Código de zona de destino.

        Returns:
            str: Identificador del asiento reservado.
        """
        return self._shuttle.reservar_asiento(reserva_id, zona)

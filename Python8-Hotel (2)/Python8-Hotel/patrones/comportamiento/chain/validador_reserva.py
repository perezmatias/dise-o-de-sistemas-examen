"""
Módulo que implementa el patrón Chain of Responsibility para validar reservas.

El patrón Chain of Responsibility (Cadena de Responsabilidad) permite pasar
solicitudes a lo largo de una cadena de manejadores. Cada manejador decide si
procesa la solicitud o la pasa al siguiente eslabón de la cadena.

Analogía: es como el check-in de un hotel. Tu reserva primero pasa por el
agente de disponibilidad, luego por el de régimen de comidas, luego por el
de identificación del huésped y por último por administración. Cada uno puede
aprobar, rechazar o escalar. Si uno rechaza, los demás no necesitan revisar.

Problema que resuelve:
    Validar una reserva requiere múltiples controles (disponibilidad, régimen,
    huésped, monto máximo). Sin Chain of Responsibility, el código de reservas
    tendría un método largo con ifs anidados acoplados a cada validación. Con este
    patrón, cada validación es una clase independiente y reutilizable, y la cadena
    se configura dinámicamente en tiempo de ejecución.

Clases:
    ValidadorReserva: Interfaz abstracta del manejador (ABC).
    ValidadorDisponibilidad: Verifica que la reserva incluya al menos una habitación.
    ValidadorRegimen: Verifica que el régimen de comidas sea ofrecido por el hotel.
    ValidadorHuesped: Verifica que el nombre del huésped esté completo.
    ValidadorMontoMaximo: Verifica que el monto no supere el límite permitido.

La reserva se representa como un dict con las siguientes claves:
    - "habitaciones" (list): Lista de habitaciones solicitadas.
    - "regimen" (str): Régimen de comidas ("solo alojamiento", "desayuno",
      "media pension", "pension completa").
    - "huesped" (str): Nombre del huésped titular.
    - "total" (float): Monto total de la reserva.

Uso:
    # Construir la cadena enlazando los validadores
    validador_disponibilidad = ValidadorDisponibilidad()
    validador_regimen        = ValidadorRegimen()
    validador_huesped        = ValidadorHuesped()
    validador_monto          = ValidadorMontoMaximo()

    validador_disponibilidad \\
        .set_siguiente(validador_regimen) \\
        .set_siguiente(validador_huesped) \\
        .set_siguiente(validador_monto)

    reserva = {
        "habitaciones": ["Doble 101", "Suite 301"],
        "regimen": "desayuno",
        "huesped": "Ana Pérez",
        "total": 950.00,
    }
    aprobada = validador_disponibilidad.validar(reserva)
    print("Reserva aprobada" if aprobada else "Reserva rechazada")

Ejemplo ejecutable:
    >>> cadena = ValidadorDisponibilidad()
    >>> _ = cadena.set_siguiente(ValidadorMontoMaximo())
    >>> cadena.validar({"habitaciones": ["Doble 101"], "total": 120.0})
      [Disponibilidad] OK: 1 habitación(es) solicitada(s).
      [Monto] OK: total $120.00 dentro del límite permitido.
    True
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from patrones._numeros import es_finito


class ValidadorReserva(ABC):
    """Interfaz abstracta del manejador en la cadena de responsabilidad.

    Define la estructura base para todos los validadores: cada uno guarda
    referencia al siguiente en la cadena y delega a él si su validación pasa.
    El método set_siguiente() devuelve el validador recibido, permitiendo
    encadenar llamadas fluidas: a.set_siguiente(b).set_siguiente(c).

    Attributes:
        _siguiente (ValidadorReserva): El siguiente validador en la cadena, o None.
    """

    def __init__(self) -> None:
        """Inicializa el validador sin sucesor en la cadena."""
        self._siguiente: Optional["ValidadorReserva"] = None

    def set_siguiente(self, validador: "ValidadorReserva") -> "ValidadorReserva":
        """Establece el siguiente validador en la cadena y lo devuelve.

        Devolver el validador recibido permite encadenar llamadas:
            a.set_siguiente(b).set_siguiente(c).set_siguiente(d)

        Args:
            validador (ValidadorReserva): El siguiente manejador en la cadena.

        Returns:
            ValidadorReserva: El mismo validador recibido (para encadenamiento fluido).

        Raises:
            ValueError: Si enlazarlo formaría un ciclo (la validación no terminaría nunca).
        """
        actual = validador
        while actual is not None:
            if actual is self:
                raise ValueError("No se puede enlazar el validador: formaría un ciclo")
            actual = actual._siguiente
        self._siguiente = validador
        return validador

    def _pasar_al_siguiente(self, reserva: Dict[str, Any]) -> bool:
        """Pasa la reserva al siguiente validador si existe; si no, aprueba.

        Este método es utilizado internamente por las subclases al final de
        una validación exitosa. Si no hay siguiente en la cadena, significa
        que todos los validadores pasaron y la reserva está aprobada.

        Args:
            reserva (dict): Datos de la reserva a validar.

        Returns:
            bool: True si el resto de la cadena aprueba (o si no hay más), False si no.
        """
        if self._siguiente:
            return self._siguiente.validar(reserva)
        return True

    @abstractmethod
    def validar(self, reserva: Dict[str, Any]) -> bool:
        """Valida la reserva y decide si continúa o detiene la cadena.

        Cada subclase implementa su regla de validación. Si la validación falla,
        debe imprimir el motivo y devolver False sin llamar al siguiente.
        Si pasa, debe llamar a self._pasar_al_siguiente(reserva).

        Args:
            reserva (dict): Diccionario con datos de la reserva:
                - "habitaciones" (list): Habitaciones solicitadas.
                - "regimen" (str): Régimen de comidas.
                - "huesped" (str): Nombre del huésped titular.
                - "total" (float): Monto total de la reserva.

        Returns:
            bool: True si la reserva pasa esta validación y todas las siguientes.
        """
        pass


class ValidadorDisponibilidad(ValidadorReserva):
    """Valida que la reserva incluya al menos una habitación.

    Es el primer eslabón recomendado de la cadena, ya que una reserva sin
    habitaciones no tiene sentido procesar con los demás validadores.
    """

    def validar(self, reserva: Dict[str, Any]) -> bool:
        """Verifica que la lista de habitaciones no esté vacía.

        Args:
            reserva (dict): Datos de la reserva a validar.

        Returns:
            bool: True si hay una lista no vacía; False si el tipo es inválido
                o la reserva no tiene habitaciones.
        """
        if not isinstance(reserva, dict):
            print("  [Reserva] RECHAZADO: se requiere un diccionario.")
            return False
        habitaciones = reserva.get("habitaciones") or []
        if not isinstance(habitaciones, list) or not habitaciones:
            print("  [Disponibilidad] RECHAZADO: la reserva no incluye habitaciones.")
            return False
        print(f"  [Disponibilidad] OK: {len(habitaciones)} habitación(es) solicitada(s).")
        return self._pasar_al_siguiente(reserva)


class ValidadorRegimen(ValidadorReserva):
    """Valida que el régimen de comidas sea ofrecido por el hotel.

    Los regímenes aceptados son: "solo alojamiento", "desayuno",
    "media pension" y "pension completa". La comparación es insensible
    a mayúsculas y a espacios al inicio o final.
    """

    REGIMENES_ACEPTADOS = {"solo alojamiento", "desayuno", "media pension", "pension completa"}

    def validar(self, reserva: Dict[str, Any]) -> bool:
        """Verifica que el régimen esté en la lista de aceptados.

        Args:
            reserva (dict): Datos de la reserva a validar.

        Returns:
            bool: True si el régimen es aceptado; False si es inválido o falta.
        """
        if not isinstance(reserva, dict):
            print("  [Reserva] RECHAZADO: se requiere un diccionario.")
            return False
        regimen = reserva.get("regimen")
        regimen = regimen.strip().lower() if isinstance(regimen, str) else ""
        if regimen not in self.REGIMENES_ACEPTADOS:
            # sorted(): un set no garantiza orden entre ejecuciones
            print(f"  [Régimen] RECHAZADO: régimen '{regimen}' no está disponible. "
                  f"Aceptados: {', '.join(sorted(self.REGIMENES_ACEPTADOS))}.")
            return False
        print(f"  [Régimen] OK: régimen '{regimen}' aceptado.")
        return self._pasar_al_siguiente(reserva)


class ValidadorHuesped(ValidadorReserva):
    """Valida que el nombre del huésped titular esté completo.

    Requiere que el nombre tenga al menos 5 caracteres (sin espacios
    al inicio o final), lo que filtra nombres incompletos o vacíos.
    """

    LONGITUD_MINIMA = 5

    def validar(self, reserva: Dict[str, Any]) -> bool:
        """Verifica que el nombre del huésped cumpla con la longitud mínima.

        Args:
            reserva (dict): Datos de la reserva a validar.

        Returns:
            bool: True si el nombre es válido; False si está vacío o es muy corto.
        """
        if not isinstance(reserva, dict):
            print("  [Reserva] RECHAZADO: se requiere un diccionario.")
            return False
        huesped = reserva.get("huesped")
        huesped = huesped.strip() if isinstance(huesped, str) else ""
        if len(huesped) < self.LONGITUD_MINIMA:
            print(f"  [Huésped] RECHAZADO: nombre incompleto "
                  f"(mínimo {self.LONGITUD_MINIMA} caracteres).")
            return False
        print(f"  [Huésped] OK: '{huesped}'.")
        return self._pasar_al_siguiente(reserva)


class ValidadorMontoMaximo(ValidadorReserva):
    """Valida que el monto total de la reserva no supere el límite permitido.

    Reservas con montos excesivamente altos son señal de posible error o
    fraude. El límite predeterminado es $10.000. Este validador se recomienda
    como último eslabón de la cadena.
    """

    MONTO_MAXIMO = 10000.00

    def validar(self, reserva: Dict[str, Any]) -> bool:
        """Verifica que el total de la reserva no supere el límite permitido.

        Args:
            reserva (dict): Datos de la reserva a validar.

        Returns:
            bool: True si el monto es aceptable; False si no es numérico,
                no es finito, es negativo o supera el límite.
                Un total ausente equivale a cero según HU-039.
        """
        if not isinstance(reserva, dict):
            print("  [Reserva] RECHAZADO: se requiere un diccionario.")
            return False
        total = reserva.get("total", 0)
        # bool es subclase de int en Python: se excluye explícitamente
        if not isinstance(total, (int, float)) or isinstance(total, bool):
            print(f"  [Monto] RECHAZADO: total inválido ({total!r}).")
            return False
        if not es_finito(total):
            print("  [Monto] RECHAZADO: el total debe ser finito.")
            return False
        if total < 0:
            print(f"  [Monto] RECHAZADO: total negativo ${total:.2f}.")
            return False
        if total > self.MONTO_MAXIMO:
            print(f"  [Monto] RECHAZADO: total ${total:.2f} supera el límite "
                  f"de ${self.MONTO_MAXIMO:.2f}.")
            return False
        print(f"  [Monto] OK: total ${total:.2f} dentro del límite permitido.")
        return self._pasar_al_siguiente(reserva)

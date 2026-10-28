#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demostración de Patrones de Diseño en Python - Sistema de Gestión Hotelera.

Este archivo es el punto de entrada del programa. Ejecuta demostraciones
de los 8 patrones de diseño implementados en el paquete 'patrones/', en el
mismo orden y con la misma numeración que las secciones de la salida:

    1. Singleton  - Una sola central de reservas.             (Creacional)
    2. Factory Method - Subclases deciden qué habitación crear. (Creacional)
    3. Observer   - Notificaciones a huéspedes suscritos.     (Comportamiento)
    4. Strategy   - Políticas de tarifa intercambiables.      (Comportamiento)
    5. Builder    - Construcción paso a paso de reservas.     (Creacional)
    6. Decorator  - Servicios opcionales sobre habitaciones.  (Estructural)
    7. Adapter    - Servicios de traslado con APIs incompatibles. (Estructural)
    8. Chain of Responsibility - Validación de reservas.      (Comportamiento)

Ejecución:
    python main.py

Cada sección está claramente separada para que el estudiante pueda
identificar qué patrón se está demostrando y cómo se usa.
"""

# Importaciones organizadas en 3 bloques por categoría GoF (HU-040)

# Patrones creacionales
from patrones.creacionales.singleton import CentralReservas
from patrones.creacionales.factory import (
    CreadorHabitacion, CreadorHabitacionEstandar, CreadorSuite,
)
from patrones.creacionales.builder import (
    ReservaEstandarBuilder, ReservaPremiumBuilder, DirectorReserva,
)

# Patrones estructurales
from patrones.estructurales.decorator import (
    HabitacionBasica, DesayunoIncluido, SeguroViaje, LateCheckout,
)
from patrones.estructurales.adapter import ServicioTraslado, AdaptadorTaxi, AdaptadorShuttle

# Patrones de comportamiento
from patrones.comportamiento.observer import Huesped, Hotel
from patrones.comportamiento.strategy import (
    Cotizador, TarifaTemporadaAlta, TarifaTemporadaBaja, TarifaCorporativa,
)
from patrones.comportamiento.chain import (
    ValidadorDisponibilidad, ValidadorRegimen, ValidadorHuesped, ValidadorMontoMaximo,
)


def main() -> None:
    """Función principal que demuestra todos los patrones de diseño."""
    print("=" * 50)
    print("DEMOSTRACIÓN DE PATRONES DE DISEÑO EN PYTHON")
    print("SISTEMA DE GESTIÓN HOTELERA")
    print("=" * 50)
    print()

    # ============================================
    # 1. PATRÓN SINGLETON - Central de reservas
    # ============================================
    # Demuestra que get_instance() siempre retorna el MISMO objeto.
    # No importa cuántas veces se llame, solo existe una central de reservas.
    print(">>> 1. PATRÓN SINGLETON <<<")
    central1 = CentralReservas.get_instance()
    central2 = CentralReservas.get_instance()

    # 'is' compara identidad (misma posición en memoria), no igualdad de valor
    print(f"¿Son la misma instancia? {central1 is central2}")
    central1.consultar("Habitaciones libres del 10 al 13 de marzo")
    print()

    # ============================================
    # 2. PATRÓN FACTORY METHOD - Crear habitaciones
    # ============================================
    # Cada creador concreto (subclase de CreadorHabitacion) decide qué clase
    # instanciar en su factory method crear_habitacion(). registrar_habitacion()
    # es código del creador abstracto: usa el factory method y muestra la
    # habitación sin saber si es una HabitacionEstandar o una Suite.
    print(">>> 2. PATRÓN FACTORY METHOD <<<")
    creador_doble: CreadorHabitacion = CreadorHabitacionEstandar(2)
    creador_simple: CreadorHabitacion = CreadorHabitacionEstandar(1)
    creador_suite_mar: CreadorHabitacion = CreadorSuite("Vista al mar")
    creador_suite_jardin: CreadorHabitacion = CreadorSuite()  # vista por defecto: jardín

    doble = creador_doble.registrar_habitacion("Doble 101", 80.00)
    simple = creador_simple.registrar_habitacion("Simple 102", 55.50)
    suite_mar = creador_suite_mar.registrar_habitacion("Suite 501", 200.00)
    suite_jardin = creador_suite_jardin.registrar_habitacion("Suite 301", 150.00)

    # Los datos se leen mediante propiedades (@property), no con getters get_*()
    print(f"Acceso por propiedades -> nombre: {doble.nombre} | tarifa: ${doble.tarifa:.2f}")
    print()

    # ============================================
    # 3. PATRÓN OBSERVER - Sistema de promociones
    # ============================================
    # Los huéspedes se suscriben al hotel. Cuando hay una promoción,
    # todos los suscritos reciben la notificación automáticamente.
    print(">>> 3. PATRÓN OBSERVER <<<")
    hotel = Hotel("Hotel Los Cortez")

    huesped1 = Huesped("Ana Pérez")
    huesped2 = Huesped("Luis Gómez")
    huesped3 = Huesped("Marta Díaz")

    # Suscribir 3 huéspedes -> los 3 recibirán la primera promoción
    hotel.suscribir(huesped1)
    hotel.suscribir(huesped2)
    hotel.suscribir(huesped3)

    hotel.nueva_promocion("20% de descuento en suites")

    # Desuscribir a Luis -> solo Ana y Marta recibirán la siguiente promoción
    print()
    hotel.desuscribir(huesped2)
    print()

    hotel.nueva_promocion("Semana de vacaciones: 3 noches al precio de 2")
    print()

    # ============================================
    # 4. PATRÓN STRATEGY - Diferentes políticas de tarifa
    # ============================================
    # Cada cotizador usa una estrategia de tarifa diferente.
    # El Cotizador no sabe cómo funciona cada tarifa internamente;
    # solo llama a aplicar() y la estrategia se encarga del resto.
    # Las habitaciones son las creadas en la sección Factory Method.
    print(">>> 4. PATRÓN STRATEGY <<<")

    # Cotización 1 - Temporada alta (recargo del 30%)
    cotizador1 = Cotizador()
    cotizador1.agregar_habitacion(doble)
    cotizador1.agregar_habitacion(suite_mar)
    cotizador1.set_estrategia_tarifa(TarifaTemporadaAlta())
    cotizador1.confirmar()

    # Cotización 2 - Temporada baja (descuento del 20%)
    cotizador2 = Cotizador()
    cotizador2.agregar_habitacion(simple)
    cotizador2.agregar_habitacion(doble)
    cotizador2.set_estrategia_tarifa(TarifaTemporadaBaja())
    cotizador2.confirmar()

    # Cotización 3 - Tarifa corporativa (descuento del 10% por convenio con la empresa)
    cotizador3 = Cotizador()
    cotizador3.agregar_habitacion(suite_jardin)
    cotizador3.agregar_habitacion(suite_mar)
    cotizador3.set_estrategia_tarifa(TarifaCorporativa("Acme S.A."))
    cotizador3.confirmar()

    # ============================================
    # 5. PATRÓN BUILDER - Construcción de reservas
    # ============================================
    # El Builder construye un objeto complejo (Reserva) paso a paso.
    # El Director orquesta la secuencia; el cliente elige el tipo de builder.
    # Ventaja: sin un constructor de 10 parámetros ni combinaciones de subclases.
    print(">>> 5. PATRÓN BUILDER <<<")

    # Reserva estándar básica: el director ejecuta solo los pasos necesarios
    print("-- Reserva estándar básica --")
    builder_estandar = ReservaEstandarBuilder()
    director = DirectorReserva(builder_estandar)
    reserva_basica = director.construir_reserva_basica(doble, 3, "Ana Pérez")
    reserva_basica.mostrar_resumen()
    print()

    # Reserva premium completa: el director agrega todas las habitaciones
    # y el seguro de cancelación automáticamente
    print("-- Reserva premium completa --")
    builder_premium = ReservaPremiumBuilder()
    director.set_builder(builder_premium)
    reserva_completa = director.construir_reserva_completa(
        [suite_mar, suite_jardin],
        2,
        "Luis Gómez"
    )
    reserva_completa.mostrar_resumen()
    print()

    # ============================================
    # 6. PATRÓN DECORATOR - Servicios opcionales
    # ============================================
    # El Decorator agrega responsabilidades a un objeto dinámicamente.
    # Cada decorador "envuelve" al anterior y apila descripción y precio.
    # Ventaja: sin subclasificar cada combinación posible de servicios.
    print(">>> 6. PATRÓN DECORATOR <<<")

    # Habitación base sin decoradores
    habitacion_base = HabitacionBasica("Suite Presidencial", 899.99)
    print(f"Base:                {habitacion_base.descripcion}")
    print(f"                     Precio: ${habitacion_base.precio:.2f}")

    # Agregar desayuno incluido (+$15.00)
    con_desayuno = DesayunoIncluido(habitacion_base)
    print(f"+ DesayunoIncluido:  {con_desayuno.descripcion}")
    print(f"                     Precio: ${con_desayuno.precio:.2f}")

    # Agregar seguro de viaje sobre el precio ya con desayuno (+2%)
    con_seguro = SeguroViaje(con_desayuno)
    print(f"+ SeguroViaje:       {con_seguro.descripcion}")
    print(f"                     Precio: ${con_seguro.precio:.2f}")

    # Agregar late checkout (+$25.00)
    con_late_checkout = LateCheckout(con_seguro)
    print(f"+ LateCheckout:      {con_late_checkout.descripcion}")
    print(f"                     Precio: ${con_late_checkout.precio:.2f}")
    print()

    # ============================================
    # 7. PATRÓN ADAPTER - Servicios de traslado
    # ============================================
    # El taxi y el shuttle tienen APIs propietarias incompatibles entre sí.
    # El Adapter traduce ambas a una interfaz unificada (ServicioTraslado).
    # El código cliente llama siempre a calcular_costo/estimar_minutos/crear_traslado
    # sin importar qué proveedor está detrás.
    print(">>> 7. PATRÓN ADAPTER <<<")

    # Función cliente que trabaja solo contra la interfaz ServicioTraslado
    def cotizar_y_crear_traslado(servicio: ServicioTraslado, nombre_proveedor: str,
                                 distancia_km: float, zona: str, reserva_id: str) -> None:
        """Demuestra que el cliente usa la misma interfaz para cualquier proveedor.

        Args:
            servicio: Cualquier adaptador que implemente ServicioTraslado.
            nombre_proveedor: Etiqueta del proveedor para la salida.
            distancia_km: Distancia del traslado en kilómetros.
            zona: Barrio (taxi) o código de zona (shuttle), según HU-019/HU-020.
            reserva_id: Identificador de la reserva en el hotel.
        """
        costo = servicio.calcular_costo(distancia_km, zona)
        minutos = servicio.estimar_minutos(zona)
        print(f"  [{nombre_proveedor}] Costo: ${costo:.2f} | Minutos estimados: {minutos}")
        identificador = servicio.crear_traslado(reserva_id, zona)
        print(f"  [{nombre_proveedor}] Identificador: {identificador}")

    # Ambas variables se declaran con el tipo de la interfaz, no del adaptador concreto
    servicio_taxi: ServicioTraslado = AdaptadorTaxi()
    servicio_shuttle: ServicioTraslado = AdaptadorShuttle()

    print("-- Traslado en taxi (adaptador convierte km->metros, parsea 'X-Y minutos') --")
    cotizar_y_crear_traslado(servicio_taxi, "Taxi", 2.5, "Palermo", "RES-001")
    print()

    print("-- Traslado en shuttle (adaptador convierte km->millas, usa código de zona) --")
    cotizar_y_crear_traslado(servicio_shuttle, "Shuttle", 2.5, "Z1", "RES-001")
    print()

    # ============================================
    # 8. PATRÓN CHAIN OF RESPONSIBILITY - Validación
    # ============================================
    # La solicitud (reserva) pasa por una cadena de validadores.
    # Cada uno decide si aprueba y pasa al siguiente, o rechaza y detiene la cadena.
    # Ventaja: cada regla es independiente, reutilizable y la cadena es configurable.
    print(">>> 8. PATRÓN CHAIN OF RESPONSIBILITY <<<")

    # Construir la cadena: Disponibilidad → Régimen → Huésped → Monto máximo
    validador_disponibilidad = ValidadorDisponibilidad()
    validador_disponibilidad \
        .set_siguiente(ValidadorRegimen()) \
        .set_siguiente(ValidadorHuesped()) \
        .set_siguiente(ValidadorMontoMaximo())

    # Caso 1: reserva válida — debe pasar toda la cadena
    reserva_valida = {
        "habitaciones": ["Doble 101", "Suite 501"],
        "regimen": "desayuno",
        "huesped": "Ana Pérez",
        "total": 950.00,
    }
    print("-- Reserva válida --")
    resultado = validador_disponibilidad.validar(reserva_valida)
    print(f"  Resultado: {'APROBADA' if resultado else 'RECHAZADA'}")
    print()

    # Caso 2: reserva con régimen de comidas no ofrecido — debe fallar en ValidadorRegimen
    reserva_regimen_invalido = {
        "habitaciones": ["Simple 102"],
        "regimen": "todo incluido",
        "huesped": "Luis Gómez",
        "total": 320.00,
    }
    print("-- Reserva con régimen de comidas no ofrecido --")
    resultado2 = validador_disponibilidad.validar(reserva_regimen_invalido)
    print(f"  Resultado: {'APROBADA' if resultado2 else 'RECHAZADA'}")
    print()

    # Caso 3: reserva con monto excesivo — debe fallar en ValidadorMontoMaximo
    reserva_monto_excesivo = {
        "habitaciones": ["Suite 501", "Suite 301", "Doble 101"],
        "regimen": "pension completa",
        "huesped": "Marta Díaz",
        "total": 12500.00,
    }
    print("-- Reserva con monto que supera el límite permitido --")
    resultado3 = validador_disponibilidad.validar(reserva_monto_excesivo)
    print(f"  Resultado: {'APROBADA' if resultado3 else 'RECHAZADA'}")
    print()

    print("=" * 50)
    print("FIN DE LA DEMOSTRACIÓN")
    print("=" * 50)


# Este bloque asegura que main() solo se ejecute cuando el archivo
# se ejecuta directamente (python main.py), no cuando se importa como módulo.
if __name__ == "__main__":
    main()

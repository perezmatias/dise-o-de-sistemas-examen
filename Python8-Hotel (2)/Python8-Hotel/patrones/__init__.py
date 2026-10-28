"""
Paquete principal de patrones de diseño (Sistema de Gestión Hotelera).

Organizado en tres categorías GoF, cada una con sus subpaquetes:

Patrones Creacionales  (patrones.creacionales.*):
    - creacionales.singleton  → CentralReservas
    - creacionales.factory    → Habitacion, HabitacionEstandar, Suite, Creador* (Factory Method)
    - creacionales.builder    → Reserva, ReservaBuilder, Reserva*Builder, DirectorReserva

Patrones Estructurales  (patrones.estructurales.*):
    - estructurales.decorator → ComponenteHabitacion, HabitacionBasica, Decorador*, servicios
    - estructurales.adapter   → ServicioTraslado, SistemaLegado*, Adaptador*

Patrones de Comportamiento  (patrones.comportamiento.*):
    - comportamiento.observer → Observer, Huesped, Hotel
    - comportamiento.strategy → EstrategiaTarifa, Tarifa*, Cotizador
    - comportamiento.chain    → ValidadorReserva, Validador*
"""

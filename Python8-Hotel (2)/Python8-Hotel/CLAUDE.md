# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Educational Python project (Equipo: Desarrollo Los Cortez) demonstrating eight GoF design patterns through a simulated hotel management scenario ("Hotel Los Cortez"). Uses only the Python standard library — no external dependencies. Keep changes focused on the educational purpose of the repository.

The system models eight concrete problems grouped by GoF category:

- **Creacionales**: shared reservations center (Singleton), room creation delegated to creator subclasses (Factory Method), step-by-step reservation construction (Builder)
- **Estructurales**: optional room services stacked at runtime (Decorator), unified airport-transfer API over incompatible providers (Adapter)
- **Comportamiento**: guest notification system (Observer), interchangeable rate policies (Strategy), multi-step reservation validation (Chain of Responsibility)

Seven patterns use an abstract base class (ABC) and concrete implementations; Singleton directly controls instance creation. Each pattern lives in its own subpackage nested under one of three category packages inside `patrones/`.

This project is the hotel-domain twin of the e-commerce project `Python8-main` (see "Fuentes de verdad"): same architecture, conventions and robustness level, different domain.

## Running the Project

```bash
python main.py
```

Quick sanity checks for individual patterns:

```bash
# Singleton — verifica que dos llamadas devuelven el mismo objeto
python -c "from patrones.creacionales.singleton import CentralReservas; c1 = CentralReservas.get_instance(); c2 = CentralReservas.get_instance(); print('OK' if c1 is c2 else 'FAIL')"

# Factory Method — verifica que el creador concreto crea la habitación y se accede por propiedad
python -c "from patrones.creacionales.factory import CreadorHabitacionEstandar; h = CreadorHabitacionEstandar(1).crear_habitacion('Simple 102', 55.5); print('OK' if h.nombre == 'Simple 102' else 'FAIL')"

# Factory Method — verifica que cada creador concreto decide la clase de la habitación
python -c "from patrones.creacionales.factory import CreadorHabitacionEstandar, CreadorSuite, HabitacionEstandar, Suite; t = [type(c.crear_habitacion('X', 1.0)) for c in (CreadorHabitacionEstandar(), CreadorSuite())]; print('OK' if t == [HabitacionEstandar, Suite] else 'FAIL')"

# Builder — verifica que el director inicializa el builder correctamente
python -c "from patrones.creacionales.builder import ReservaEstandarBuilder, DirectorReserva; b = ReservaEstandarBuilder(); DirectorReserva(b); print('Builder OK')"

# Builder — verifica el total: 2 noches x $100 + servicio Premium $40 + seguro 3% ($6) = $246
python -c "
from patrones.creacionales.factory import CreadorSuite
from patrones.creacionales.builder import ReservaPremiumBuilder, DirectorReserva
h = CreadorSuite().crear_habitacion('Suite 501', 100.0)
r = DirectorReserva(ReservaPremiumBuilder()).construir_reserva_completa([h], 2, 'Ana Perez')
print('Builder total OK' if r.calcular_total() == 246.0 else 'FAIL')
"

# Decorator — verifica apilamiento de precio: base $100 + desayuno $15 = $115
python -c "
from patrones.estructurales.decorator import HabitacionBasica, DesayunoIncluido
h = DesayunoIncluido(HabitacionBasica('X', 100.0))
print('Decorator OK' if h.precio == 115.0 else 'FAIL')
"

# Adapter — verifica que el adaptador de taxi devuelve un costo mayor que 0
python -c "
from patrones.estructurales.adapter import AdaptadorTaxi
a = AdaptadorTaxi()
print('Adapter OK' if a.calcular_costo(2.0, 'Palermo') > 0 else 'FAIL')
"

# Observer — verifica suscripción y rechazo de duplicados
python -c "
from patrones.comportamiento.observer import Huesped, Hotel
h = Hotel('Test'); g = Huesped('Ana')
h.suscribir(g); h.suscribir(g)
print('OK' if len(h._huespedes) == 1 else 'FAIL')
"

# Strategy — verifica confirmación y reset del cotizador
python -c "
from patrones.creacionales.factory import CreadorHabitacionEstandar
from patrones.comportamiento.strategy import Cotizador, TarifaCorporativa
c = Cotizador(); c.set_estrategia_tarifa(TarifaCorporativa('ACME'))
c.agregar_habitacion(CreadorHabitacionEstandar().crear_habitacion('Test', 100.0))
c.confirmar()
print('OK' if c._habitaciones == [] else 'FAIL')
"

# Chain — verifica que una reserva válida pasa toda la cadena
python -c "
from patrones.comportamiento.chain import ValidadorDisponibilidad, ValidadorRegimen, ValidadorHuesped, ValidadorMontoMaximo
v = ValidadorDisponibilidad()
v.set_siguiente(ValidadorRegimen()).set_siguiente(ValidadorHuesped()).set_siguiente(ValidadorMontoMaximo())
r = v.validar({'habitaciones': ['x'], 'regimen': 'desayuno', 'huesped': 'Ana Perez', 'total': 100})
print('Chain OK' if r else 'FAIL')
"
```

Test suite (stdlib `unittest`, no external dependencies) lives in `tests/`: one file per pattern, a smoke test for `main.py` (HU-040 criteria), `test_convenciones.py` and `test_doctests.py`:

```bash
python -m unittest discover -s tests -t .
```

`tests/utilidades.py` provides `capturar_salida()` to capture `print()` output. `tests/test_convenciones.py` enforces lines ≤ 100 chars, type hints on every signature and no unused imports in `main.py` and `patrones/`. `tests/test_doctests.py` runs every `>>>` docstring example in `patrones/` (resetting the Singleton first), so docstring examples must show the exact output. Singleton tests reset `CentralReservas._instance = None` in `setUp()` for isolation. No build step, no linter configured. Target Python 3.6+.

## Architecture

`main.py` is the entry point — imports from `patrones` and demos each pattern in sequence inside `main()`. Rooms created in the Factory section (`Doble 101`, `Suite 501`, etc.) are deliberately reused in the Builder and Strategy sections to show realistic inter-pattern integration.

The `patrones/` package is organised into **three category packages**, each containing the relevant pattern subpackages with their own `__init__.py` re-exports:

```
patrones/
├── __init__.py
├── _numeros.py                     # Shared finite-float range check
├── creacionales/
│   ├── __init__.py
│   ├── singleton/
│   │   ├── __init__.py              # re-exports CentralReservas
│   │   └── central_reservas.py
│   ├── factory/
│   │   ├── __init__.py              # re-exports Habitacion, HabitacionEstandar, Suite, Creador*
│   │   ├── habitacion.py
│   │   └── creador_habitacion.py
│   └── builder/
│       ├── __init__.py              # re-exports Reserva, ReservaBuilder, Reserva*Builder, DirectorReserva
│       ├── reserva.py
│       └── reserva_builder.py
├── estructurales/
│   ├── __init__.py
│   ├── decorator/
│   │   ├── __init__.py              # re-exports ComponenteHabitacion, HabitacionBasica, Decorador*, servicios
│   │   └── decorador_habitacion.py
│   └── adapter/
│       ├── __init__.py              # re-exports ServicioTraslado, SistemaLegado*, Adaptador*
│       └── adaptador_traslado.py
└── comportamiento/
    ├── __init__.py
    ├── observer/
    │   ├── __init__.py              # re-exports Observer, Huesped, Hotel
    │   ├── observer.py
    │   └── hotel.py
    ├── strategy/
    │   ├── __init__.py              # re-exports EstrategiaTarifa, Tarifa*, Cotizador
    │   ├── estrategia_tarifa.py
    │   └── cotizador.py
    └── chain/
        ├── __init__.py              # re-exports ValidadorReserva, Validador*
        └── validador_reserva.py
```

| Category | Pattern | Subpackage path | Key Classes |
|----------|---------|-----------------|-------------|
| Creacional | Singleton | `creacionales.singleton` | `CentralReservas` — `__new__` + `_initialized` flag prevent re-init |
| Creacional | Factory Method | `creacionales.factory` | Abstract `Habitacion` → `HabitacionEstandar`, `Suite`; abstract creator `CreadorHabitacion` (factory method `crear_habitacion()`) → `CreadorHabitacionEstandar`, `CreadorSuite` |
| Creacional | Builder | `creacionales.builder` | `Reserva` (product); abstract `ReservaBuilder` → `ReservaEstandarBuilder`, `ReservaPremiumBuilder`; `DirectorReserva` orchestrates sequences |
| Estructural | Decorator | `estructurales.decorator` | Abstract `ComponenteHabitacion` → `HabitacionBasica`; instantiable base `DecoradorHabitacion` → `DesayunoIncluido`, `SeguroViaje`, `LateCheckout` |
| Estructural | Adapter | `estructurales.adapter` | Abstract `ServicioTraslado` (target); `SistemaLegadoTaxi`, `SistemaLegadoShuttle` (adaptees); `AdaptadorTaxi`, `AdaptadorShuttle` wrap adaptees |
| Comportamiento | Observer | `comportamiento.observer` | Abstract `Observer` → `Huesped`; `Hotel` validates `isinstance`, rejects duplicates, handles missing subscriber gracefully |
| Comportamiento | Strategy | `comportamiento.strategy` | Abstract `EstrategiaTarifa` → `TarifaTemporadaAlta`, `TarifaTemporadaBaja`, `TarifaCorporativa`; `Cotizador` resets after `confirmar()` |
| Comportamiento | Chain | `comportamiento.chain` | Abstract `ValidadorReserva` → `ValidadorDisponibilidad`, `ValidadorRegimen`, `ValidadorHuesped`, `ValidadorMontoMaximo`; `set_siguiente()` returns next handler for fluent chaining |

Public pattern imports use the three-level path; internal numeric checks use patrones._numeros: `from patrones.<categoria>.<patron> import <Clase>`, e.g.:
```python
from patrones.creacionales.singleton import CentralReservas
from patrones.estructurales.adapter import AdaptadorTaxi
from patrones.comportamiento.chain import ValidadorDisponibilidad
```

## Key Implementation Details

- **Singleton**: `get_instance()` simply calls `CentralReservas()` — `__new__` handles the guard. The `_initialized` flag in `__init__` prevents re-execution since Python always calls `__init__` after `__new__`. A class-level `threading.Lock` (`_lock`) makes creation (double-checked locking in `__new__`) and initialization (`__init__`) thread-safe. The first initialization prints `Conectando a la central de reservas de Hotel Los Cortez...` (hard-coded hotel name, `_hotel`/`_conectado` exposed as `hotel`/`conectado` properties); `consultar()` prints `[CentralReservas] Ejecutando: ...`.
- **Factory Method** (GoF): `CreadorHabitacion` (ABC) declares the abstract factory method `crear_habitacion(nombre, tarifa) -> Habitacion` and the operation `registrar_habitacion(nombre, tarifa)`, which calls the factory method, prints via `mostrar_info()` and returns the room without knowing its concrete class. Concrete creators decide the class: `CreadorHabitacionEstandar(camas=2)` → `HabitacionEstandar`, `CreadorSuite(vista="Vista al jardín")` → `Suite`. The creators carry the extra constructor argument (camas / vista), so existing creators are never modified to add a type. `Habitacion.__init__` raises `TypeError` for non-numeric (or bool) rates and `ValueError` for non-finite or negative rates (`"La tarifa no puede ser negativa: ..."`). `mostrar_info()` formats rates with `:.2f` and `/noche`.
- **Builder**: `Reserva` is the product (`PORCENTAJE_SEGURO = 0.03`); `ReservaEstandarBuilder` (`TIPO_SERVICIO = "Estándar"`, `COSTO_SERVICIO = 10.00`) and `ReservaPremiumBuilder` (`"Premium"`, `40.00`). `build()` always applies the builder's `TIPO_SERVICIO` and `COSTO_SERVICIO` (HU-011/HU-012), so a label set via `set_tipo_servicio()` is overwritten. `build()` resets `self._reserva = Reserva()` before returning the previous product, allowing builder reuse. `DirectorReserva.set_builder()` swaps the builder at runtime without recreating the director; `construir_reserva_basica()` has no insurance, `construir_reserva_completa()` adds the cancellation insurance. Standard and Premium builders duplicate their step implementations on purpose (HU-011/HU-012 require both to subclass `ReservaBuilder` directly). `Reserva.calcular_subtotal()` = Σ tarifa × noches (default 1 night); `calcular_total()` = subtotal + `costo_servicio` + `round(subtotal * 0.03, 2)` if the cancellation insurance is active.
- **Decorator**: `ComponenteHabitacion` defines `descripcion` and `precio` as `@property @abstractmethod` — subclasses should preserve the property contract; ABC does not enforce descriptor types. `DesayunoIncluido` adds `COSTO = 15.00` and `LateCheckout` adds `COSTO = 25.00` (fixed surcharges, descriptions `" + Desayuno incluido"` / `" + Late checkout"`). `SeguroViaje` computes 2% (`PORCENTAJE = 0.02`) of `self._componente.precio` (already-decorated price, not base) and raises `ValueError("El precio con seguro excede el rango numérico")` if the result is not finite. `round(..., 2)` rounds to two decimals without guaranteeing exact decimal arithmetic.
- **Adapter**: `AdaptadorTaxi.calcular_costo()` converts km → metros with `int(round(km * 1000))` (not truncation). `AdaptadorTaxi.estimar_minutos()` parses `"10-15 minutos"` by splitting on `"-"` and taking `[0]`; zone matching (`SistemaLegadoTaxi.ZONAS_CERCANAS = {"centro", "recoleta", "palermo", "san telmo"}`) ignores case, leading/trailing spaces and accents (module helper `_normalizar_zona`, `unicodedata` NFKD). Taxi fare = `2.50 + metros * 0.0015` for near zones, `0.0025` otherwise; the vehicle id is `TAXI-{RESERVA_ID}-{first 3 letters of normalized zone}` (e.g. `san telmo` → `SAN`). `AdaptadorShuttle` converts km → millas with `KM_A_MILLAS = 0.621` and `round(..., 3)`; shuttle fare = `4.00 + millas * 1.80`; minutes are `{"Z1": 20, "Z2": 35}` and 50 for any other code; the seat id is `SHT{RESERVA_ID}{CODIGO}`. Per spec, `zona` is a neighbourhood name for the taxi and a zone code (`"Z1"`, `"Z2"`, `"Z3"`) for the shuttle.
- **Observer — Hotel.suscribir()**: validates `isinstance(huesped, Observer)` raising `TypeError("El objeto debe ser una instancia de Observer")` (exact message from HU-024), short-circuits on duplicate without error (the list is `_huespedes`).
- **Observer — Hotel.desuscribir()**: checks `if huesped not in self._huespedes` before `remove()` to avoid `ValueError`.
- **Observer — Hotel.notificar_huespedes()**: iterates over a copy (`list(self._huespedes)`) so an observer unsubscribing inside `actualizar()` does not make the loop skip the next one. `nueva_promocion()` prints a header and notifies with `"Nueva promoción: ..."`.
- **Strategy — rates**: every `EstrategiaTarifa.aplicar(monto)` prints its detail and **returns** the final amount rounded with `round(..., 2)`. `TarifaTemporadaAlta.RECARGO = 0.30`, `TarifaTemporadaBaja.DESCUENTO = 0.20`, `TarifaCorporativa(empresa).DESCUENTO = 0.10`. All strategies print amounts with `:.2f`.
- **Strategy — Cotizador**: `set_estrategia_tarifa()` raises `TypeError` if the object is not an `EstrategiaTarifa`. `calcular_total()` sums the rooms' nightly rates (one night; no multiplication by nights) and rounds to 2 decimals. `confirmar()` guards an empty quote and `None` strategy (prints a notice and returns without raising); on success it prints the detail, applies the strategy, and clears `_habitaciones` and `_estrategia_tarifa`.
- **Chain**: `set_siguiente()` returns the handler it receives enabling fluent chaining: `a.set_siguiente(b).set_siguiente(c)`, and raises `ValueError` if the link would create a cycle. `_pasar_al_siguiente()` returns `True` at chain end (no next = approved). Validators return `False` for non-dict requests and invalid fields. `ValidadorDisponibilidad` requires a nonempty list under `"habitaciones"`; `ValidadorRegimen` accepts `REGIMENES_ACEPTADOS = {"solo alojamiento", "desayuno", "media pension", "pension completa"}` (compared with `strip().lower()`, no accents; listed with `sorted()` for deterministic output); `ValidadorHuesped` requires `LONGITUD_MINIMA = 5` characters after `strip()`; `ValidadorMontoMaximo` rejects negative, non-finite or non-numeric totals and totals above `MONTO_MAXIMO = 10000.00`, while a missing total defaults to zero (HU-039). The `reserva` dict keys: `"habitaciones"`, `"regimen"`, `"huesped"`, `"total"`.

## Code Conventions

- Classes: `CamelCase`. Methods/variables: `snake_case`. Protected attributes: `_single_underscore`.
- Abstract interfaces use `abc.ABC` + `@abstractmethod`. The only `@staticmethod` is the Singleton access point `CentralReservas.get_instance()` (plus private validation helpers inside `Reserva`/`Cotizador`); the Factory Method uses instance methods overridden by creator subclasses.
- All output is via `print()` to stdout — no real DB, network, or file I/O.
- Keep lines under ~100 chars. Use f-strings for formatting.
- All code, output, and documentation is in Spanish. Currency is `$` formatted with `:.2f`; the hotel is "Hotel Los Cortez".
- Every module, class, and method has a Google-style docstring (Args/Returns/Raises sections); properties and `__repr__` use one-line docstrings. Maintain this when adding new code.
- Type hints are present on all method signatures (`param: type`, `-> return`). Use `from typing import List, Optional, Dict, Any` for complex types (Python 3.6 compatibility).
- Domain objects expose read-only data via `@property` (Python idiom) — not Java-style `get_*()` methods. `Habitacion` exposes `nombre`/`tarifa`; `ComponenteHabitacion` exposes `descripcion`/`precio`; `Huesped` exposes `nombre`.
- Key domain classes implement `__repr__` for debugging: `HabitacionEstandar`, `Suite`, `HabitacionBasica`, `Huesped`, `Reserva`.

## Fuentes de verdad

- `historias1.md` contiene las 40 historias de usuario (9 épicas) con criterios de aceptación exactos (firmas, constantes, mensajes de salida). Es la **especificación**: ante una duda de comportamiento, consultarla antes de cambiar código. Ejemplos de reglas que parecen inconsistencias pero están especificadas: el seguro de cancelación de la `Reserva` (Builder) es 3% del subtotal y el `SeguroViaje` (Decorator) es 2% del precio decorado; el taxi recibe un barrio y el shuttle un código de zona (`"Z1"`) como `zona`.
- `README.md` está actualizado (8 patrones, rutas de 3 niveles, propiedades, salida completa real de `main.py`). Si cambia la salida de `main.py`, regenerar la sección "Salida Completa del Programa".
- Este proyecto es el **gemelo hotelero** del proyecto de e-commerce original `Python8-main` (proyecto hermano, mismo equipo): se replicó su arquitectura, convenciones, nivel de robustez y numeración de historias (HU-001..HU-040) cambiando el dominio. Equivalencias: `DatabaseConnection` → `CentralReservas`, `Producto`/`Creador*` → `Habitacion`/`Creador*`, `Pedido*` → `Reserva*`, `ProductoConcreto`/`DecoradorProducto` → `HabitacionBasica`/`DecoradorHabitacion`, `SistemaEnvio` (DHL/FedEx) → `ServicioTraslado` (Taxi/Shuttle), `Cliente`/`Tienda` → `Huesped`/`Hotel`, `EstrategiaPago`/`CarritoCompra` → `EstrategiaTarifa`/`Cotizador`, `ValidadorPedido` → `ValidadorReserva`. Ante una duda de diseño, el original sirve de referencia; no se modifica desde este repositorio.

## Extending the Project

Follow the existing idiom for each pattern category:

- **New room type**: subclass `Habitacion` (ABC in `creacionales.factory`) implementing `mostrar_info()`, plus a new creator subclassing `CreadorHabitacion` that overrides `crear_habitacion()`. Existing creators are not modified.
- **New rate policy**: subclass `EstrategiaTarifa` (ABC in `comportamiento.strategy`), implement `aplicar(monto: float) -> float` (print the detail and return the rounded final amount), inject via `set_estrategia_tarifa`.
- **New observer**: subclass `Observer` (ABC in `comportamiento.observer`), implement `actualizar(mensaje)`.
- **New reservation builder**: subclass `ReservaBuilder` (ABC in `creacionales.builder`), implement all abstract steps.
- **New room service decorator**: subclass `DecoradorHabitacion` (in `estructurales.decorator`), override the `descripcion` and `precio` properties adding surcharge on top of `self._componente.precio`.
- **New transfer provider**: create an adaptee class, then subclass `ServicioTraslado` (ABC in `estructurales.adapter`) to wrap it.
- **New validation rule**: subclass `ValidadorReserva` (ABC in `comportamiento.chain`), implement `validar(reserva)` calling `self._pasar_al_siguiente(reserva)` on success.

New patterns should be placed in the appropriate category directory (`creacionales/`, `estructurales/`, or `comportamiento/`) following the same subpackage structure. Patterns are intentionally decoupled — avoid importing across category packages except in `main.py`.

## Validation contracts after robustness fixes

- Rates and prices must be nonnegative int/float values representable as finite float; bool is rejected. Invalid types
  raise TypeError, negative or non-finite values raise ValueError.
- Cotizador requires nombre, tarifa and callable mostrar_info(); builders (Reserva) require
  nombre and tarifa. Validate before appending so rejected inputs preserve state.
- Reservation nights must be an int >= 1 (bool rejected): TypeError for other types, ValueError below 1.
- Adapter distances must be finite positive int/float values (excluding bool).
- Chain validators reject non-dict requests. Disponibilidad requires a nonempty list.
  MontoMaximo rejects non-finite totals; missing total remains zero per HU-039.
- Regression cases live in tests/test_regresiones_validacion.py.

- Cotizador and Reserva revalidate current room rates when calculating totals;
  external rooms are held by reference. Non-finite totals raise ValueError.
- patrones/_numeros.py safely rejects integers outside the float range. Adapters and
  SeguroViaje also reject arithmetic overflow with ValueError.
- tests/test_limites_numericos.py covers those limits. tests/test_documentacion.py
  compares each README Python example with its adjacent expected output, and
  compares the complete program output with main.py.

## Contratos de coherencia tras la revision

- `ReservaBuilder` incluye `reset() -> None` abstracto; cada builder concreto lo implementa.
- Cada receta del Director inicia un producto limpio y descarta parciales tras errores; la basica nunca conserva seguro previo. Los pasos manuales se acumulan hasta `build()` o `reset()`.
- Las estrategias validan entrada y resultado finitos no negativos, excluyendo bool; `Cotizador.confirmar()` valida el retorno antes de confirmar y conserva el estado ante errores.
- El shuttle normaliza el codigo de zona con `strip().upper()` tanto para minutos como para el identificador.
- El Singleton comparte una instancia por proceso; no garantiza disponibilidad ni evita reservas duplicadas.

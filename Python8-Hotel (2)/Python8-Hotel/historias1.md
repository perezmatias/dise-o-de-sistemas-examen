# Historias de Usuario - Sistema de Gestion Hotelera con Patrones de Diseño

**Proyecto:** Patrones de Diseño en Python
**Equipo:** Desarrollo Los Cortez
**Fecha:** Octubre 2026
**Versión:** 1.0 (8 patrones GoF implementados en dominio hotelero — propiedades, type hints, __repr__)

---

## Roles del Sistema

| Rol | Descripcion |
|-----|-------------|
| **Desarrollador** | Programador que construye y mantiene el sistema aplicando patrones de diseño |
| **Huesped** | Usuario final que consulta habitaciones, cotiza estadias y realiza reservas en el hotel |
| **Administrador del hotel** | Responsable de gestionar el hotel, publicar promociones y manejar suscriptores |
| **Huesped suscrito** | Huesped que se suscribio a las promociones de un hotel |
| **Estudiante / Evaluador** | Persona que estudia o evalua la implementacion de los patrones |

---

## EPICA 1: Gestion de la Central de Reservas (Patron Singleton)

> **Objetivo:** Garantizar una unica central de reservas durante toda la ejecucion, compartiendo una instancia dentro de un proceso entre recepcion, sitio web y agentes de viaje. No garantiza disponibilidad ni evita reservas duplicadas; esas garantias requieren transacciones y controles de negocio.
>
> **Patron aplicado:** Singleton
>
> **Archivos involucrados:** `patrones/creacionales/singleton/central_reservas.py`

---

### HU-001: Crear una unica instancia de la central de reservas

**Como** desarrollador del sistema,
**quiero** que la clase `CentralReservas` permita crear una sola instancia durante toda la ejecucion,
**para** compartir una instancia y evitar inicializaciones duplicadas dentro de un proceso; la integridad de las reservas requiere controles de negocio adicionales.

**Criterios de Aceptacion:**

1. La clase `CentralReservas` sobreescribe `__new__(cls) -> "CentralReservas"` para interceptar la creacion del objeto antes de que Python lo inicialice.
2. Existe una variable de clase `_instance` (inicializada en `None`) que almacena la referencia a la unica instancia.
3. Si `_instance` es `None`, se crea una nueva instancia usando `super(CentralReservas, cls).__new__(cls)` y se asigna a `_instance`.
4. Si `_instance` ya existe, `__new__()` retorna la instancia existente sin crear otra.
5. Existe una variable de clase `_lock = threading.Lock()`; `__new__()` verifica `_instance` dos veces (fuera y dentro del lock, "double-checked locking") para que varios hilos obtengan el mismo objeto.
6. Al verificar `central1 = CentralReservas()` y `central2 = CentralReservas()`, la expresion `central1 is central2` retorna `True`.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `CentralReservas` |
| Metodo clave | `__new__(cls) -> "CentralReservas"` |
| Variables de control | `_instance` (variable de clase), `_lock` (`threading.Lock`) |
| Archivo | `patrones/creacionales/singleton/central_reservas.py` |

**Definicion de Hecho:**
- [x] `__new__()` implementado y controla la creacion con double-checked locking.
- [x] `central1 is central2` retorna `True` en todos los flujos, tambien entre hilos.
- [x] No se crean objetos duplicados en memoria.

---

### HU-002: Prevenir la reinicializacion de la central

**Como** desarrollador del sistema,
**quiero** que los datos de la central no se reinicialicen aunque se invoque el constructor multiples veces,
**para** proteger la configuracion de la central y evitar perdida de estado.

**Criterios de Aceptacion:**

1. Existe un flag `_initialized: bool` que se establece en `False` al crear el objeto en `__new__()`.
2. El metodo `__init__(self) -> None` ejecuta su logica dentro de `with self._lock` y verifica `if not self._initialized` antes de configurar la central.
3. En la primera inicializacion se asignan `_hotel = "Hotel Los Cortez"` y `_conectado = True`.
4. El mensaje `"Conectando a la central de reservas de Hotel Los Cortez..."` se imprime exactamente **una vez**, sin importar cuantas instancias se soliciten.
5. Tras la primera inicializacion, `_initialized` se establece en `True` y llamadas posteriores no tienen efecto.
6. Los datos se exponen como propiedades de solo lectura: `hotel -> str` y `conectado -> bool`.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Flag de control | `_initialized: bool` |
| Atributos protegidos | `_hotel: str`, `_conectado: bool` |
| Propiedades | `hotel -> str`, `conectado -> bool` |
| Firma | `__init__(self) -> None` |
| Salida de creacion | `Conectando a la central de reservas de Hotel Los Cortez...` |
| Archivo | `patrones/creacionales/singleton/central_reservas.py` |

**Definicion de Hecho:**
- [x] Flag `_initialized` controla la inicializacion unica, protegido por el lock.
- [x] Mensaje de conexion aparece solo una vez.
- [x] `hotel` y `conectado` se leen como propiedades (no `get_*()`).

---

### HU-003: Acceder a la central mediante punto de acceso global

**Como** desarrollador del sistema,
**quiero** obtener la instancia de la central a traves del metodo estatico `get_instance()`,
**para** acceder a la central desde cualquier modulo sin instanciar directamente la clase.

**Criterios de Aceptacion:**

1. El metodo `get_instance()` esta decorado con `@staticmethod` y tiene firma `-> "CentralReservas"`.
2. Internamente delega a `CentralReservas()`, activando el mecanismo `__new__()`.
3. Llamadas consecutivas siempre retornan la misma instancia, y `get_instance()` retorna el mismo objeto que el constructor directo.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Metodo | `get_instance() -> "CentralReservas"` (estatico) |
| Implementacion | `return CentralReservas()` |
| Archivo | `patrones/creacionales/singleton/central_reservas.py` |

**Definicion de Hecho:**
- [x] Metodo estatico implementado con tipo de retorno anotado.
- [x] Delega a `__new__()` sin duplicar logica.
- [x] Siempre retorna la misma instancia.

---

### HU-004: Ejecutar consultas sobre la central unica

**Como** desarrollador del sistema,
**quiero** ejecutar consultas a traves del metodo `consultar()` de la central Singleton,
**para** simular operaciones sobre las reservas asegurando que siempre usen la misma central.

**Criterios de Aceptacion:**

1. El metodo `consultar(self, consulta: str) -> None` recibe el parametro `consulta` con type hint.
2. Imprime en consola: `"[CentralReservas] Ejecutando: {consulta}"`.
3. Se invoca sobre la instancia obtenida con `get_instance()`.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Firma | `consultar(self, consulta: str) -> None` |
| Salida esperada | `[CentralReservas] Ejecutando: Habitaciones libres del 10 al 13 de marzo` |
| Archivo | `patrones/creacionales/singleton/central_reservas.py` |

**Definicion de Hecho:**
- [x] Metodo funcional con type hints y salida por consola.
- [x] Comprobado con al menos una consulta de ejemplo.

---

## EPICA 2: Catalogo de Habitaciones (Patron Factory Method)

> **Objetivo:** Delegar en subclases creadoras la decision de que tipo de habitacion instanciar, desacoplando el codigo cliente (recepcion) de las clases concretas y permitiendo agregar tipos nuevos sin modificar el codigo existente.
>
> **Patron aplicado:** Factory Method
>
> **Archivos involucrados:** `patrones/creacionales/factory/habitacion.py`, `patrones/creacionales/factory/creador_habitacion.py`

---

### HU-005: Definir interfaz comun para todas las habitaciones

**Como** desarrollador del sistema,
**quiero** que exista una clase abstracta `Habitacion` que defina la estructura base de todas las habitaciones,
**para** garantizar que cualquier tipo de habitacion comparta una interfaz comun y exponga sus datos mediante propiedades Python.

**Criterios de Aceptacion:**

1. La clase `Habitacion` hereda de `ABC` (modulo `abc`).
2. El constructor tiene firma `__init__(self, nombre: str, tarifa: float) -> None`, donde `tarifa` es el valor por noche.
3. Declara el metodo abstracto `mostrar_info(self) -> None` decorado con `@abstractmethod`.
4. Expone `nombre` como `@property` que retorna `self._nombre` (tipo `str`).
5. Expone `tarifa` como `@property` que retorna `self._tarifa` (tipo `float`); ambas propiedades son de solo lectura.
6. Valida la tarifa en este orden: no `int`/`float` (o `bool`) lanza `TypeError("La tarifa debe ser un número")`; no finita lanza `ValueError("La tarifa debe ser un número finito")`; negativa lanza `ValueError("La tarifa no puede ser negativa: {tarifa}")`. La tarifa `0` es valida.
7. Intentar instanciar `Habitacion()` directamente lanza `TypeError`.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `Habitacion(ABC)` |
| Atributos protegidos | `_nombre: str`, `_tarifa: float` |
| Metodo abstracto | `mostrar_info(self) -> None` |
| Propiedades | `nombre -> str`, `tarifa -> float` |
| Validacion numerica | `es_finito()` de `patrones/_numeros.py` |
| Archivo | `patrones/creacionales/factory/habitacion.py` |

**Definicion de Hecho:**
- [x] Clase abstracta con ABC, `@abstractmethod` y type hints.
- [x] Propiedades `nombre` y `tarifa` retornan valores correctos y no son asignables.
- [x] Tarifas invalidas (tipo, no finita, negativa) son rechazadas con el mensaje exacto.
- [x] Instanciacion directa lanza `TypeError`.

---

### HU-006: Registrar habitaciones de tipo Estandar

**Como** huesped del hotel,
**quiero** que el sistema soporte habitaciones estandar con nombre, tarifa por noche y cantidad de camas,
**para** conocer la capacidad de cada habitacion antes de reservarla.

**Criterios de Aceptacion:**

1. La clase `HabitacionEstandar` hereda de `Habitacion` con constructor `__init__(self, nombre: str, tarifa: float, camas: int = 2) -> None`.
2. Invoca `super().__init__(nombre, tarifa)` y almacena `_camas: int` (por defecto, 2), expuesto como propiedad `camas -> int`.
3. `mostrar_info(self) -> None` imprime: `"Habitación Estándar: {nombre} | Camas: {camas} | Tarifa: ${tarifa:.2f}/noche"`.
4. Las propiedades heredadas `nombre` y `tarifa` retornan los valores correctos.
5. Implementa `__repr__(self) -> str` retornando `"HabitacionEstandar(nombre=..., tarifa=..., camas=...)"` para facilitar la depuracion.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `HabitacionEstandar(Habitacion)` |
| Atributo adicional | `_camas: int` |
| `__repr__` | `HabitacionEstandar(nombre='Doble 101', tarifa=80.0, camas=2)` |
| Salida `mostrar_info()` | `Habitación Estándar: Doble 101 \| Camas: 2 \| Tarifa: $80.00/noche` |
| Archivo | `patrones/creacionales/factory/habitacion.py` |

**Definicion de Hecho:**
- [x] Herencia correcta con `super().__init__()`.
- [x] `mostrar_info()` produce el formato exacto.
- [x] `__repr__` implementado y util para depuracion.

---

### HU-007: Registrar habitaciones de tipo Suite

**Como** huesped del hotel,
**quiero** que el sistema soporte suites con nombre, tarifa por noche y vista destacada,
**para** elegir la suite cuya vista mejor se ajuste a mi estadia antes de reservarla.

**Criterios de Aceptacion:**

1. La clase `Suite` hereda de `Habitacion` con constructor `__init__(self, nombre: str, tarifa: float, vista: str = "Vista al jardín") -> None`.
2. Invoca `super().__init__(nombre, tarifa)` y almacena `_vista: str`, expuesto como propiedad `vista -> str`.
3. `mostrar_info(self) -> None` imprime: `"Suite: {nombre} | {vista} | Tarifa: ${tarifa:.2f}/noche"`.
4. Las propiedades heredadas `nombre` y `tarifa` retornan los valores correctos.
5. Implementa `__repr__(self) -> str` retornando `"Suite(nombre=..., tarifa=..., vista=...)"`.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `Suite(Habitacion)` |
| Atributo adicional | `_vista: str` |
| `__repr__` | `Suite(nombre='Suite 501', tarifa=200.0, vista='Vista al mar')` |
| Salida `mostrar_info()` | `Suite: Suite 501 \| Vista al mar \| Tarifa: $200.00/noche` |
| Archivo | `patrones/creacionales/factory/habitacion.py` |

**Definicion de Hecho:**
- [x] Herencia correcta con `super().__init__()`.
- [x] `mostrar_info()` produce el formato exacto.
- [x] `__repr__` implementado con la vista entre comillas (`!r`).

---

### HU-008: Crear habitaciones mediante creadores (Factory Method)

**Como** desarrollador del sistema,
**quiero** que cada tipo de habitacion tenga su propio creador que decida que clase concreta instanciar,
**para** que el codigo cliente trabaje solo contra las abstracciones y agregar un tipo nuevo no obligue a modificar el codigo existente.

**Criterios de Aceptacion:**

1. `CreadorHabitacion` hereda de `ABC` y declara el factory method abstracto `crear_habitacion(self, nombre: str, tarifa: float) -> Habitacion`.
2. `CreadorHabitacion` implementa `registrar_habitacion(self, nombre: str, tarifa: float) -> Habitacion`, que invoca `crear_habitacion()`, llama a `mostrar_info()` sobre el resultado y lo retorna, sin conocer la clase concreta.
3. `CreadorHabitacionEstandar(CreadorHabitacion)` recibe `camas: int = 2` en su constructor y su `crear_habitacion()` retorna una `HabitacionEstandar`.
4. `CreadorSuite(CreadorHabitacion)` recibe `vista: str = "Vista al jardín"` en su constructor y su `crear_habitacion()` retorna una `Suite`.
5. No es posible instanciar `CreadorHabitacion` ni una subclase que no implemente `crear_habitacion()` (lanza `TypeError`).
6. Agregar un tipo de habitacion nuevo requiere solo una subclase de `Habitacion` y una de `CreadorHabitacion`, sin modificar las existentes.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Creador abstracto | `CreadorHabitacion(ABC)` |
| Factory method | `crear_habitacion(nombre, tarifa) -> Habitacion` (`@abstractmethod`) |
| Operacion del creador | `registrar_habitacion(nombre, tarifa) -> Habitacion` |
| Creadores concretos | `CreadorHabitacionEstandar(camas)`, `CreadorSuite(vista)` |
| Archivo | `patrones/creacionales/factory/creador_habitacion.py` |

**Definicion de Hecho:**
- [x] Cada creador concreto retorna su habitacion concreta con type hints.
- [x] `registrar_habitacion()` funciona con cualquier creador, incluso uno nuevo.
- [x] Instanciacion directa del creador abstracto lanza `TypeError`.

---

## EPICA 3: Construccion de Reservas Complejas (Patron Builder)

> **Objetivo:** Construir reservas con multiples opciones configurables (habitaciones, noches, huesped, tipo de servicio, seguro de cancelacion) paso a paso, sin requerir un constructor con multiples parametros ni combinaciones de subclases.
>
> **Patron aplicado:** Builder
>
> **Archivos involucrados:** `patrones/creacionales/builder/reserva.py`, `patrones/creacionales/builder/reserva_builder.py`

---

### HU-009: Representar la reserva como objeto complejo

**Como** desarrollador del sistema,
**quiero** que exista una clase `Reserva` que agrupe todos los datos de una reserva,
**para** tener un objeto resultado bien definido que el builder construya paso a paso.

**Criterios de Aceptacion:**

1. `Reserva` se inicializa con `__init__(self) -> None` con todos los atributos en estado neutro.
2. Atributos anotados: `_habitaciones: List[Any]`, `_noches: int` (1), `_huesped: str` (`""`), `_tipo_servicio: str` (`""`), `_costo_servicio: float` (0.0), `_seguro_cancelacion: bool` (`False`).
3. Constante de clase: `PORCENTAJE_SEGURO = 0.03` (3% del subtotal de habitaciones).
4. Los mutadores validan **antes** de modificar el estado:
   - `agregar_habitacion(habitacion)` exige las propiedades `nombre` y `tarifa` (duck typing); si falta alguna lanza `TypeError("La habitación debe exponer nombre y tarifa")`; tarifa no `int`/`float` (o `bool`) lanza `TypeError("La tarifa debe ser un número")`; tarifa negativa o no finita lanza `ValueError("La tarifa debe ser finita y no negativa")`.
   - `set_noches(noches: int)` exige un `int` mayor o igual que 1: no `int` (o `bool`) lanza `TypeError("Las noches deben ser un número entero")`; menor que 1 lanza `ValueError("Las noches deben ser al menos 1")`.
   - `set_huesped(nombre: str)` lanza `TypeError("El huésped debe ser un texto")` si no es `str`.
   - `set_tipo_servicio(tipo: str, costo: float)`: costo no numerico (o `bool`) lanza `TypeError("El costo del servicio debe ser un número")`; negativo o no finito lanza `ValueError("El costo del servicio debe ser finito y no negativo")`.
   - `set_seguro_cancelacion(activo: bool)` activa o desactiva el seguro.
5. Expone propiedades de solo lectura: `habitaciones` (retorna una copia de la lista), `noches`, `huesped`, `tipo_servicio`, `costo_servicio` y `seguro_cancelacion`.
6. `calcular_subtotal(self) -> float` suma `tarifa × noches` de cada habitacion (via propiedad `tarifa`, revalidada), redondeado a 2 decimales; si el parcial o el subtotal no son finitos lanza `ValueError("El subtotal de la reserva excede el rango numérico")`.
7. `calcular_total(self) -> float` retorna subtotal mas `costo_servicio` mas, si hay seguro, `round(subtotal * PORCENTAJE_SEGURO, 2)`, redondeado a 2 decimales; si no es finito lanza `ValueError("El total de la reserva excede el rango numérico")`.
8. `mostrar_resumen(self) -> None` imprime, en este orden: `=== RESUMEN DE LA RESERVA ===`, `Huésped: {huesped}`, `Noches: {noches}`, `Habitaciones:`, una linea `  - {nombre} | ${tarifa:.2f}/noche` por habitacion, `Servicio: {tipo} (${costo:.2f})`, `Seguro de cancelación: Sí (+${costo_seguro:.2f})` o `Seguro de cancelación: No`, `Subtotal: ${subtotal:.2f}`, `TOTAL: ${total:.2f}` y `=============================` (29 signos "=").
9. `__repr__(self) -> str` retorna representacion tecnica con huesped, lista de nombres de habitaciones, noches, servicio y total.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `Reserva` |
| Imports | `from typing import Any, List` |
| Seguro de cancelacion | `PORCENTAJE_SEGURO = 0.03` (3% del subtotal) |
| Acceso a habitaciones | Via propiedad `h.tarifa` y `h.nombre` (duck typing) |
| `__repr__` | `Reserva(huesped='Ana Pérez', habitaciones=['Doble 101'], noches=2, servicio='Estándar', total=170.00)` |
| Ejemplo | Doble 101 a $80.00 × 2 noches + servicio Estandar $10.00 = `TOTAL: $170.00` |
| Archivo | `patrones/creacionales/builder/reserva.py` |

**Definicion de Hecho:**
- [x] Atributos con type annotations (`List`, `Any`).
- [x] `calcular_subtotal()` usa `h.tarifa` (propiedad, no getter) y revalida cada tarifa.
- [x] Mutadores invalidos no alteran el estado de la reserva.
- [x] `__repr__` implementado para depuracion.

---

### HU-010: Definir interfaz abstracta del builder

**Como** desarrollador del sistema,
**quiero** una clase abstracta `ReservaBuilder` que defina los pasos de construccion de la reserva,
**para** garantizar que todos los builders concretos implementen los mismos pasos.

**Criterios de Aceptacion:**

1. `ReservaBuilder` hereda de `ABC` y declara 7 metodos abstractos con `@abstractmethod`.
2. Metodos: `agregar_habitacion(habitacion)`, `set_noches(noches: int)`, `set_huesped(nombre: str)`, `set_tipo_servicio(tipo: str)`, `agregar_seguro_cancelacion()`, `build() -> Reserva` y `reset() -> None`.
3. Los cinco primeros pasos devuelven `"ReservaBuilder"` (el propio builder) para permitir interfaz fluida.
4. La docstring de `agregar_habitacion` especifica duck typing: objeto con propiedades `nombre` y `tarifa`.
5. No es posible instanciar `ReservaBuilder` directamente.
6. `reset(self) -> None` descarta el producto parcial e inicia una reserva vacia sin seguro; no altera productos ya entregados.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `ReservaBuilder(ABC)` |
| Metodos abstractos | 6 pasos de construccion y reset() |
| Interfaz fluida | Cinco pasos retornan `"ReservaBuilder"`; `build()` retorna `Reserva` |
| Duck typing | habitaciones con propiedades `nombre` y `tarifa` |
| Archivo | `patrones/creacionales/builder/reserva_builder.py` |

**Definicion de Hecho:**
- [x] 7 metodos abstractos con `@abstractmethod`, incluido `reset()`.
- [x] Instanciacion directa lanza `TypeError`.

---

### HU-011: Construir reservas con servicio estandar

**Como** huesped del hotel,
**quiero** crear reservas con servicio Estandar (costo $10.00),
**para** elegir la opcion mas economica cuando no necesito atencion especial durante la estadia.

**Criterios de Aceptacion:**

1. `ReservaEstandarBuilder` implementa todos los pasos abstractos de `ReservaBuilder`.
2. Constantes de clase: `COSTO_SERVICIO = 10.00`, `TIPO_SERVICIO = "Estándar"`.
3. `agregar_habitacion(habitacion)` valida y agrega la habitacion y luego imprime `"  Habitación agregada: {habitacion.nombre} (${habitacion.tarifa:.2f}/noche)"` accediendo via **propiedades**; si la validacion falla no imprime nada ni altera la reserva.
4. `set_tipo_servicio(tipo)` asigna la etiqueta recibida con `COSTO_SERVICIO`; `agregar_seguro_cancelacion()` activa el seguro; `set_noches()` y `set_huesped()` delegan en la `Reserva` y sus validaciones.
5. `build(self) -> Reserva` aplica **siempre** `TIPO_SERVICIO` y `COSTO_SERVICIO` (la etiqueta puesta con `set_tipo_servicio()` se reemplaza), guarda la reserva terminada, hace `self._reserva = Reserva()` y retorna la anterior para permitir reutilizacion.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `ReservaEstandarBuilder(ReservaBuilder)` |
| Costo servicio | `COSTO_SERVICIO = 10.00` |
| Tipo servicio | `TIPO_SERVICIO = "Estándar"` |
| Reset en build | `self._reserva = Reserva()` antes de retornar la reserva terminada |
| Acceso a habitacion | `habitacion.nombre`, `habitacion.tarifa` (propiedades) |
| Archivo | `patrones/creacionales/builder/reserva_builder.py` |

**Definicion de Hecho:**
- [x] Implementa todos los pasos abstractos.
- [x] `build()` aplica las constantes y resetea la reserva interna para reutilizacion.
- [x] Accede a habitaciones via propiedades (no getters).

---

### HU-012: Construir reservas con servicio premium

**Como** huesped del hotel,
**quiero** crear reservas con servicio Premium (costo $40.00),
**para** priorizar atencion y comodidad durante mi estadia.

**Criterios de Aceptacion:**

1. `ReservaPremiumBuilder` implementa todos los pasos abstractos con las mismas firmas que `ReservaEstandarBuilder`.
2. Constantes de clase: `COSTO_SERVICIO = 40.00`, `TIPO_SERVICIO = "Premium"`.
3. `build(self) -> Reserva` aplica las constantes premium y resetea `self._reserva = Reserva()`.
4. El comportamiento de `agregar_habitacion`, `set_noches`, `set_huesped` y `agregar_seguro_cancelacion` es identico al builder estandar (ambos subclasean directamente a `ReservaBuilder` y duplican los pasos a proposito).

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `ReservaPremiumBuilder(ReservaBuilder)` |
| Costo servicio | `COSTO_SERVICIO = 40.00` |
| Tipo servicio | `"Premium"` |
| Archivo | `patrones/creacionales/builder/reserva_builder.py` |

**Definicion de Hecho:**
- [x] Constantes premium correctas.
- [x] `build()` resetea correctamente el builder.

---

### HU-013: Orquestar la construccion de reservas con el Director

**Como** desarrollador del sistema,
**quiero** un `DirectorReserva` que defina secuencias de construccion predefinidas,
**para** que el codigo cliente no tenga que invocar cada paso manualmente.

**Criterios de Aceptacion:**

1. `DirectorReserva` tiene constructor `__init__(self, builder: "ReservaBuilder") -> None`.
2. `set_builder(self, builder: "ReservaBuilder") -> None` permite cambiar el builder en tiempo de ejecucion sin recrear el director.
3. `construir_reserva_basica(self, habitacion, noches: int, huesped: str) -> Reserva` agrega una habitacion, setea noches y huesped, y llama `build()`; no activa el seguro de cancelacion.
4. `construir_reserva_completa(self, habitaciones: List, noches: int, huesped: str) -> Reserva` itera las habitaciones, setea noches y huesped, ademas activa el seguro de cancelacion y llama `build()`.
5. Si tiene exito, devuelve una instancia de `Reserva` completamente configurada.
6. Cada receta inicia el builder con `reset()`, sin habitaciones ni seguro previos.
7. Si un paso falla, propaga el error y descarta el producto parcial con `reset()`. Reintentar no duplica habitaciones. La reserva basica siempre se entrega sin seguro.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `DirectorReserva` |
| Import | `from typing import Any, List` |
| Tipos de construccion | `construir_reserva_basica`, `construir_reserva_completa` |
| Ejemplo basico | Doble 101 ($80.00) × 3 noches, Estandar: `TOTAL: $250.00` |
| Ejemplo completo | Suite 501 + Suite 301 × 2 noches, Premium con seguro: `TOTAL: $761.00` |
| Patron | Director orquesta; builder ensambla; cliente elige builder |
| Archivo | `patrones/creacionales/builder/reserva_builder.py` |

**Definicion de Hecho:**
- [x] `set_builder()` permite cambiar builder sin recrear director.
- [x] Reserva basica: una habitacion, sin seguro de cancelacion.
- [x] Reserva completa: todas las habitaciones con seguro de cancelacion activado.

---

## EPICA 4: Servicios Opcionales en Habitaciones (Patron Decorator)

> **Objetivo:** Agregar responsabilidades opcionales (desayuno incluido, seguro de viaje, late checkout) a una habitacion en tiempo de ejecucion, sin crear una subclase por cada combinacion posible.
>
> **Patron aplicado:** Decorator
>
> **Archivos involucrados:** `patrones/estructurales/decorator/decorador_habitacion.py`

---

### HU-014: Definir interfaz abstracta de componente con propiedades

**Como** desarrollador del sistema,
**quiero** una interfaz abstracta `ComponenteHabitacion` que defina `descripcion` y `precio` como propiedades abstractas,
**para** que tanto el componente base como todos los decoradores sean intercambiables y usen el idioma Python de propiedades.

**Criterios de Aceptacion:**

1. `ComponenteHabitacion` hereda de `ABC`.
2. Declara `descripcion` como `@property @abstractmethod` con retorno `-> str`.
3. Declara `precio` como `@property @abstractmethod` con retorno `-> float` (precio por noche con todos los decoradores aplicados).
4. Toda subclase debe conservar el contrato de ambas propiedades. `@abstractmethod` exige sobrescribir los miembros abstractos, pero no verifica que la sobrescritura siga siendo una propiedad.
5. No es posible instanciar `ComponenteHabitacion` directamente.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `ComponenteHabitacion(ABC)` |
| Propiedades abstractas | `descripcion -> str`, `precio -> float` |
| Idioma | `@property @abstractmethod` (no metodos `get_*`) |
| Archivo | `patrones/estructurales/decorator/decorador_habitacion.py` |

**Definicion de Hecho:**
- [x] Dos propiedades abstractas declaradas con `@property @abstractmethod`.
- [x] Instanciacion directa lanza `TypeError`.

---

### HU-015: Implementar componente base concreto

**Como** desarrollador del sistema,
**quiero** una clase `HabitacionBasica` que sea el punto de partida de la cadena de decoradores,
**para** tener un componente base que devuelva nombre y precio originales sin ningun cargo adicional.

**Criterios de Aceptacion:**

1. `HabitacionBasica` hereda de `ComponenteHabitacion` con constructor `__init__(self, nombre: str, precio: float) -> None`.
2. Propiedad `descripcion -> str` retorna `self._nombre`.
3. Propiedad `precio -> float` retorna `self._precio`.
4. Valida el precio en este orden: no `int`/`float` (o `bool`) lanza `TypeError("El precio debe ser un número")`; no finito lanza `ValueError("El precio debe ser finito")`; negativo lanza `ValueError("El precio no puede ser negativo: {precio}")`.
5. Implementa `__repr__(self) -> str` retornando `"HabitacionBasica('nombre', precio)"`.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `HabitacionBasica(ComponenteHabitacion)` |
| `__repr__` | `HabitacionBasica('Doble 101', 80.0)` |
| Validacion numerica | `es_finito()` de `patrones/_numeros.py` |
| Archivo | `patrones/estructurales/decorator/decorador_habitacion.py` |

**Definicion de Hecho:**
- [x] Implementa ambas propiedades abstractas.
- [x] Precios invalidos son rechazados con el mensaje exacto.
- [x] `__repr__` implementado para depuracion.

---

### HU-016: Crear decorador base con delegacion

**Como** desarrollador del sistema,
**quiero** una clase `DecoradorHabitacion` que envuelva un `ComponenteHabitacion` y delegue a el por defecto,
**para** que los decoradores concretos solo sobreescriban lo que modifican, sin duplicar logica.

**Criterios de Aceptacion:**

1. `DecoradorHabitacion` hereda de `ComponenteHabitacion` con constructor `__init__(self, componente: ComponenteHabitacion) -> None`.
2. Propiedad `descripcion -> str` delega a `self._componente.descripcion`.
3. Propiedad `precio -> float` delega a `self._componente.precio`.
4. Las subclases solo necesitan sobreescribir la propiedad que modifican. La base es instanciable porque implementa ambas propiedades abstractas.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `DecoradorHabitacion(ComponenteHabitacion)` |
| Delegacion | `self._componente.descripcion` / `self._componente.precio` |
| Archivo | `patrones/estructurales/decorator/decorador_habitacion.py` |

**Definicion de Hecho:**
- [x] Delegacion implementada en ambas propiedades.
- [x] Subclases solo sobreescriben lo que cambian.

---

### HU-017: Agregar servicios opcionales apilables a la habitacion

**Como** huesped del hotel,
**quiero** agregar desayuno incluido, seguro de viaje y late checkout a mi habitacion de forma independiente y combinable,
**para** personalizar mi estadia sin que el sistema necesite una clase separada por cada combinacion.

**Criterios de Aceptacion:**

1. `DesayunoIncluido(DecoradorHabitacion)` — constante `COSTO = 15.00`. Propiedad `precio -> float` retorna `round(self._componente.precio + self.COSTO, 2)`. Agrega `" + Desayuno incluido"` a la descripcion.
2. `SeguroViaje(DecoradorHabitacion)` — constante `PORCENTAJE = 0.02`. Propiedad `precio -> float` retorna `round(self._componente.precio * (1 + self.PORCENTAJE), 2)`; si el resultado no es finito lanza `ValueError("El precio con seguro excede el rango numérico")`. El 2% se calcula sobre el **precio ya decorado** (no el base). Agrega `" + Seguro de viaje"`.
3. `LateCheckout(DecoradorHabitacion)` — constante `COSTO = 25.00`. Propiedad `precio -> float` retorna `round(self._componente.precio + self.COSTO, 2)`. Agrega `" + Late checkout"` a la descripcion.
4. Se pueden apilar los 3 decoradores en cualquier orden sobre la misma habitacion.
5. `round(..., 2)` se usa en todos los decoradores para precision monetaria.
6. El `SeguroViaje` (2% del precio decorado) es independiente del seguro de cancelacion de la `Reserva` del Builder (3% del subtotal, HU-009): son reglas distintas por especificacion.

**Datos Tecnicos:**

| Decorador | Cargo | Calculo |
|-----------|-------|---------|
| `DesayunoIncluido` | +$15.00 fijo | `componente.precio + 15.00` |
| `SeguroViaje` | +2% variable | `componente.precio * 1.02` |
| `LateCheckout` | +$25.00 fijo | `componente.precio + 25.00` |

| Elemento | Detalle |
|----------|---------|
| Archivo | `patrones/estructurales/decorator/decorador_habitacion.py` |
| Ejemplo apilado | Base $899.99 → +desayuno → +seguro → +late checkout = $958.29 |
| Orden relevante | Con base $85.00: desayuno luego seguro = $102.00; seguro luego desayuno = $101.70 |

**Definicion de Hecho:**
- [x] Tres decoradores concretos con `@property` para `descripcion` y `precio`.
- [x] `SeguroViaje` aplica el porcentaje sobre el precio ya decorado.
- [x] `round()` aplicado en los tres decoradores para precision monetaria.

---

## EPICA 5: Integracion de Servicios de Traslado (Patron Adapter)

> **Objetivo:** Integrar los servicios de traslado aeropuerto-hotel de un proveedor de taxis y uno de shuttle, que tienen APIs propietarias incompatibles, bajo una interfaz unificada para que el codigo cliente use siempre los mismos metodos.
>
> **Patron aplicado:** Adapter (Object Adapter)
>
> **Archivos involucrados:** `patrones/estructurales/adapter/adaptador_traslado.py`

---

### HU-018: Definir interfaz unificada de traslado

**Como** desarrollador del sistema,
**quiero** una interfaz abstracta `ServicioTraslado` que todos los adaptadores implementen,
**para** que el codigo de recepcion pueda calcular costos y crear traslados sin saber que proveedor esta usando.

**Criterios de Aceptacion:**

1. `ServicioTraslado` hereda de `ABC` y declara 3 metodos abstractos con type hints.
2. `calcular_costo(self, distancia_km: float, zona: str) -> float` — retorna costo en dolares.
3. `estimar_minutos(self, zona: str) -> int` — retorna minutos estimados de espera o viaje.
4. `crear_traslado(self, reserva_id: str, zona: str) -> str` — retorna el identificador del movil o asiento asignado.
5. No es posible instanciar `ServicioTraslado` directamente.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `ServicioTraslado(ABC)` |
| Metodos | 3 abstractos con type hints completos |
| Archivo | `patrones/estructurales/adapter/adaptador_traslado.py` |

**Definicion de Hecho:**
- [x] 3 metodos abstractos con firmas tipadas.
- [x] Instanciacion directa lanza `TypeError`.

---

### HU-019: Integrar el sistema de taxis

**Como** administrador del hotel,
**quiero** usar el sistema de taxis a traves del adaptador `AdaptadorTaxi` con la misma interfaz que cualquier proveedor,
**para** calcular tarifas y asignar moviles sin que el codigo cliente conozca la API propietaria del taxi.

**Criterios de Aceptacion:**

1. `SistemaLegadoTaxi` representa la API original del taxi con sus metodos propietarios:
   - `calcular_tarifa_taxi(metros: int, zona: str) -> float` (usa metros, no kilometros): `round(2.50 + metros * por_metro, 2)`, con `por_metro = 0.0015` para zonas cercanas y `0.0025` para las demas; si el resultado o `metros` no son finitos lanza `ValueError("La tarifa excede el rango numérico")`.
   - `tiempo_espera_taxi(zona: str) -> str` (retorna `"10-15 minutos"` para zonas cercanas y `"25-40 minutos"` para las demas, como cadena).
   - `asignar_movil(reserva_id: str, zona: str) -> str` (imprime `"[Taxi] Móvil asignado para {reserva_id} hacia {zona}"` y retorna `"TAXI-{RESERVA_ID}-{ZONA3}"`, con el id en mayusculas y las 3 primeras letras de la zona normalizada en mayusculas).
2. `SistemaLegadoTaxi.ZONAS_CERCANAS = {"centro", "recoleta", "palermo", "san telmo"}`; la comparacion ignora mayusculas, espacios externos y tildes (funcion `_normalizar_zona` con `unicodedata`), por ejemplo `"  PALERMÓ "` equivale a `"palermo"`.
3. `AdaptadorTaxi` hereda de `ServicioTraslado` e implementa los 3 metodos:
   - `calcular_costo`: valida la distancia, convierte `int(round(distancia_km * 1000))` → metros (redondea, no trunca) y delega a `calcular_tarifa_taxi`.
   - `estimar_minutos`: parsea `"10-15 minutos"` con `.split("-")[0]` → retorna `int`.
   - `crear_traslado`: delega directamente a `asignar_movil`.
4. Validacion de la distancia: tipo no `int`/`float` (o `bool`) lanza `TypeError("La distancia debe ser un número")`; no finita o menor o igual que cero lanza `ValueError("La distancia debe ser finita y mayor que cero")`; conversion a metros no finita lanza `ValueError("La conversión de la distancia excede el rango numérico")`.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Adaptado | `SistemaLegadoTaxi` |
| Conversion | km × 1000 → metros (con `round`) |
| Parseo tiempo | `"10-15 minutos".split("-")[0]` → `10` |
| Ejemplo | 2.5 km a "Palermo" (cercana): $6.25 y 10 minutos; a "Belgrano": $8.75 y 25 minutos |
| Redondeo vs truncado | 0.0039 km → 3.9 m → 4 m: tarifa $2.51 en Palermo (truncar a 3 m daria $2.50) |
| Identificador | `TAXI-RES-001-PAL`; zona `"  Núñez "` produce el sufijo `NUN` |
| Archivo | `patrones/estructurales/adapter/adaptador_traslado.py` |

**Definicion de Hecho:**
- [x] Conversion de km a metros correcta, con `round` (no `int()` directo).
- [x] Parseo de string de tiempo retorna el minimo como `int`.
- [x] Zonas se comparan sin distinguir mayusculas, espacios externos ni tildes.

---

### HU-020: Integrar el sistema de shuttle

**Como** administrador del hotel,
**quiero** usar el sistema de shuttle a traves del adaptador `AdaptadorShuttle` con la misma interfaz que el taxi,
**para** cambiar o comparar proveedores de traslado sin modificar el codigo de recepcion.

**Criterios de Aceptacion:**

1. `SistemaLegadoShuttle` representa la API del shuttle con metodos propietarios tipados:
   - `obtener_precio_shuttle(millas: float, codigo_zona: str) -> float`: `round(4.00 + millas * 1.80, 2)`.
   - `minutos_estimados(codigo_zona: str) -> int`: `{"Z1": 20, "Z2": 35}` y `50` para cualquier otro codigo; el codigo se normaliza con `strip().upper()`.
   - `reservar_asiento(reserva_id: str, codigo_zona: str) -> str`: imprime `"[Shuttle] Asiento reservado para {reserva_id} ({codigo_zona})"` y retorna `"SHT{RESERVA_ID}{CODIGO}"` (ambos en mayusculas; el codigo se normaliza con `strip().upper()`, igual que al estimar minutos).
2. `AdaptadorShuttle` hereda de `ServicioTraslado` con constante de clase `KM_A_MILLAS = 0.621`.
3. `calcular_costo`: valida la distancia (mismas reglas y mensajes que `AdaptadorTaxi`), convierte `round(distancia_km * 0.621, 3)` → millas y delega a `obtener_precio_shuttle`; si el costo no es finito lanza `ValueError("La tarifa excede el rango numérico")`.
4. `estimar_minutos`: delega directamente a `minutos_estimados`.
5. `crear_traslado`: delega directamente a `reservar_asiento`.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Adaptado | `SistemaLegadoShuttle` |
| Constante | `KM_A_MILLAS = 0.621` (como constante de clase) |
| Conversion | `distancia_km * 0.621` → millas |
| Ejemplo | 2.5 km a "Z1": $6.79 y 20 minutos; 10 km a "Z2": $15.18 y 35 minutos |
| Identificador | `SHTRES-001Z1` para la reserva `RES-001` y la zona `Z1` |
| Archivo | `patrones/estructurales/adapter/adaptador_traslado.py` |

**Definicion de Hecho:**
- [x] Constante de conversion definida como atributo de clase.
- [x] Conversion km → millas correcta con `round(..., 3)`.
- [x] Codigos de zona desconocidos estiman 50 minutos.

---

### HU-021: Usar los adaptadores de forma transparente

**Como** desarrollador del sistema,
**quiero** que el codigo cliente use `AdaptadorTaxi` y `AdaptadorShuttle` a traves de la interfaz `ServicioTraslado` sin saber cual proveedor esta detras,
**para** demostrar que el patron Adapter desacopla el hotel de los sistemas de traslado externos.

**Criterios de Aceptacion:**

1. Una funcion cliente recibe un `ServicioTraslado` generico y llama a `calcular_costo`, `estimar_minutos` y `crear_traslado` indistintamente.
2. El mismo codigo funciona con `AdaptadorTaxi()` y con `AdaptadorShuttle()` sin cambios.
3. El taxi recibe el nombre de un barrio como zona; el shuttle recibe un codigo de zona (`"Z1"`, `"Z2"`, `"Z3"`) — el adaptador gestiona la diferencia.
4. Ambos adaptadores se demuestran en `main.py` en la seccion del Patron Adapter.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Demostracion en `main.py` | Seccion `>>> 7. PATRÓN ADAPTER <<<` |
| Funcion cliente | `cotizar_y_crear_traslado(servicio: ServicioTraslado, nombre_proveedor: str, distancia_km: float, zona: str, reserva_id: str) -> None` (anidada en `main()`) |
| Entrada taxi | `distancia_km=2.5, zona="Palermo", reserva_id="RES-001"` |
| Entrada shuttle | `distancia_km=2.5, zona="Z1", reserva_id="RES-001"` |
| Archivo | `patrones/estructurales/adapter/adaptador_traslado.py` |

**Definicion de Hecho:**
- [x] Misma funcion cliente opera sobre ambos adaptadores.
- [x] Ambos proveedores demostrados en `main.py`.

---

## EPICA 6: Sistema de Promociones (Patron Observer)

> **Objetivo:** Implementar un mecanismo de suscripcion/publicacion donde el hotel notifique automaticamente a todos los huespedes suscritos sobre nuevas promociones.
>
> **Patron aplicado:** Observer (Publicador/Suscriptor)
>
> **Archivos involucrados:** `patrones/comportamiento/observer/observer.py`, `patrones/comportamiento/observer/hotel.py`

---

### HU-022: Definir contrato para observadores

**Como** desarrollador del sistema,
**quiero** que exista una interfaz abstracta `Observer` con el metodo `actualizar(mensaje: str) -> None`,
**para** establecer un contrato estandar con type hints que cualquier tipo de suscriptor debe cumplir.

**Criterios de Aceptacion:**

1. La clase `Observer` hereda de `ABC`.
2. Declara `actualizar(self, mensaje: str) -> None` con `@abstractmethod` y type hints.
3. No es posible instanciar `Observer` directamente (lanza `TypeError`).
4. Cualquier clase que herede de `Observer` debe implementar `actualizar()`.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `Observer(ABC)` |
| Firma abstracta | `actualizar(self, mensaje: str) -> None` |
| Archivo | `patrones/comportamiento/observer/observer.py` |

**Definicion de Hecho:**
- [x] Interfaz abstracta con type hints implementada.
- [x] Instanciacion directa lanza `TypeError`.

---

### HU-023: Crear huespedes que reciben notificaciones

**Como** huesped del hotel,
**quiero** registrarme como observador con mi nombre y recibir notificaciones personalizadas,
**para** estar informado de las promociones que me interesan.

**Criterios de Aceptacion:**

1. `Huesped` hereda de `Observer` con constructor `__init__(self, nombre: str) -> None`.
2. Implementa `actualizar(self, mensaje: str) -> None` imprimiendo: `"Huésped {nombre} recibió notificación: {mensaje}"`.
3. Expone `nombre` como `@property -> str` que retorna `self._nombre`.
4. Implementa `__repr__(self) -> str` retornando `"Huesped('nombre')"` para depuracion.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `Huesped(Observer)` |
| Propiedad | `nombre -> str` |
| `__repr__` | `Huesped('Ana Pérez')` |
| Salida notificacion | `Huésped Ana Pérez recibió notificación: Nueva promoción: 20% de descuento en suites` |
| Archivo | `patrones/comportamiento/observer/observer.py` |

**Definicion de Hecho:**
- [x] Implementa `actualizar()` con nombre personalizado.
- [x] Propiedad `nombre` expuesta (no getter `get_nombre()`).
- [x] `__repr__` implementado.

---

### HU-024: Suscribir huespedes al hotel con validaciones

**Como** administrador del hotel,
**quiero** que los huespedes puedan suscribirse al sistema de notificaciones con validacion de tipo y sin duplicados,
**para** mantener una lista de suscriptores limpia y evitar errores en tiempo de notificacion.

**Criterios de Aceptacion:**

1. `Hotel` tiene constructor `__init__(self, nombre: str) -> None`, mantiene la lista `_huespedes: List[Observer]` y expone `nombre` como propiedad de solo lectura.
2. `suscribir(self, huesped: Observer) -> None` valida `isinstance(huesped, Observer)`.
3. Si **no es** `Observer`, lanza `TypeError` con mensaje: `"El objeto debe ser una instancia de Observer"`.
4. Si **ya esta suscrito**, imprime `"Huésped ya está suscrito al hotel {nombre}"` sin agregarlo nuevamente ni lanzar error.
5. Si pasa ambas validaciones, agrega e imprime `"Huésped suscrito al hotel {nombre}"`.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `Hotel` |
| Import | `from typing import List` |
| Firma | `suscribir(self, huesped: Observer) -> None` |
| Validacion 1 | `isinstance(huesped, Observer)` → `TypeError` |
| Validacion 2 | `huesped in self._huespedes` → rechazo silencioso (solo imprime) |
| Salida | `Huésped suscrito al hotel Hotel Los Cortez` |
| Archivo | `patrones/comportamiento/observer/hotel.py` |

**Definicion de Hecho:**
- [x] Valida tipo `Observer` con type hint en la firma.
- [x] Rechaza duplicados con mensaje informativo.

---

### HU-025: Desuscribir huespedes del hotel de forma segura

**Como** huesped suscrito,
**quiero** cancelar mi suscripcion a las notificaciones sin que el sistema falle,
**para** dejar de recibir alertas cuando ya no me interesen las promociones.

**Criterios de Aceptacion:**

1. `desuscribir(self, huesped: Observer) -> None` verifica existencia antes de eliminar.
2. Si **no esta suscrito**, imprime `"Huésped no está suscrito al hotel {nombre}"` sin lanzar excepcion.
3. Si **esta suscrito**, elimina con `list.remove()` e imprime `"Huésped desuscrito del hotel {nombre}"`.
4. Tras desuscribirse, el huesped no recibe notificaciones posteriores.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Firma | `desuscribir(self, huesped: Observer) -> None` |
| Verificacion | `if huesped not in self._huespedes` (evita `ValueError`) |
| Archivo | `patrones/comportamiento/observer/hotel.py` |

**Definicion de Hecho:**
- [x] No lanza `ValueError` al desuscribir un huesped no suscrito.
- [x] Huesped desuscrito no recibe mas notificaciones.

---

### HU-026: Publicar promociones y notificar automaticamente a suscriptores

**Como** administrador del hotel,
**quiero** publicar una nueva promocion y que todos los huespedes suscritos sean notificados automaticamente,
**para** maximizar el alcance de las promociones sin contactar a cada huesped individualmente.

**Criterios de Aceptacion:**

1. `nueva_promocion(self, descripcion: str) -> None` imprime `"¡Nueva promoción en {nombre_hotel}!"` (precedido de un salto de linea) y delega a `notificar_huespedes()` con el mensaje `"Nueva promoción: {descripcion}"`.
2. `notificar_huespedes(self, mensaje: str) -> None` imprime `"--- Notificando a {N} huéspedes ---"` (precedido de un salto de linea) y llama `actualizar(mensaje)` en cada suscriptor.
3. Recorre una copia de la lista (`list(self._huespedes)`), de modo que un observador que se desuscribe dentro de `actualizar()` no hace que se saltee al siguiente.
4. Si hay 3 suscritos, los 3 reciben la notificacion. Si uno se desuscribio, solo 2 la reciben.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Firmas | `nueva_promocion(self, descripcion: str) -> None`, `notificar_huespedes(self, mensaje: str) -> None` |
| Iteracion | `for huesped in list(self._huespedes): huesped.actualizar(mensaje)` |
| Archivo | `patrones/comportamiento/observer/hotel.py` |

**Definicion de Hecho:**
- [x] Todos los suscritos reciben la notificacion.
- [x] Conteo de huespedes notificados es correcto.
- [x] Desuscripcion durante la notificacion no saltea a otros huespedes.

---

## EPICA 7: Cotizacion de Estadias y Politicas de Tarifa (Patron Strategy)

> **Objetivo:** Permitir que los huespedes acumulen habitaciones en una cotizacion y seleccionen dinamicamente entre diferentes politicas de tarifa (temporada alta, temporada baja, convenio corporativo) al momento de confirmar, sin que el cotizador conozca los detalles internos de cada politica.
>
> **Patron aplicado:** Strategy
>
> **Archivos involucrados:** `patrones/comportamiento/strategy/estrategia_tarifa.py`, `patrones/comportamiento/strategy/cotizador.py`

---

### HU-027: Definir interfaz de estrategia de tarifa

**Como** desarrollador del sistema,
**quiero** una interfaz abstracta `EstrategiaTarifa` que defina el contrato para todas las politicas de tarifa,
**para** poder agregar nuevas politicas en el futuro sin modificar el cotizador ni el flujo de confirmacion.

**Criterios de Aceptacion:**

1. `EstrategiaTarifa` hereda de `ABC` y declara `aplicar(self, monto: float) -> float` con `@abstractmethod` y type hints.
2. El contrato de `aplicar()` es imprimir el detalle del calculo **y devolver** el monto final redondeado a 2 decimales.
3. No es posible instanciar `EstrategiaTarifa` directamente.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `EstrategiaTarifa(ABC)` |
| Firma abstracta | `aplicar(self, monto: float) -> float` |
| Archivo | `patrones/comportamiento/strategy/estrategia_tarifa.py` |

**Definicion de Hecho:**
- [x] Interfaz abstracta con type hints implementada.
- [x] Instanciacion directa lanza `TypeError`.

---

### HU-028: Aplicar recargo de temporada alta del 30%

**Como** huesped del hotel,
**quiero** cotizar mi estadia con la politica de temporada alta y ver el recargo del 30% aplicado,
**para** conocer el monto exacto que pagare en fechas de mayor demanda.

**Criterios de Aceptacion:**

1. `TarifaTemporadaAlta(EstrategiaTarifa)` sin atributos propios y con constante de clase `RECARGO = 0.30`.
2. `aplicar(self, monto: float) -> float` calcula `round(monto * (1 + self.RECARGO), 2)` usando `round()` para precision monetaria y retorna el resultado.
3. Imprime: `"[Temporada Alta] Recargo del 30% sobre ${monto:.2f}: total ${final:.2f}"`, donde el porcentaje sale de `f"{RECARGO:.0%}"`.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `TarifaTemporadaAlta(EstrategiaTarifa)` |
| Constante | `RECARGO = 0.30` |
| Calculo | `round(monto * 1.30, 2)` |
| Salida | `[Temporada Alta] Recargo del 30% sobre $280.00: total $364.00` |
| Redondeo | `0.1 + 0.2` produce `$0.30` y total `$0.39` (no `0.39000000000000001`) |
| Archivo | `patrones/comportamiento/strategy/estrategia_tarifa.py` |

**Definicion de Hecho:**
- [x] `round()` aplicado para precision monetaria.
- [x] Imprime monto base y total con recargo, y retorna el total.

---

### HU-029: Aplicar descuento de temporada baja del 20%

**Como** huesped del hotel,
**quiero** cotizar mi estadia con la politica de temporada baja y recibir automaticamente un descuento del 20%,
**para** obtener un beneficio economico por viajar en fechas de menor demanda.

**Criterios de Aceptacion:**

1. `TarifaTemporadaBaja(EstrategiaTarifa)` con constante de clase `DESCUENTO = 0.20`.
2. `aplicar(self, monto: float) -> float` calcula `round(monto * (1 - self.DESCUENTO), 2)` y retorna el resultado.
3. Imprime: `"[Temporada Baja] Descuento del 20% sobre ${monto:.2f}: total ${final:.2f}"`.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `TarifaTemporadaBaja(EstrategiaTarifa)` |
| Constante | `DESCUENTO = 0.20` |
| Calculo | `round(monto * 0.80, 2)` (redondea a dos decimales) |
| Salida | `[Temporada Baja] Descuento del 20% sobre $135.50: total $108.40` |
| Archivo | `patrones/comportamiento/strategy/estrategia_tarifa.py` |

**Definicion de Hecho:**
- [x] `round()` aplicado para precision monetaria.
- [x] Muestra monto base y total con descuento.

---

### HU-030: Aplicar tarifa corporativa del 10% para empresas con convenio

**Como** huesped del hotel,
**quiero** cotizar mi estadia con la tarifa corporativa de mi empresa y recibir un descuento del 10%,
**para** aprovechar el convenio vigente entre mi empresa y el hotel.

**Criterios de Aceptacion:**

1. `TarifaCorporativa(EstrategiaTarifa)` con constructor `__init__(self, empresa: str) -> None` y constante de clase `DESCUENTO = 0.10`.
2. `aplicar(self, monto: float) -> float` calcula `round(monto * (1 - self.DESCUENTO), 2)` y retorna el resultado.
3. Imprime: `"[Corporativa - {empresa}] Descuento del 10% sobre ${monto:.2f}: total ${final:.2f}"`.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `TarifaCorporativa(EstrategiaTarifa)` |
| Atributo | `_empresa: str` |
| Constante | `DESCUENTO = 0.10` |
| Salida | `[Corporativa - Acme S.A.] Descuento del 10% sobre $350.00: total $315.00` |
| Archivo | `patrones/comportamiento/strategy/estrategia_tarifa.py` |

**Definicion de Hecho:**
- [x] Nombre de la empresa se muestra correctamente.
- [x] Type hints en constructor y `aplicar()`.

---

### HU-031: Agregar habitaciones a la cotizacion

**Como** huesped del hotel,
**quiero** agregar habitaciones de cualquier tipo a mi cotizacion,
**para** acumular las habitaciones que deseo reservar antes de confirmar.

**Criterios de Aceptacion:**

1. `Cotizador` se inicializa con `_habitaciones = []` y `_estrategia_tarifa = None`.
2. `agregar_habitacion(self, habitacion) -> None` anade la habitacion a la lista.
3. Imprime: `"Habitación agregada a la cotización: {habitacion.nombre}"` accediendo via **propiedad** (no `get_nombre()`), una vez agregada.
4. Acepta cualquier objeto con `nombre`, `tarifa` y metodo invocable `mostrar_info()` (duck typing), coherente con HU-034.
5. Antes de agregar, valida el contrato y que la tarifa sea `int` o `float` finita y no negativa, excluyendo `bool`: sin `mostrar_info()` invocable lanza `TypeError("La habitación debe implementar mostrar_info()")`; sin `nombre` o `tarifa` lanza `TypeError("La habitación debe exponer nombre y tarifa")`; tarifa de tipo incorrecto lanza `TypeError("La tarifa debe ser un número")`; tarifa negativa o no finita lanza `ValueError("La tarifa debe ser finita y no negativa")`. Las habitaciones anteriores se conservan.
6. Expone `habitaciones` (copia de la lista) y `estrategia_tarifa` (estrategia activa o `None`) como propiedades de solo lectura.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Acceso al nombre | `habitacion.nombre` (propiedad, no `get_nombre()`) |
| Firma | `agregar_habitacion(self, habitacion) -> None` |
| Imports | `from typing import Any, List, Optional` |
| Archivo | `patrones/comportamiento/strategy/cotizador.py` |

**Definicion de Hecho:**
- [x] Usa `habitacion.nombre` via propiedad.
- [x] Acepta `HabitacionEstandar`, `Suite` u otras habitaciones con propiedad `nombre`.
- [x] Una habitacion invalida no altera la cotizacion.

---

### HU-032: Seleccionar politica de tarifa dinamicamente

**Como** huesped del hotel,
**quiero** elegir o cambiar la politica de tarifa en cualquier momento antes de confirmar,
**para** tener flexibilidad sin necesidad de crear una nueva cotizacion.

**Criterios de Aceptacion:**

1. `set_estrategia_tarifa(self, estrategia_tarifa: EstrategiaTarifa) -> None` establece la estrategia activa.
2. Se puede cambiar en cualquier momento antes de `confirmar()`; gana la ultima configurada.
3. Acepta cualquier objeto que herede de `EstrategiaTarifa`; en caso contrario lanza `TypeError("La estrategia debe ser una instancia de EstrategiaTarifa, se recibió {tipo}")`, donde `{tipo}` es el nombre del tipo recibido.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Firma | `set_estrategia_tarifa(self, estrategia_tarifa: EstrategiaTarifa) -> None` |
| Principio | Inyeccion de dependencia en tiempo de ejecucion |
| Archivo | `patrones/comportamiento/strategy/cotizador.py` |

**Definicion de Hecho:**
- [x] Estrategia se puede establecer y cambiar.
- [x] Confirmar usa la ultima estrategia configurada.
- [x] Un objeto que no es `EstrategiaTarifa` es rechazado con `TypeError`.

---

### HU-033: Calcular el subtotal de la cotizacion automaticamente

**Como** huesped del hotel,
**quiero** que el sistema calcule automaticamente el subtotal de las habitaciones cotizadas,
**para** conocer el monto base exacto antes de aplicar la politica de tarifa.

**Criterios de Aceptacion:**

1. `calcular_total(self) -> float` recorre las habitaciones, revalida cada **propiedad** `tarifa`, acumula y redondea a dos decimales. Rechaza tarifas invalidas y totales no finitos antes de aplicar la politica de tarifa.
2. Con cotizacion vacia retorna `0.0`.
3. Funciona correctamente con 1 o multiples habitaciones: suma una tarifa por habitacion (no multiplica por noches).
4. Un total que desborda el rango de `float` lanza `ValueError("El total de la cotización excede el rango numérico")`.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Firma | `calcular_total(self) -> float` |
| Implementacion | Acumulación de tarifas revalidadas y `round(total, 2)` |
| Acceso tarifa | Via propiedad `tarifa` (no `get_tarifa()`) |
| Redondeo | `0.1 + 0.2` produce `0.3` (no `0.30000000000000004`) |
| Archivo | `patrones/comportamiento/strategy/cotizador.py` |

**Definicion de Hecho:**
- [x] Usa propiedad `tarifa` en la suma.
- [x] Cotizacion vacia retorna `0.0`.

---

### HU-034: Confirmar la cotizacion con resumen, tarifa y vaciado

**Como** huesped del hotel,
**quiero** confirmar mi cotizacion con un resumen que muestre las habitaciones, aplique la politica de tarifa y vacie el cotizador,
**para** completar la cotizacion de forma clara y que el cotizador quede listo para una nueva consulta.

**Criterios de Aceptacion:**

1. `confirmar(self) -> None` con dos validaciones previas: cotizacion vacia (imprime `"La cotización está vacía"` y retorna) y `_estrategia_tarifa is None` (imprime `"Debe seleccionar una estrategia de tarifa"` y retorna), sin lanzar excepcion.
2. Calcula el subtotal con `calcular_total()` **antes** de imprimir nada; si falla, no se imprime el resumen y la cotizacion se conserva.
3. Muestra `"=== COTIZACIÓN ==="` (precedido de un salto de linea), `"Habitaciones cotizadas:"`, lista las habitaciones con `mostrar_info()` y muestra `"Subtotal: ${subtotal:.2f}"`.
4. Delega el calculo final a `self._estrategia_tarifa.aplicar(subtotal)`.
5. Imprime `"¡Cotización confirmada!"` (seguido de una linea en blanco) y resetea `_habitaciones = []` y `_estrategia_tarifa = None`.
6. Si la estrategia lanza una excepcion o devuelve un resultado invalido, la cotizacion y la estrategia se conservan para reintentar, sin imprimir el mensaje de exito.
7. Antes de confirmar, valida el retorno: debe ser int/float finito no negativo y distinto de bool. Tipo invalido produce TypeError; negativo, no finito o fuera de rango produce ValueError.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Firma | `confirmar(self) -> None` |
| Post-confirmacion | Vaciado de `_habitaciones` y `_estrategia_tarifa` |
| Ejemplo | Doble 101 ($80.00) + Suite 501 ($200.00), temporada alta: subtotal `$280.00`, total `$364.00` |
| Archivo | `patrones/comportamiento/strategy/cotizador.py` |

**Definicion de Hecho:**
- [x] Ambas validaciones funcionan.
- [x] Cotizador se vacia despues de confirmar con exito.
- [x] Una falla previa a la estrategia o de la propia estrategia conserva el estado.

---

## EPICA 8: Validacion de Reservas en Cadena (Patron Chain of Responsibility)

> **Objetivo:** Validar una reserva a traves de multiples controles independientes (disponibilidad, regimen de comidas, huesped, monto maximo) de forma encadenada, donde cada validador decide si aprueba y delega al siguiente, o rechaza y detiene la cadena.
>
> **Patron aplicado:** Chain of Responsibility
>
> **Archivos involucrados:** `patrones/comportamiento/chain/validador_reserva.py`

---

### HU-035: Definir interfaz abstracta del validador

**Como** desarrollador del sistema,
**quiero** una clase abstracta `ValidadorReserva` con soporte de encadenamiento fluido,
**para** poder construir la cadena de validacion con la sintaxis `a.set_siguiente(b).set_siguiente(c)`.

**Criterios de Aceptacion:**

1. `ValidadorReserva(ABC)` con constructor `__init__(self) -> None` e inicializa `_siguiente = None`.
2. `set_siguiente(self, validador: "ValidadorReserva") -> "ValidadorReserva"` asigna `_siguiente` y **retorna el validador recibido** para permitir encadenamiento fluido.
3. `set_siguiente()` lanza `ValueError("No se puede enlazar el validador: formaría un ciclo")` si enlazar el validador recibido formaria un ciclo (incluido el auto-enlace).
4. `_pasar_al_siguiente(self, reserva: Dict[str, Any]) -> bool` retorna `True` si no hay siguiente (fin de cadena = aprobada) o delega al siguiente con `self._siguiente.validar(reserva)`.
5. Declara `validar(self, reserva: Dict[str, Any]) -> bool` como `@abstractmethod`.
6. La `reserva` es un `dict` con claves: `"habitaciones"`, `"regimen"`, `"huesped"`, `"total"`.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `ValidadorReserva(ABC)` |
| Import | `from typing import Any, Dict, Optional` |
| Encadenamiento | `set_siguiente()` retorna el handler recibido |
| Fin de cadena | `_pasar_al_siguiente` retorna `True` si no hay siguiente |
| Archivo | `patrones/comportamiento/chain/validador_reserva.py` |

**Definicion de Hecho:**
- [x] `set_siguiente()` retorna el validador (habilita encadenamiento fluido) y rechaza ciclos.
- [x] `_pasar_al_siguiente()` retorna `True` al final de la cadena.
- [x] Type hints `Dict[str, Any]` en todos los metodos.

---

### HU-036: Validar que la reserva incluye habitaciones

**Como** administrador del hotel,
**quiero** que el primer validador de la cadena verifique que la reserva incluye al menos una habitacion,
**para** rechazar reservas vacias antes de revisar regimen u otras validaciones.

**Criterios de Aceptacion:**

1. `ValidadorDisponibilidad(ValidadorReserva)` implementa `validar(self, reserva: Dict[str, Any]) -> bool`.
2. Requiere una reserva de tipo `dict` (si no, imprime `"  [Reserva] RECHAZADO: se requiere un diccionario."` y retorna `False`) y una lista no vacía en `habitaciones`; rechaza campos ausentes, `None` y otros tipos devolviendo `False`.
3. Si esta vacia, imprime `"  [Disponibilidad] RECHAZADO: la reserva no incluye habitaciones."` y retorna `False`.
4. Si tiene habitaciones, imprime `"  [Disponibilidad] OK: {N} habitación(es) solicitada(s)."` y llama a `self._pasar_al_siguiente(reserva)`.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Clase | `ValidadorDisponibilidad(ValidadorReserva)` |
| Validacion | `reserva.get("habitaciones") or []`, debe ser `list` no vacia |
| Archivo | `patrones/comportamiento/chain/validador_reserva.py` |

**Definicion de Hecho:**
- [x] Rechaza reservas sin habitaciones.
- [x] Delega al siguiente si hay habitaciones.

---

### HU-037: Validar el regimen de comidas de la reserva

**Como** administrador del hotel,
**quiero** que el sistema rechace reservas con regimenes de comidas que el hotel no ofrece,
**para** asegurar que solo se procesen reservas con regimenes disponibles.

**Criterios de Aceptacion:**

1. `ValidadorRegimen(ValidadorReserva)` tiene constante `REGIMENES_ACEPTADOS = {"solo alojamiento", "desayuno", "media pension", "pension completa"}`.
2. Normaliza con `.strip().lower()` y verifica `regimen not in self.REGIMENES_ACEPTADOS`; un regimen ausente o que no es `str` se trata como cadena vacia y se rechaza.
3. Si invalido, imprime `"  [Régimen] RECHAZADO: régimen '{regimen}' no está disponible. Aceptados: {lista}."` con la lista generada por `sorted()` (orden determinista: `desayuno, media pension, pension completa, solo alojamiento`) y retorna `False`.
4. Si valido, imprime `"  [Régimen] OK: régimen '{regimen}' aceptado."` y delega al siguiente.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Constante | `REGIMENES_ACEPTADOS = {"solo alojamiento", "desayuno", "media pension", "pension completa"}` |
| Normalizacion | `.strip().lower()` (case-insensitive) |
| Archivo | `patrones/comportamiento/chain/validador_reserva.py` |

**Definicion de Hecho:**
- [x] Constante como `set` para busqueda O(1).
- [x] Comparacion case-insensitive y sin espacios externos.
- [x] Lista de aceptados con orden determinista (`sorted()`).

---

### HU-038: Validar el nombre del huesped titular

**Como** administrador del hotel,
**quiero** que el sistema rechace reservas con nombres de huesped incompletos,
**para** asegurar que cada reserva pueda identificar correctamente al titular en el check-in.

**Criterios de Aceptacion:**

1. `ValidadorHuesped(ValidadorReserva)` tiene constante `LONGITUD_MINIMA = 5`.
2. Aplica `.strip()` y verifica `len(huesped) < LONGITUD_MINIMA`; un huesped ausente o que no es `str` se trata como cadena vacia y se rechaza.
3. Si invalido, imprime `"  [Huésped] RECHAZADO: nombre incompleto (mínimo {N} caracteres)."` y retorna `False`.
4. Si valido, imprime `"  [Huésped] OK: '{huesped}'."` (con el nombre ya sin espacios externos) y delega al siguiente.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Constante | `LONGITUD_MINIMA = 5` |
| Normalizacion | `.strip()` elimina espacios externos |
| Archivo | `patrones/comportamiento/chain/validador_reserva.py` |

**Definicion de Hecho:**
- [x] Constante configurable para el minimo de caracteres.
- [x] `.strip()` antes de la validacion.

---

### HU-039: Validar que el monto no supere el limite permitido

**Como** administrador del hotel,
**quiero** que el ultimo validador de la cadena rechace reservas con montos sospechosamente altos,
**para** prevenir posibles errores o fraudes antes de confirmar la reserva.

**Criterios de Aceptacion:**

1. `ValidadorMontoMaximo(ValidadorReserva)` tiene constante `MONTO_MAXIMO = 10000.00`.
2. Obtiene el total con `reserva.get("total", 0)`: ausente equivale a cero. Rechaza tipos distintos de `int`/`float` (imprime `"  [Monto] RECHAZADO: total inválido ({total!r})."`), booleanos, valores no finitos (`"  [Monto] RECHAZADO: el total debe ser finito."`) y negativos (`"  [Monto] RECHAZADO: total negativo ${total:.2f}."`) devolviendo `False`.
3. Si `total > MONTO_MAXIMO`, imprime `"  [Monto] RECHAZADO: total ${total:.2f} supera el límite de ${MONTO_MAXIMO:.2f}."` y retorna `False`; un total exactamente igual a `10000.00` se acepta.
4. Si dentro del limite, imprime `"  [Monto] OK: total ${total:.2f} dentro del límite permitido."` y llama `_pasar_al_siguiente(reserva)`.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Constante | `MONTO_MAXIMO = 10000.00` |
| Formato salida | `:.2f` para valores monetarios |
| Posicion en cadena | Ultimo eslabon recomendado |
| Archivo | `patrones/comportamiento/chain/validador_reserva.py` |

**Definicion de Hecho:**
- [x] Constante configurable para el limite maximo.
- [x] Rechaza montos superiores a $10000.00.

---

## EPICA 9: Demostracion Integral del Sistema (8 Patrones)

> **Objetivo:** Integrar los 8 patrones en un programa principal ejecutable que demuestre el funcionamiento completo del sistema de gestion hotelera con inter-operacion entre patrones.
>
> **Archivo involucrado:** `main.py`

---

### HU-040: Ejecutar demostracion completa de los 8 patrones

**Como** estudiante o evaluador del sistema,
**quiero** ejecutar un unico archivo `main.py` que demuestre los 8 patrones en secuencia con secciones claramente delimitadas,
**para** observar el funcionamiento integral del sistema y comprender cada patron en un contexto practico de gestion hotelera.

**Criterios de Aceptacion:**

1. Se ejecuta con `python main.py` sin errores ni excepciones.
2. Muestra encabezado y pie con separadores `"=" * 50`: el encabezado contiene `DEMOSTRACIÓN DE PATRONES DE DISEÑO EN PYTHON` y el subtitulo `SISTEMA DE GESTIÓN HOTELERA`; el pie contiene `FIN DE LA DEMOSTRACIÓN`.
3. Estructura del archivo: primera linea `#!/usr/bin/env python3`, docstring con la lista numerada `N. Nombre` de los 8 patrones, e imports organizados en 3 bloques por categoria (creacionales, estructurales, comportamiento). Cada seccion se anuncia con `>>> N. PATRÓN X <<<` y los numeros coinciden con los del docstring.
4. **Seccion 1 Singleton:** Obtiene dos instancias con `CentralReservas.get_instance()`, verifica `central1 is central2` y obtiene `True`, ejecuta `consultar("Habitaciones libres del 10 al 13 de marzo")`.
5. **Seccion 2 Factory Method:** Crea 2 habitaciones estandar (`Doble 101` con 2 camas y `Simple 102` con 1 cama) y 2 suites (`Suite 501` con vista al mar y `Suite 301` con la vista por defecto) via `CreadorHabitacionEstandar` y `CreadorSuite` (`registrar_habitacion()`). Demuestra propiedades `nombre` y `tarifa`.
6. **Seccion 3 Observer:** Hotel "Hotel Los Cortez" con 3 huespedes suscritos que reciben la primera promocion; uno se desuscribe; 2 reciben la segunda promocion.
7. **Seccion 4 Strategy:** 3 cotizadores con politicas de tarifa diferentes (temporada alta, temporada baja, corporativa "Acme S.A."); cada uno confirma su cotizacion completa. Habitaciones reutilizadas del paso Factory.
8. **Seccion 5 Builder:** Reserva basica con `ReservaEstandarBuilder` (Doble 101, 3 noches); reserva completa con `ReservaPremiumBuilder` (dos suites, 2 noches, seguro de cancelacion). Un unico Director orquesta ambas via `set_builder()`. Habitaciones reutilizadas del paso Factory.
9. **Seccion 6 Decorator:** Habitacion base "Suite Presidencial" apilada con `DesayunoIncluido` → `SeguroViaje` → `LateCheckout`; se muestra `descripcion` y `precio` acumulados via propiedades en cada paso.
10. **Seccion 7 Adapter:** Misma funcion cliente cotiza y crea traslados con `AdaptadorTaxi` y `AdaptadorShuttle` usando la interfaz `ServicioTraslado`.
11. **Seccion 8 Chain:** Cadena `ValidadorDisponibilidad → ValidadorRegimen → ValidadorHuesped → ValidadorMontoMaximo` evaluada con 3 casos: reserva valida (APROBADA), regimen de comidas no ofrecido (RECHAZADA en ValidadorRegimen), monto excesivo (RECHAZADA en ValidadorMontoMaximo).
12. No requiere dependencias externas. Compatible con Python 3.6+.

**Datos Tecnicos:**

| Elemento | Detalle |
|----------|---------|
| Archivo | `main.py` |
| Ejecucion | `python main.py` |
| Secciones | 8 patrones + encabezado/pie |
| Orden de las secciones | Singleton, Factory Method, Observer, Strategy, Builder, Decorator, Adapter, Chain of Responsibility |
| Reutilizacion inter-patron | `doble`, `simple`, `suite_mar`, `suite_jardin` usados en Factory, Strategy, Builder |
| Imports | Organizados en 3 bloques: creacionales, estructurales, comportamiento |
| Resultados clave | Strategy: $364.00 / $108.40 / $315.00; Builder: TOTAL $250.00 y $761.00; Decorator: $958.29 |
| Dependencias | Solo biblioteca estandar de Python (`abc`, `typing`, `threading`, `unicodedata`, `math`) |

**Definicion de Hecho:**
- [x] Ejecucion completa sin errores.
- [x] Los 8 patrones se demuestran en orden.
- [x] Habitaciones del Factory reutilizadas en Strategy y Builder.
- [x] Decorator usa propiedades `.descripcion` y `.precio` (no `.get_descripcion()` / `.get_precio()`).

---

## Contrato numerico de las estrategias

Las tres estrategias incluidas validan el monto antes de calcular y el resultado antes de imprimir.
Aceptan int/float finitos no negativos, incluido cero, excluyendo bool. Un tipo invalido
produce TypeError; un negativo, no finito o entero fuera del rango float produce ValueError.
El recargo de temporada alta tambien rechaza el desbordamiento de una entrada finita.
El cotizador comprueba el retorno de cualquier estrategia, incluidas las extensiones.

## Limites numericos y referencias externas

Las tarifas, precios y distancias deben ser representables como float finito. Los
enteros que exceden ese rango se rechazan con `ValueError` (o `False` en el
validador de monto maximo). Las conversiones de traslado (km a metros), la tarifa
del taxi y del shuttle, el subtotal y el total de la reserva, el total de la
cotizacion y el precio con seguro de viaje se comprueban tambien despues del
calculo: una entrada finita no garantiza que la suma o multiplicacion resulte finita.

Reserva y Cotizador almacenan referencias, no copias de las habitaciones. Revalidan
las tarifas al calcular; si una habitacion externa cambia a un valor invalido, se
rechaza el calculo. El cotizador conserva sus habitaciones y estrategia ante ese error.

`patrones/_numeros.py` centraliza la comprobacion del rango, sin imports entre
categorias. Los ejemplos `>>>` de las docstrings se ejecutan con `tests/test_doctests.py`, y
`tests/test_documentacion.py` ejecuta cada ejemplo Python del README y compara su salida
con el resultado esperado publicado junto al ejemplo. Tambien compara la seccion
"Salida Completa del Programa" con la salida real de `main.py`.

## Precisiones de validacion (revision de robustez)

- HU-005/HU-015: tarifas y precios `int`/`float` finitos no negativos; `bool` no es una tarifa.
- HU-009/HU-010/HU-011/HU-012: la reserva y los builders comprueban nombre/tarifa antes de
  agregar y conservan la reserva si la entrada es invalida. Las noches exigen un `int`
  mayor o igual que 1 (`bool` no vale). Admiten habitaciones por duck typing.
- HU-019/HU-020: los adaptadores requieren una distancia `int`/`float` finita mayor que
  cero; tipos incorrectos (incluido bool) producen `TypeError`; valores invalidos, `ValueError`.
- HU-031/HU-034: el contrato incluye `mostrar_info()`; un error previo a la politica de tarifa
  o de la propia estrategia conserva habitaciones y estrategia para reintentar.
- HU-035 a HU-039: entradas que no son diccionarios se rechazan con `False`.
- `round()` redondea resultados, pero no garantiza representacion decimal exacta.

## Matriz de Trazabilidad

### Historias de Usuario por Archivo

| Archivo | Historias Relacionadas |
|---------|----------------------|
| `patrones/creacionales/singleton/central_reservas.py` | HU-001, HU-002, HU-003, HU-004 |
| `patrones/creacionales/factory/habitacion.py` | HU-005, HU-006, HU-007 |
| `patrones/creacionales/factory/creador_habitacion.py` | HU-008 |
| `patrones/creacionales/builder/reserva.py` | HU-009 |
| `patrones/creacionales/builder/reserva_builder.py` | HU-010, HU-011, HU-012, HU-013 |
| `patrones/estructurales/decorator/decorador_habitacion.py` | HU-014, HU-015, HU-016, HU-017 |
| `patrones/estructurales/adapter/adaptador_traslado.py` | HU-018, HU-019, HU-020, HU-021 |
| `patrones/comportamiento/observer/observer.py` | HU-022, HU-023 |
| `patrones/comportamiento/observer/hotel.py` | HU-024, HU-025, HU-026 |
| `patrones/comportamiento/strategy/estrategia_tarifa.py` | HU-027, HU-028, HU-029, HU-030 |
| `patrones/comportamiento/strategy/cotizador.py` | HU-031, HU-032, HU-033, HU-034 |
| `patrones/comportamiento/chain/validador_reserva.py` | HU-035, HU-036, HU-037, HU-038, HU-039 |
| `main.py` | HU-040 |

### Historias de Usuario por Patron y Epica

| Patron GoF | Categoria | Epica | Historias | Cantidad |
|------------|-----------|-------|-----------|----------|
| Singleton | Creacional | Epica 1 | HU-001 a HU-004 | 4 |
| Factory Method | Creacional | Epica 2 | HU-005 a HU-008 | 4 |
| Builder | Creacional | Epica 3 | HU-009 a HU-013 | 5 |
| Decorator | Estructural | Epica 4 | HU-014 a HU-017 | 4 |
| Adapter | Estructural | Epica 5 | HU-018 a HU-021 | 4 |
| Observer | Comportamiento | Epica 6 | HU-022 a HU-026 | 5 |
| Strategy | Comportamiento | Epica 7 | HU-027 a HU-034 | 8 |
| Chain | Comportamiento | Epica 8 | HU-035 a HU-039 | 5 |
| Demo integral | Transversal | Epica 9 | HU-040 | 1 |
| **Total** | | | | **40** |

### Historias por Rol

| Rol | Historias | Cantidad |
|-----|-----------|----------|
| Desarrollador | HU-001, HU-002, HU-003, HU-004, HU-005, HU-008, HU-009, HU-010, HU-013, HU-014, HU-015, HU-016, HU-018, HU-021, HU-022, HU-027, HU-035 | 17 |
| Huesped | HU-006, HU-007, HU-011, HU-012, HU-017, HU-028, HU-029, HU-030, HU-031, HU-032, HU-033, HU-034 | 12 |
| Administrador del hotel | HU-019, HU-020, HU-024, HU-026, HU-036, HU-037, HU-038, HU-039 | 8 |
| Huesped (del hotel / suscrito) | HU-023, HU-025 | 2 |
| Estudiante / Evaluador | HU-040 | 1 |
| **Total** | | **40** |

### Mejoras tecnicas reflejadas en esta version

| Mejora | Historias impactadas | Descripcion |
|--------|---------------------|-------------|
| `@property` | HU-002, HU-005, HU-006, HU-007, HU-009, HU-014, HU-015, HU-023, HU-024, HU-031 | `hotel`, `conectado`, `nombre`, `tarifa`, `camas`, `vista`, `descripcion`, `precio` y las lecturas de `Reserva` y `Cotizador` expuestas como propiedades Python |
| Type hints | Todas las HUs | Firmas con `param: tipo` y `-> retorno` en todos los metodos |
| `__repr__` | HU-006, HU-007, HU-009, HU-015, HU-023 | `HabitacionEstandar`, `Suite`, `Reserva`, `HabitacionBasica`, `Huesped` |
| 3-level paths | Todas las HUs | `patrones/<categoria>/<patron>/archivo.py` |
| Thread-safety | HU-001, HU-002 | `threading.Lock` de clase con double-checked locking en `__new__` y lock en `__init__` |
| Validacion de tarifas | HU-005, HU-015 | `Habitacion` y `HabitacionBasica` requieren int/float finito no negativo; excluyen bool. Tipo invalido: `TypeError`; valor negativo/no finito: `ValueError` |
| Formato monetario | HU-006, HU-007, HU-028, HU-029, HU-030, HU-034 | Montos impresos con 2 decimales (`:.2f`); `calcular_total()` del cotizador y las estrategias redondean a 2 decimales |
| Normalizacion de zonas | HU-019 | El taxi compara zonas sin distinguir mayusculas, espacios externos ni tildes (`unicodedata`) |
| Notificacion segura | HU-026 | `notificar_huespedes()` recorre una copia de la lista: desuscribirse durante la notificacion no saltea a otros |
| Validacion de estrategia | HU-032 | `set_estrategia_tarifa()` lanza `TypeError` si el objeto no es `EstrategiaTarifa` |
| Cadena robusta | HU-035 a HU-039 | `set_siguiente()` rechaza ciclos (`ValueError`); los validadores rechazan reservas que no son dict y campos invalidos; Disponibilidad exige lista no vacia; Monto maximo rechaza totales no finitos o negativos, pero total ausente equivale a cero por HU-039; `ValidadorRegimen` lista los regimenes con `sorted()` |
| Suite de tests | Todas las HUs | `python -m unittest discover -s tests -t .`: tests por patron, criterios de HU-040, convenciones y doctests |

---

*Documento generado a partir del analisis del codigo fuente implementado.*
*Las marcas de cumplimiento describen la implementación; no sustituyen la ejecución de pruebas en cada versión objetivo de Python.*
*Version 1.0 — refleja la arquitectura gemela con 8 patrones GoF organizados en 3 categorias, en dominio hotelero.*

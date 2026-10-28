"""Tests del patrón Factory Method (Habitacion, creadores abstracto y concretos)."""

import unittest

import patrones.creacionales.factory as paquete_factory
from patrones.creacionales.factory import (
    CreadorHabitacion,
    CreadorHabitacionEstandar,
    CreadorSuite,
    Habitacion,
    HabitacionEstandar,
    Suite,
)
from tests.utilidades import capturar_salida


class Penthouse(Habitacion):
    """Habitación nueva definida solo en el test para verificar la extensibilidad."""

    def mostrar_info(self) -> None:
        print(f"Penthouse: {self._nombre} | Tarifa: ${self._tarifa:.2f}/noche")


class CreadorPenthouse(CreadorHabitacion):
    """Creador concreto nuevo: extiende el sistema sin modificar el existente."""

    def crear_habitacion(self, nombre: str, tarifa: float) -> Penthouse:
        return Penthouse(nombre, tarifa)


class TestCreadorHabitacion(unittest.TestCase):
    """Verifica el creador abstracto y su operación basada en el factory method."""

    def test_creador_abstracto_no_se_puede_instanciar(self) -> None:
        with self.assertRaises(TypeError):
            CreadorHabitacion()

    def test_subclase_sin_factory_method_no_se_puede_instanciar(self) -> None:
        class CreadorIncompleto(CreadorHabitacion):
            pass

        with self.assertRaises(TypeError):
            CreadorIncompleto()

    def test_registrar_habitacion_crea_muestra_y_devuelve_la_habitacion(self) -> None:
        habitacion, salida = capturar_salida(
            lambda: CreadorHabitacionEstandar(1).registrar_habitacion("Simple 102", 55.5)
        )
        self.assertIsInstance(habitacion, HabitacionEstandar)
        self.assertEqual(
            salida.strip(),
            "Habitación Estándar: Simple 102 | Camas: 1 | Tarifa: $55.50/noche",
        )

    def test_registrar_habitacion_con_suite_muestra_su_formato(self) -> None:
        habitacion, salida = capturar_salida(
            lambda: CreadorSuite("Vista al mar").registrar_habitacion("Suite Nupcial", 250)
        )
        self.assertIsInstance(habitacion, Suite)
        self.assertEqual(
            salida.strip(), "Suite: Suite Nupcial | Vista al mar | Tarifa: $250.00/noche"
        )

    def test_registrar_habitacion_funciona_con_creadores_nuevos_sin_cambios(self) -> None:
        habitacion, salida = capturar_salida(
            lambda: CreadorPenthouse().registrar_habitacion("PH 1", 500.0)
        )
        self.assertIsInstance(habitacion, Penthouse)
        self.assertEqual(salida.strip(), "Penthouse: PH 1 | Tarifa: $500.00/noche")

    def test_cada_creador_concreto_decide_la_clase_de_la_habitacion(self) -> None:
        creadores = [CreadorHabitacionEstandar(), CreadorSuite()]
        tipos = [type(creador.crear_habitacion("X", 1.0)) for creador in creadores]
        self.assertEqual(tipos, [HabitacionEstandar, Suite])

    def test_la_simple_factory_anterior_ya_no_existe(self) -> None:
        self.assertFalse(hasattr(paquete_factory, "HabitacionFactory"))

    def test_el_paquete_reexporta_toda_la_api_publica(self) -> None:
        self.assertEqual(
            sorted(paquete_factory.__all__),
            sorted([
                "Habitacion", "HabitacionEstandar", "Suite",
                "CreadorHabitacion", "CreadorHabitacionEstandar", "CreadorSuite",
            ]),
        )


class TestCreadorHabitacionEstandar(unittest.TestCase):
    """Verifica el creador concreto de habitaciones estándar."""

    def test_crea_habitacion_estandar_con_las_camas_configuradas(self) -> None:
        habitacion = CreadorHabitacionEstandar(3).crear_habitacion("Triple 301", 120.0)
        self.assertIsInstance(habitacion, HabitacionEstandar)
        self.assertEqual(habitacion.nombre, "Triple 301")
        self.assertEqual(habitacion.tarifa, 120.0)
        self.assertEqual(habitacion.camas, 3)
        self.assertEqual(
            repr(habitacion), "HabitacionEstandar(nombre='Triple 301', tarifa=120.0, camas=3)"
        )

    def test_camas_por_defecto_son_2(self) -> None:
        habitacion = CreadorHabitacionEstandar().crear_habitacion("Doble 101", 80.0)
        self.assertEqual(
            repr(habitacion), "HabitacionEstandar(nombre='Doble 101', tarifa=80.0, camas=2)"
        )

    def test_un_creador_puede_producir_varias_habitaciones_independientes(self) -> None:
        creador = CreadorHabitacionEstandar(2)
        primera = creador.crear_habitacion("Doble 101", 80.0)
        segunda = creador.crear_habitacion("Doble 102", 85.0)
        self.assertIsNot(primera, segunda)
        self.assertEqual([primera.nombre, segunda.nombre], ["Doble 101", "Doble 102"])


class TestCreadorSuite(unittest.TestCase):
    """Verifica el creador concreto de suites."""

    def test_crea_suite_con_la_vista_configurada(self) -> None:
        suite = CreadorSuite("Vista a la montaña").crear_habitacion("Suite Andes", 300.0)
        self.assertIsInstance(suite, Suite)
        self.assertEqual(suite.vista, "Vista a la montaña")
        self.assertEqual(
            repr(suite), "Suite(nombre='Suite Andes', tarifa=300.0, vista='Vista a la montaña')"
        )

    def test_vista_por_defecto_es_vista_al_jardin(self) -> None:
        suite = CreadorSuite().crear_habitacion("Suite 1", 1.0)
        self.assertIn("vista='Vista al jardín'", repr(suite))
        self.assertEqual(suite.vista, "Vista al jardín")


class TestHabitacion(unittest.TestCase):
    """Verifica la clase abstracta Habitacion y las validaciones comunes."""

    def test_habitacion_abstracta_no_se_puede_instanciar(self) -> None:
        with self.assertRaises(TypeError):
            Habitacion("X", 1.0)

    def test_tarifa_negativa_lanza_value_error(self) -> None:
        with self.assertRaises(ValueError) as contexto:
            CreadorHabitacionEstandar().crear_habitacion("X", -5.0)
        self.assertEqual(str(contexto.exception), "La tarifa no puede ser negativa: -5.0")

    def test_tarifa_cero_es_valida(self) -> None:
        self.assertEqual(CreadorSuite().crear_habitacion("X", 0).tarifa, 0)

    def test_tarifa_es_de_solo_lectura(self) -> None:
        habitacion = CreadorHabitacionEstandar().crear_habitacion("X", 10.0)
        with self.assertRaises(AttributeError):
            habitacion.tarifa = 1.0

    def test_nombre_es_de_solo_lectura(self) -> None:
        habitacion = CreadorSuite().crear_habitacion("X", 10.0)
        with self.assertRaises(AttributeError):
            habitacion.nombre = "Y"

    def test_mostrar_info_formatea_tarifa_con_dos_decimales(self) -> None:
        _, salida_estandar = capturar_salida(
            CreadorHabitacionEstandar(1).crear_habitacion("X", 10).mostrar_info
        )
        _, salida_suite = capturar_salida(
            CreadorSuite("Vista al río").crear_habitacion("Y", 899.5).mostrar_info
        )
        self.assertIn("Tarifa: $10.00/noche", salida_estandar)
        self.assertIn("Tarifa: $899.50/noche", salida_suite)

    def test_tarifas_con_tipo_incorrecto_lanzan_type_error(self) -> None:
        creadores = (CreadorHabitacionEstandar(), CreadorSuite())
        for tarifa in (True, False, "10", None, [10]):
            for creador in creadores:
                with self.subTest(creador=creador, tarifa=tarifa):
                    with self.assertRaises(TypeError) as contexto:
                        creador.crear_habitacion("X", tarifa)
                    self.assertEqual(str(contexto.exception), "La tarifa debe ser un número")

    def test_tarifas_no_finitas_lanzan_value_error(self) -> None:
        creadores = (CreadorHabitacionEstandar(), CreadorSuite())
        for tarifa in (float("nan"), float("inf"), float("-inf"), 10 ** 400, -(10 ** 400)):
            for creador in creadores:
                with self.subTest(creador=creador, tarifa=tarifa):
                    with self.assertRaises(ValueError) as contexto:
                        creador.crear_habitacion("X", tarifa)
                    self.assertEqual(
                        str(contexto.exception), "La tarifa debe ser un número finito"
                    )

    def test_tarifa_entera_grande_pero_representable_es_valida(self) -> None:
        habitacion = CreadorSuite().crear_habitacion("X", 10 ** 100)
        self.assertEqual(habitacion.tarifa, 10 ** 100)


if __name__ == "__main__":
    unittest.main()

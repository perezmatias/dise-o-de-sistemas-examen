"""Tests del patrón Strategy (Cotizador y estrategias de tarifa)."""

import unittest
from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace

from patrones.comportamiento.strategy import (
    Cotizador,
    EstrategiaTarifa,
    TarifaCorporativa,
    TarifaTemporadaAlta,
    TarifaTemporadaBaja,
)
from tests.utilidades import capturar_salida


class HabitacionPrueba:
    """Doble de prueba con el contrato que exige el Cotizador."""

    def __init__(self, nombre: str, tarifa: float) -> None:
        self.nombre = nombre
        self.tarifa = tarifa

    def mostrar_info(self) -> None:
        print(f"Habitación de prueba: {self.nombre} | ${self.tarifa:.2f}")


class TestEstrategiasTarifa(unittest.TestCase):
    """Verifica cada estrategia concreta de forma aislada."""

    def test_temporada_alta_aplica_recargo_del_treinta_por_ciento(self) -> None:
        final, salida = capturar_salida(lambda: TarifaTemporadaAlta().aplicar(100))
        self.assertEqual(final, 130.0)
        self.assertIn("[Temporada Alta] Recargo del 30% sobre $100.00: total $130.00", salida)

    def test_temporada_alta_redondea_a_dos_decimales(self) -> None:
        final, salida = capturar_salida(lambda: TarifaTemporadaAlta().aplicar(10.01))
        self.assertEqual(final, 13.01)
        self.assertIn("total $13.01", salida)

    def test_temporada_baja_aplica_descuento_del_veinte_por_ciento(self) -> None:
        final, salida = capturar_salida(lambda: TarifaTemporadaBaja().aplicar(100))
        self.assertEqual(final, 80.0)
        self.assertIn("[Temporada Baja] Descuento del 20% sobre $100.00: total $80.00", salida)

    def test_temporada_baja_redondea_a_dos_decimales(self) -> None:
        final, _ = capturar_salida(lambda: TarifaTemporadaBaja().aplicar(1019.98))
        self.assertEqual(final, 815.98)

    def test_corporativa_aplica_descuento_del_diez_por_ciento(self) -> None:
        final, salida = capturar_salida(lambda: TarifaCorporativa("Acme").aplicar(200))
        self.assertEqual(final, 180.0)
        self.assertIn(
            "[Corporativa - Acme] Descuento del 10% sobre $200.00: total $180.00", salida
        )

    def test_corporativa_usa_el_nombre_de_la_empresa(self) -> None:
        _, salida = capturar_salida(lambda: TarifaCorporativa("Globex").aplicar(50))
        self.assertIn("[Corporativa - Globex]", salida)
        self.assertNotIn("Acme", salida)

    def test_constantes_de_las_estrategias(self) -> None:
        self.assertEqual(TarifaTemporadaAlta.RECARGO, 0.30)
        self.assertEqual(TarifaTemporadaBaja.DESCUENTO, 0.20)
        self.assertEqual(TarifaCorporativa.DESCUENTO, 0.10)

    def test_todas_las_estrategias_son_estrategia_tarifa(self) -> None:
        for estrategia in (TarifaTemporadaAlta(), TarifaTemporadaBaja(), TarifaCorporativa("A")):
            self.assertIsInstance(estrategia, EstrategiaTarifa)

    def test_estrategia_tarifa_es_abstracta(self) -> None:
        with self.assertRaises(TypeError):
            EstrategiaTarifa()  # type: ignore[abstract]

    def test_monto_cero_devuelve_cero(self) -> None:
        final, _ = capturar_salida(lambda: TarifaTemporadaAlta().aplicar(0))
        self.assertEqual(final, 0.0)

    def test_temporada_alta_rechaza_resultado_que_desborda(self) -> None:
        with self.assertRaises(ValueError):
            capturar_salida(lambda: TarifaTemporadaAlta().aplicar(1.5e308))

    def test_estrategias_rechazan_montos_invalidos(self) -> None:
        estrategias = (TarifaTemporadaAlta(), TarifaTemporadaBaja(), TarifaCorporativa("A"))
        casos = ((True, TypeError), (False, TypeError), ("10", TypeError), (None, TypeError),
                 (-1, ValueError), (float("nan"), ValueError), (float("inf"), ValueError),
                 (float("-inf"), ValueError), (10 ** 400, ValueError))
        for estrategia in estrategias:
            for monto, error in casos:
                with self.subTest(estrategia=type(estrategia).__name__, monto=monto):
                    with self.assertRaises(error):
                        capturar_salida(lambda: estrategia.aplicar(monto))

    def test_estrategias_aceptan_cero_y_montos_grandes_finitos(self) -> None:
        casos = ((TarifaTemporadaAlta(), 1.3e300), (TarifaTemporadaBaja(), 8e299),
                 (TarifaCorporativa("A"), 9e299))
        for estrategia, esperado in casos:
            with self.subTest(estrategia=type(estrategia).__name__):
                cero, _ = capturar_salida(lambda: estrategia.aplicar(0))
                grande, _ = capturar_salida(lambda: estrategia.aplicar(1e300))
                self.assertEqual(cero, 0)
                self.assertAlmostEqual(grande / esperado, 1)


class TestCotizador(unittest.TestCase):
    """Verifica el contexto que usa las estrategias."""

    def setUp(self) -> None:
        self.cotizador = Cotizador()

    def _agregar(self, *tarifas: float) -> None:
        for tarifa in tarifas:
            habitacion = HabitacionPrueba("X", tarifa)
            capturar_salida(lambda: self.cotizador.agregar_habitacion(habitacion))

    def test_calcular_total_redondea_a_dos_decimales(self) -> None:
        self._agregar(0.1, 0.2)
        self.assertEqual(self.cotizador.calcular_total(), 0.3)

    def test_calcular_total_de_cotizador_vacio_es_cero(self) -> None:
        self.assertEqual(self.cotizador.calcular_total(), 0)

    def test_agregar_habitacion_imprime_confirmacion(self) -> None:
        _, salida = capturar_salida(
            lambda: self.cotizador.agregar_habitacion(HabitacionPrueba("Doble 101", 80))
        )
        self.assertEqual(salida.strip(), "Habitación agregada a la cotización: Doble 101")

    def test_confirmar_muestra_total_formateado(self) -> None:
        self._agregar(0.1, 0.2)
        self.cotizador.set_estrategia_tarifa(TarifaTemporadaBaja())
        _, salida = capturar_salida(self.cotizador.confirmar)
        self.assertIn("Subtotal: $0.30", salida)
        self.assertNotIn("0.30000000000000004", salida)

    def test_confirmar_aplica_la_estrategia_y_muestra_el_detalle(self) -> None:
        self._agregar(100)
        self.cotizador.set_estrategia_tarifa(TarifaTemporadaAlta())
        _, salida = capturar_salida(self.cotizador.confirmar)
        self.assertIn("=== COTIZACIÓN ===", salida)
        self.assertIn("Habitación de prueba: X | $100.00", salida)
        self.assertIn("[Temporada Alta] Recargo del 30% sobre $100.00: total $130.00", salida)
        self.assertIn("¡Cotización confirmada!", salida)

    def test_confirmar_vacia_cotizador_y_estrategia(self) -> None:
        self._agregar(10.0)
        self.cotizador.set_estrategia_tarifa(TarifaTemporadaBaja())
        capturar_salida(self.cotizador.confirmar)
        self.assertEqual(self.cotizador.habitaciones, [])
        self.assertIsNone(self.cotizador.estrategia_tarifa)

    def test_confirmar_sin_habitaciones_no_aplica_tarifa(self) -> None:
        self.cotizador.set_estrategia_tarifa(TarifaTemporadaBaja())
        _, salida = capturar_salida(self.cotizador.confirmar)
        self.assertIn("La cotización está vacía", salida)
        self.assertNotIn("[Temporada Baja]", salida)

    def test_confirmar_sin_estrategia_no_aplica_tarifa(self) -> None:
        self._agregar(10.0)
        _, salida = capturar_salida(self.cotizador.confirmar)
        self.assertIn("Debe seleccionar una estrategia de tarifa", salida)
        self.assertEqual(len(self.cotizador.habitaciones), 1)

    def test_set_estrategia_rechaza_objetos_que_no_son_estrategia(self) -> None:
        with self.assertRaises(TypeError):
            self.cotizador.set_estrategia_tarifa("corporativa")  # type: ignore[arg-type]
        self.assertIsNone(self.cotizador.estrategia_tarifa)

    def test_confirmar_usa_la_ultima_estrategia_seleccionada(self) -> None:
        self._agregar(20)
        self.cotizador.set_estrategia_tarifa(TarifaTemporadaAlta())
        self.cotizador.set_estrategia_tarifa(TarifaTemporadaBaja())
        _, salida = capturar_salida(self.cotizador.confirmar)
        self.assertIn("total $16.00", salida)
        self.assertNotIn("Temporada Alta", salida)

    def test_error_de_estrategia_conserva_cotizacion_y_permite_reintentar(self) -> None:
        class TarifaFallida(EstrategiaTarifa):
            def aplicar(self, monto: float) -> float:
                raise RuntimeError("Tarifa rechazada")

        self._agregar(10)
        estrategia = TarifaFallida()
        self.cotizador.set_estrategia_tarifa(estrategia)
        with self.assertRaises(RuntimeError):
            capturar_salida(self.cotizador.confirmar)
        self.assertEqual(self.cotizador.calcular_total(), 10)
        self.assertIs(self.cotizador.estrategia_tarifa, estrategia)
        self.cotizador.set_estrategia_tarifa(TarifaTemporadaBaja())
        _, salida = capturar_salida(self.cotizador.confirmar)
        self.assertIn("total $8.00", salida)
        self.assertEqual(self.cotizador.calcular_total(), 0)

    def test_retorno_invalido_de_estrategia_conserva_cotizacion(self) -> None:
        class TarifaInvalida(EstrategiaTarifa):
            def aplicar(self, monto: float) -> float:
                return float("inf")

        self._agregar(10)
        estrategia = TarifaInvalida()
        self.cotizador.set_estrategia_tarifa(estrategia)
        with self.assertRaises(ValueError):
            capturar_salida(self.cotizador.confirmar)
        self.assertEqual(self.cotizador.calcular_total(), 10)
        self.assertIs(self.cotizador.estrategia_tarifa, estrategia)

    def test_retorno_invalido_no_anuncia_exito_y_permite_reintentar(self) -> None:
        class TarifaExterna(EstrategiaTarifa):
            def __init__(self, resultado: object) -> None:
                self.resultado = resultado

            def aplicar(self, monto: float) -> float:
                return self.resultado

        casos = ((None, TypeError), (True, TypeError), (False, TypeError), ("10", TypeError),
                 (-1, ValueError), (float("nan"), ValueError), (float("inf"), ValueError),
                 (float("-inf"), ValueError), (10 ** 400, ValueError))
        for resultado, error in casos:
            with self.subTest(resultado=resultado):
                cotizador = Cotizador()
                habitacion = HabitacionPrueba("X", 10)
                capturar_salida(lambda: cotizador.agregar_habitacion(habitacion))
                estrategia = TarifaExterna(resultado)
                cotizador.set_estrategia_tarifa(estrategia)
                salida = StringIO()
                with redirect_stdout(salida), self.assertRaises(error):
                    cotizador.confirmar()
                self.assertNotIn("¡Cotización confirmada!", salida.getvalue())
                self.assertEqual(cotizador.habitaciones, [habitacion])
                self.assertIs(cotizador.estrategia_tarifa, estrategia)
                cotizador.set_estrategia_tarifa(TarifaTemporadaBaja())
                retorno, salida_exitosa = capturar_salida(cotizador.confirmar)
                self.assertIsNone(retorno)
                self.assertIn("total $8.00", salida_exitosa)
                self.assertEqual(cotizador.habitaciones, [])

    def test_desbordamiento_de_recargo_conserva_cotizacion(self) -> None:
        self._agregar(1.5e308)
        estrategia = TarifaTemporadaAlta()
        self.cotizador.set_estrategia_tarifa(estrategia)
        salida = StringIO()
        with redirect_stdout(salida), self.assertRaises(ValueError):
            self.cotizador.confirmar()
        self.assertNotIn("total $inf", salida.getvalue())
        self.assertNotIn("¡Cotización confirmada!", salida.getvalue())
        self.assertEqual(len(self.cotizador.habitaciones), 1)
        self.assertIs(self.cotizador.estrategia_tarifa, estrategia)

    def test_cotizador_se_reutiliza_despues_de_confirmar(self) -> None:
        self._agregar(10)
        self.cotizador.set_estrategia_tarifa(TarifaTemporadaBaja())
        capturar_salida(self.cotizador.confirmar)
        self._agregar(50)
        self.cotizador.set_estrategia_tarifa(TarifaTemporadaAlta())
        _, salida = capturar_salida(self.cotizador.confirmar)
        self.assertIn("total $65.00", salida)


class TestCotizadorValidaciones(unittest.TestCase):
    """Verifica la robustez numérica y el contrato de las habitaciones."""

    def setUp(self) -> None:
        self.cotizador = Cotizador()

    def _intentar_agregar(self, habitacion: object) -> None:
        capturar_salida(lambda: self.cotizador.agregar_habitacion(habitacion))

    def test_rechaza_habitacion_sin_mostrar_info(self) -> None:
        habitacion = SimpleNamespace(nombre="X", tarifa=10)
        with self.assertRaises(TypeError):
            self._intentar_agregar(habitacion)
        self.assertEqual(self.cotizador.calcular_total(), 0)

    def test_rechaza_habitacion_sin_nombre_ni_tarifa(self) -> None:
        habitacion = SimpleNamespace(mostrar_info=lambda: None)
        with self.assertRaises(TypeError):
            self._intentar_agregar(habitacion)
        self.assertEqual(self.cotizador.habitaciones, [])

    def test_alta_fallida_no_contamina_la_cotizacion(self) -> None:
        try:
            self._intentar_agregar(object())
        except (AttributeError, TypeError):
            pass
        self.assertEqual(self.cotizador.habitaciones, [])

    def test_rechaza_tipos_de_tarifa_incorrectos(self) -> None:
        for tarifa in (True, "10", None):
            habitacion = HabitacionPrueba("X", tarifa)  # type: ignore[arg-type]
            with self.subTest(tarifa=tarifa), self.assertRaises(TypeError):
                self._intentar_agregar(habitacion)
        self.assertEqual(self.cotizador.habitaciones, [])

    def test_rechaza_tarifas_negativas_y_no_finitas(self) -> None:
        for tarifa in (-1, float("nan"), float("inf"), float("-inf"), 10 ** 400):
            with self.subTest(tarifa=tarifa), self.assertRaises(ValueError):
                self._intentar_agregar(HabitacionPrueba("X", tarifa))
        self.assertEqual(self.cotizador.habitaciones, [])

    def test_acepta_tarifa_cero_y_enteros_grandes_representables(self) -> None:
        self._intentar_agregar(HabitacionPrueba("Cortesía", 0))
        self._intentar_agregar(HabitacionPrueba("Lujo", 10 ** 100))
        self.assertEqual(len(self.cotizador.habitaciones), 2)

    def test_confirmar_rechaza_suma_infinita_sin_vaciar_cotizacion(self) -> None:
        for _ in range(2):
            self._intentar_agregar(HabitacionPrueba("X", 1e308))
        estrategia = TarifaTemporadaBaja()
        self.cotizador.set_estrategia_tarifa(estrategia)
        with self.assertRaises(ValueError):
            capturar_salida(self.cotizador.confirmar)
        self.assertEqual(len(self.cotizador.habitaciones), 2)
        self.assertIs(self.cotizador.estrategia_tarifa, estrategia)

    def test_revalida_tarifa_externa_al_calcular(self) -> None:
        for tarifa, error in ((float("nan"), ValueError), (-1, ValueError), ("10", TypeError)):
            with self.subTest(tarifa=tarifa):
                habitacion = HabitacionPrueba("X", 10)
                cotizador = Cotizador()
                capturar_salida(lambda: cotizador.agregar_habitacion(habitacion))
                habitacion.tarifa = tarifa  # type: ignore[assignment]
                with self.assertRaises(error):
                    cotizador.calcular_total()
                habitacion.tarifa = 20
                self.assertEqual(cotizador.calcular_total(), 20)

    def test_habitaciones_se_conservan_por_referencia(self) -> None:
        habitacion = HabitacionPrueba("X", 10)
        self._intentar_agregar(habitacion)
        self.assertIs(self.cotizador.habitaciones[0], habitacion)


if __name__ == "__main__":
    unittest.main()

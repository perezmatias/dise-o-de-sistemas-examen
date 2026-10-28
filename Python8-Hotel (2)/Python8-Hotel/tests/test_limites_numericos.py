"""Regresiones de desbordamiento y tarifas modificadas después del alta."""

import unittest
from types import SimpleNamespace

from patrones.comportamiento.chain import ValidadorMontoMaximo
from patrones.comportamiento.strategy import Cotizador, TarifaTemporadaBaja
from patrones.creacionales.builder import ReservaEstandarBuilder, ReservaPremiumBuilder
from patrones.creacionales.factory import CreadorHabitacionEstandar, CreadorSuite
from patrones.estructurales.adapter import AdaptadorShuttle, AdaptadorTaxi
from patrones.estructurales.decorator import HabitacionBasica, SeguroViaje
from tests.utilidades import capturar_salida


class TestLimitesNumericos(unittest.TestCase):
    """Evita resultados no finitos y excepciones de conversión sin contexto."""

    def test_tarifa_entera_fuera_de_rango_se_rechaza_con_value_error(self) -> None:
        creadores = (CreadorHabitacionEstandar().crear_habitacion,
                     CreadorSuite().crear_habitacion, HabitacionBasica)
        for crear in creadores:
            with self.subTest(crear=crear), self.assertRaises(ValueError):
                crear('X', 10 ** 400)

    def test_monto_maximo_rechaza_entero_fuera_de_rango_sin_excepcion(self) -> None:
        for total in (10 ** 400, -(10 ** 400)):
            resultado, _ = capturar_salida(
                lambda: ValidadorMontoMaximo().validar({'total': total}))
            self.assertFalse(resultado)

    def test_conversion_de_distancia_no_puede_desbordar(self) -> None:
        for distancia in (1e308, 10 ** 400):
            with self.subTest(tipo=AdaptadorTaxi, distancia=distancia), \
                    self.assertRaises(ValueError):
                AdaptadorTaxi().calcular_costo(distancia, 'Palermo')
        for distancia in (10 ** 400, float('inf')):
            with self.subTest(tipo=AdaptadorShuttle, distancia=distancia), \
                    self.assertRaises(ValueError):
                AdaptadorShuttle().calcular_costo(distancia, 'Z1')

    def test_confirmar_rechaza_suma_infinita_sin_vaciar_cotizador(self) -> None:
        cotizador = Cotizador()
        for _ in range(2):
            capturar_salida(lambda: cotizador.agregar_habitacion(
                CreadorSuite().crear_habitacion('X', 1e308)))
        estrategia = TarifaTemporadaBaja()
        cotizador.set_estrategia_tarifa(estrategia)
        with self.assertRaises(ValueError):
            capturar_salida(cotizador.confirmar)
        self.assertEqual(len(cotizador.habitaciones), 2)
        self.assertIs(cotizador.estrategia_tarifa, estrategia)

    def test_cotizador_revalida_tarifa_externa_al_calcular(self) -> None:
        for tarifa, error in ((float('nan'), ValueError), (-1, ValueError), ('10', TypeError)):
            with self.subTest(tarifa=tarifa):
                habitacion = SimpleNamespace(nombre='X', tarifa=10, mostrar_info=lambda: None)
                cotizador = Cotizador()
                capturar_salida(lambda: cotizador.agregar_habitacion(habitacion))
                habitacion.tarifa = tarifa
                with self.assertRaises(error):
                    cotizador.calcular_total()
                habitacion.tarifa = 20
                self.assertEqual(cotizador.calcular_total(), 20)

    def test_reserva_revalida_tarifa_externa_al_calcular(self) -> None:
        for tipo in (ReservaEstandarBuilder, ReservaPremiumBuilder):
            for tarifa, error in ((float('nan'), ValueError), (-1, ValueError),
                                  (True, TypeError)):
                with self.subTest(tipo=tipo, tarifa=tarifa):
                    habitacion = SimpleNamespace(nombre='X', tarifa=10)
                    builder = tipo()
                    capturar_salida(lambda: builder.agregar_habitacion(habitacion))
                    reserva = builder.build()
                    habitacion.tarifa = tarifa
                    with self.assertRaises(error):
                        reserva.calcular_total()

    def test_reserva_rechaza_total_infinito(self) -> None:
        builder = ReservaEstandarBuilder()
        for _ in range(2):
            capturar_salida(lambda: builder.agregar_habitacion(
                CreadorSuite().crear_habitacion('X', 1e308)))
        with self.assertRaises(ValueError):
            builder.build().calcular_total()

    def test_reserva_rechaza_subtotal_infinito_por_las_noches(self) -> None:
        builder = ReservaEstandarBuilder()
        capturar_salida(lambda: builder.agregar_habitacion(
            CreadorSuite().crear_habitacion('X', 1e308)))
        reserva = builder.set_noches(2).build()
        with self.assertRaises(ValueError):
            reserva.calcular_subtotal()

    def test_reserva_rechaza_noches_que_desbordan_la_multiplicacion(self) -> None:
        for tipo in (ReservaEstandarBuilder, ReservaPremiumBuilder):
            with self.subTest(tipo=tipo):
                builder = tipo()
                capturar_salida(lambda: builder.agregar_habitacion(
                    SimpleNamespace(nombre='X', tarifa=10.0)))
                reserva = builder.set_noches(10 ** 400).build()
                with self.assertRaises(ValueError):
                    reserva.calcular_total()

    def test_seguro_rechaza_precio_resultante_infinito(self) -> None:
        habitacion = SeguroViaje(HabitacionBasica('X', 1.79e308))
        with self.assertRaises(ValueError):
            _ = habitacion.precio

    def test_shuttle_rechaza_tarifa_infinita_con_conversion_finita(self) -> None:
        with self.assertRaises(ValueError):
            AdaptadorShuttle().calcular_costo(1.7e308, 'Z1')

    def test_valores_grandes_representables_siguen_funcionando(self) -> None:
        self.assertEqual(CreadorSuite().crear_habitacion('X', 10 ** 100).tarifa, 10 ** 100)
        self.assertEqual(AdaptadorTaxi().calcular_costo(1, 'Palermo'), 4.0)
        self.assertEqual(AdaptadorShuttle().calcular_costo(1, 'Z1'), 5.12)
        self.assertEqual(SeguroViaje(HabitacionBasica('X', 100)).precio, 102)

    def test_altas_rechazan_entero_fuera_de_rango_sin_modificar_estado(self) -> None:
        for tipo in (Cotizador, ReservaEstandarBuilder, ReservaPremiumBuilder):
            with self.subTest(tipo=tipo):
                destino = tipo()
                habitacion = SimpleNamespace(nombre='X', tarifa=10 ** 400,
                                             mostrar_info=lambda: None)
                with self.assertRaises(ValueError):
                    destino.agregar_habitacion(habitacion)
                if isinstance(destino, Cotizador):
                    self.assertEqual(destino.calcular_total(), 0)
                else:
                    self.assertEqual(destino.build().habitaciones, [])

    def test_reserva_se_recupera_al_corregir_tarifa_externa(self) -> None:
        # Una noche, tarifa corregida a 20: 20 + servicio (Estándar $10 / Premium $40)
        for tipo, esperado in ((ReservaEstandarBuilder, 30), (ReservaPremiumBuilder, 60)):
            habitacion = SimpleNamespace(nombre='X', tarifa=10)
            builder = tipo()
            capturar_salida(lambda: builder.agregar_habitacion(habitacion))
            reserva = builder.build()
            habitacion.tarifa = float('inf')
            with self.assertRaises(ValueError):
                reserva.calcular_total()
            habitacion.tarifa = 20
            self.assertEqual(reserva.calcular_total(), esperado)


if __name__ == "__main__":
    unittest.main()

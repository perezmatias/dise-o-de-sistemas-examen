"""Regresiones de validación y conservación del estado ante entradas inválidas."""

import unittest
from types import SimpleNamespace

from patrones.comportamiento.chain import (
    ValidadorDisponibilidad, ValidadorMontoMaximo, ValidadorRegimen, ValidadorHuesped,
)
from patrones.comportamiento.strategy import Cotizador, TarifaTemporadaBaja
from patrones.creacionales.builder import ReservaEstandarBuilder, ReservaPremiumBuilder
from patrones.creacionales.factory import CreadorHabitacionEstandar, CreadorSuite
from patrones.estructurales.adapter import AdaptadorShuttle, AdaptadorTaxi
from patrones.estructurales.decorator import HabitacionBasica
from tests.utilidades import capturar_salida


class TestRegresionesValidacion(unittest.TestCase):
    """Comprueba los errores reproducidos durante la auditoría."""

    def setUp(self) -> None:
        self.creadores = (CreadorHabitacionEstandar().crear_habitacion,
                          CreadorSuite().crear_habitacion)
        self.adaptadores = ((AdaptadorTaxi(), 'Palermo'), (AdaptadorShuttle(), 'Z1'))

    def test_disponibilidad_rechaza_cadena_en_lugar_de_lista(self) -> None:
        resultado, _ = capturar_salida(
            lambda: ValidadorDisponibilidad().validar({'habitaciones': 'x'}))
        self.assertFalse(resultado)

    def test_monto_maximo_rechaza_nan(self) -> None:
        resultado, _ = capturar_salida(
            lambda: ValidadorMontoMaximo().validar({'total': float('nan')}))
        self.assertFalse(resultado)

    def test_habitaciones_rechazan_tarifa_nan(self) -> None:
        for crear in self.creadores + (HabitacionBasica,):
            with self.subTest(crear=crear), self.assertRaises(ValueError):
                crear('X', float('nan'))

    def test_cotizador_rechaza_habitacion_sin_contrato_completo(self) -> None:
        cotizador = Cotizador()
        with self.assertRaises(TypeError):
            capturar_salida(
                lambda: cotizador.agregar_habitacion(SimpleNamespace(nombre='X', tarifa=10)))
        self.assertEqual(cotizador.calcular_total(), 0)

    def test_alta_fallida_no_contamina_cotizador(self) -> None:
        cotizador = Cotizador()
        try:
            cotizador.agregar_habitacion(object())
        except (AttributeError, TypeError):
            pass
        self.assertEqual(cotizador.habitaciones, [])

    def test_alta_fallida_no_contamina_builders(self) -> None:
        for tipo in (ReservaEstandarBuilder, ReservaPremiumBuilder):
            with self.subTest(builder=tipo):
                builder = tipo()
                try:
                    builder.agregar_habitacion(object())
                except (AttributeError, TypeError):
                    pass
                self.assertEqual(builder.build().habitaciones, [])

    def test_adaptadores_rechazan_distancia_negativa(self) -> None:
        for adaptador, zona in self.adaptadores:
            with self.subTest(adaptador=adaptador), self.assertRaises(ValueError):
                adaptador.calcular_costo(-1, zona)

    def test_disponibilidad_rechaza_tipos_incorrectos_sin_excepcion(self) -> None:
        for valor in (1, True, {'x': 1}, ('x',), None, []):
            with self.subTest(valor=valor):
                resultado, _ = capturar_salida(
                    lambda: ValidadorDisponibilidad().validar({'habitaciones': valor})
                )
                self.assertFalse(resultado)

    def test_validadores_rechazan_reserva_que_no_es_diccionario(self) -> None:
        tipos = (ValidadorDisponibilidad, ValidadorRegimen, ValidadorHuesped,
                 ValidadorMontoMaximo)
        for tipo in tipos:
            for reserva in (None, [], 'reserva'):
                with self.subTest(tipo=tipo, reserva=reserva):
                    resultado, _ = capturar_salida(lambda: tipo().validar(reserva))
                    self.assertFalse(resultado)

    def test_cadena_rechaza_nan_y_habitaciones_invalidas(self) -> None:
        cadena = ValidadorDisponibilidad()
        cadena.set_siguiente(ValidadorRegimen()).set_siguiente(ValidadorHuesped()) \
            .set_siguiente(ValidadorMontoMaximo())
        base = dict(habitaciones=['X'], regimen='desayuno', huesped='Ana Pérez', total=100)
        resultado, _ = capturar_salida(lambda: cadena.validar(dict(base)))
        self.assertTrue(resultado)
        for cambios in ({'habitaciones': 'x'}, {'total': float('nan')}):
            reserva = dict(base)
            reserva.update(cambios)
            resultado, _ = capturar_salida(lambda: cadena.validar(reserva))
            self.assertFalse(resultado)

    def test_monto_maximo_rechaza_no_finitos_y_conserva_limites(self) -> None:
        for total, esperado in ((float('inf'), False), (float('-inf'), False),
                                (True, False), (0, True), (10000, True), (10000.01, False)):
            with self.subTest(total=total):
                resultado, _ = capturar_salida(
                    lambda: ValidadorMontoMaximo().validar({'total': total}))
                self.assertEqual(resultado, esperado)
        resultado, _ = capturar_salida(lambda: ValidadorMontoMaximo().validar({}))
        self.assertTrue(resultado)  # HU-039: total ausente equivale a cero.

    def test_habitaciones_rechazan_tipos_de_tarifa_incorrectos(self) -> None:
        for crear in self.creadores + (HabitacionBasica,):
            for tarifa in (True, '10', None):
                with self.subTest(crear=crear, tarifa=tarifa), self.assertRaises(TypeError):
                    crear('X', tarifa)

    def test_habitaciones_rechazan_infinitos_y_aceptan_cero(self) -> None:
        for crear in self.creadores:
            for tarifa in (float('inf'), float('-inf')):
                with self.subTest(crear=crear, tarifa=tarifa), self.assertRaises(ValueError):
                    crear('X', tarifa)
            self.assertEqual(crear('Cortesía', 0).tarifa, 0)

    def test_habitacion_basica_rechaza_infinitos_y_acepta_cero(self) -> None:
        for precio in (float('inf'), float('-inf')):
            with self.subTest(precio=precio), self.assertRaises(ValueError):
                HabitacionBasica('X', precio)
        self.assertEqual(HabitacionBasica('Cortesía', 0).precio, 0)

    def test_altas_invalidas_preservan_habitaciones_anteriores(self) -> None:
        for tipo in (Cotizador, ReservaEstandarBuilder, ReservaPremiumBuilder):
            for tarifa, error in ((float('nan'), ValueError), (-1, ValueError),
                                  ('10', TypeError), (True, TypeError)):
                with self.subTest(tipo=tipo, tarifa=tarifa):
                    destino = tipo()
                    valida = CreadorHabitacionEstandar().crear_habitacion('Doble', 10)
                    capturar_salida(lambda: destino.agregar_habitacion(valida))
                    invalida = SimpleNamespace(nombre='X', tarifa=tarifa,
                                               mostrar_info=lambda: None)
                    with self.assertRaises(error):
                        capturar_salida(lambda: destino.agregar_habitacion(invalida))
                    if isinstance(destino, Cotizador):
                        self.assertEqual(destino.calcular_total(), 10)
                    else:
                        self.assertEqual(destino.build().habitaciones, [valida])

    def test_cotizador_admite_habitacion_ajena_con_contrato_completo(self) -> None:
        cotizador = Cotizador()
        habitacion = SimpleNamespace(nombre='Cabaña', tarifa=20,
                                     mostrar_info=lambda: print('Cabaña de prueba'))
        capturar_salida(lambda: cotizador.agregar_habitacion(habitacion))
        cotizador.set_estrategia_tarifa(TarifaTemporadaBaja())
        _, salida = capturar_salida(cotizador.confirmar)
        self.assertIn('Cabaña de prueba', salida)
        self.assertIn('[Temporada Baja] Descuento del 20% sobre $20.00: total $16.00', salida)
        self.assertEqual(cotizador.calcular_total(), 0)

    def test_builders_admiten_habitacion_ajena_con_nombre_y_tarifa(self) -> None:
        # Una noche: tarifa 20 + servicio (Estándar $10 / Premium $40)
        for tipo, total in ((ReservaEstandarBuilder, 30), (ReservaPremiumBuilder, 60)):
            builder = tipo()
            capturar_salida(
                lambda: builder.agregar_habitacion(SimpleNamespace(nombre='X', tarifa=20)))
            self.assertEqual(builder.build().calcular_total(), total)

    def test_adaptadores_rechazan_distancia_cero_y_no_finita(self) -> None:
        for adaptador, zona in self.adaptadores:
            for distancia in (0, float('nan'), float('inf'), float('-inf')):
                with self.subTest(adaptador=adaptador, distancia=distancia), \
                        self.assertRaises(ValueError):
                    adaptador.calcular_costo(distancia, zona)

    def test_adaptadores_rechazan_tipo_de_distancia_incorrecto(self) -> None:
        for adaptador, zona in self.adaptadores:
            for distancia in (True, '1', None):
                with self.subTest(adaptador=adaptador, distancia=distancia), \
                        self.assertRaises(TypeError):
                    adaptador.calcular_costo(distancia, zona)


if __name__ == '__main__':
    unittest.main()

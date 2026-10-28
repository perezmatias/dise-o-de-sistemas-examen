"""Tests del patrón Builder (Reserva, builders concretos y DirectorReserva)."""

import unittest
from types import SimpleNamespace

from patrones.creacionales.builder import (
    DirectorReserva,
    Reserva,
    ReservaBuilder,
    ReservaEstandarBuilder,
    ReservaPremiumBuilder,
)
from patrones.creacionales.factory import CreadorHabitacionEstandar, CreadorSuite
from tests.utilidades import capturar_salida

BUILDERS = (ReservaEstandarBuilder, ReservaPremiumBuilder)


class TestReservaBuilders(unittest.TestCase):
    """Verifica la construcción paso a paso de reservas."""

    def setUp(self) -> None:
        self.doble = CreadorHabitacionEstandar(2).crear_habitacion("Doble 101", 100.0)

    def test_builder_estandar_aplica_costo_y_etiqueta_por_defecto(self) -> None:
        builder = ReservaEstandarBuilder()
        capturar_salida(lambda: builder.agregar_habitacion(self.doble))
        reserva = builder.build()
        self.assertEqual(reserva.tipo_servicio, ReservaEstandarBuilder.TIPO_SERVICIO)
        self.assertEqual(reserva.calcular_total(), 110.0)

    def test_builder_premium_aplica_su_costo(self) -> None:
        builder = ReservaPremiumBuilder()
        capturar_salida(lambda: builder.agregar_habitacion(self.doble))
        reserva = builder.build()
        self.assertEqual(reserva.tipo_servicio, "Premium")
        self.assertEqual(reserva.calcular_total(), 140.0)

    def test_constantes_de_los_builders(self) -> None:
        self.assertEqual(ReservaEstandarBuilder.TIPO_SERVICIO, "Estándar")
        self.assertEqual(ReservaEstandarBuilder.COSTO_SERVICIO, 10.00)
        self.assertEqual(ReservaPremiumBuilder.TIPO_SERVICIO, "Premium")
        self.assertEqual(ReservaPremiumBuilder.COSTO_SERVICIO, 40.00)
        self.assertEqual(Reserva.PORCENTAJE_SEGURO, 0.03)

    def test_build_aplica_las_constantes_del_builder(self) -> None:
        # HU-011/HU-012: build() aplica TIPO_SERVICIO y COSTO_SERVICIO del builder,
        # aunque antes se haya llamado a set_tipo_servicio().
        for tipo in BUILDERS:
            with self.subTest(builder=tipo):
                builder = tipo()
                builder.set_tipo_servicio("Cortesía")
                reserva = builder.build()
                self.assertEqual(reserva.tipo_servicio, tipo.TIPO_SERVICIO)
                self.assertEqual(reserva.costo_servicio, tipo.COSTO_SERVICIO)

    def test_build_resetea_el_builder_para_reutilizarlo(self) -> None:
        builder = ReservaPremiumBuilder()
        capturar_salida(lambda: builder.agregar_habitacion(self.doble))
        builder.set_huesped("Ana Pérez").set_noches(3).agregar_seguro_cancelacion()
        builder.build()
        segunda = builder.build()
        self.assertEqual(segunda.habitaciones, [])
        self.assertEqual(segunda.noches, 1)
        self.assertEqual(segunda.huesped, "")
        self.assertFalse(segunda.seguro_cancelacion)
        self.assertEqual(segunda.tipo_servicio, ReservaPremiumBuilder.TIPO_SERVICIO)

    def test_reserva_con_noches_huesped_y_seguro(self) -> None:
        builder = ReservaEstandarBuilder()
        capturar_salida(lambda: builder.agregar_habitacion(self.doble))
        builder.set_noches(1)
        builder.set_huesped("Ana Pérez")
        builder.agregar_seguro_cancelacion()
        # 100 + 10 servicio + 3 seguro (3% de 100)
        self.assertEqual(builder.build().calcular_total(), 113.0)

    def test_total_multiplica_la_tarifa_por_las_noches(self) -> None:
        builder = ReservaEstandarBuilder()
        capturar_salida(lambda: builder.agregar_habitacion(self.doble))
        builder.set_noches(3)
        reserva = builder.build()
        self.assertEqual(reserva.calcular_subtotal(), 300.0)
        # 300 + 10 servicio
        self.assertEqual(reserva.calcular_total(), 310.0)

    def test_seguro_es_el_3_por_ciento_del_subtotal_con_noches(self) -> None:
        builder = ReservaPremiumBuilder()
        capturar_salida(lambda: builder.agregar_habitacion(self.doble))
        builder.set_noches(2).agregar_seguro_cancelacion()
        # 200 subtotal + 40 servicio + 6 seguro
        self.assertEqual(builder.build().calcular_total(), 246.0)

    def test_varias_habitaciones_se_suman(self) -> None:
        suite = CreadorSuite().crear_habitacion("Suite 1", 250.0)
        builder = ReservaEstandarBuilder()
        capturar_salida(lambda: builder.agregar_habitacion(self.doble))
        capturar_salida(lambda: builder.agregar_habitacion(suite))
        reserva = builder.set_noches(2).build()
        self.assertEqual(reserva.calcular_subtotal(), 700.0)

    def test_reserva_vacia_tiene_total_cero(self) -> None:
        reserva = Reserva()
        self.assertEqual(reserva.calcular_total(), 0.0)
        self.assertEqual(reserva.calcular_subtotal(), 0.0)

    def test_los_pasos_son_fluidos_y_devuelven_el_builder(self) -> None:
        for tipo in BUILDERS:
            with self.subTest(builder=tipo):
                builder = tipo()
                self.assertIs(builder.set_noches(2), builder)
                self.assertIs(builder.set_huesped("Ana"), builder)
                self.assertIs(builder.set_tipo_servicio("X"), builder)
                self.assertIs(builder.agregar_seguro_cancelacion(), builder)
                resultado, _ = capturar_salida(lambda: builder.agregar_habitacion(self.doble))
                self.assertIs(resultado, builder)

    def test_agregar_habitacion_informa_lo_agregado(self) -> None:
        builder = ReservaEstandarBuilder()
        _, salida = capturar_salida(lambda: builder.agregar_habitacion(self.doble))
        self.assertEqual(salida, "  Habitación agregada: Doble 101 ($100.00/noche)\n")

    def test_ambos_builders_heredan_directamente_de_reserva_builder(self) -> None:
        for tipo in BUILDERS:
            self.assertIn(ReservaBuilder, tipo.__bases__)

    def test_builder_abstracto_no_se_puede_instanciar(self) -> None:
        with self.assertRaises(TypeError):
            ReservaBuilder()

    def test_builder_incompleto_no_se_puede_instanciar(self) -> None:
        class BuilderIncompleto(ReservaBuilder):
            pass

        with self.assertRaises(TypeError):
            BuilderIncompleto()


class TestDirectorReserva(unittest.TestCase):
    """Verifica las secuencias predefinidas del director."""

    def setUp(self) -> None:
        self.suite = CreadorSuite("Vista al mar").crear_habitacion("Suite Nupcial", 299.99)

    def test_basica_descarta_habitaciones_y_seguro_preexistentes(self) -> None:
        for tipo in BUILDERS:
            with self.subTest(builder=tipo):
                builder = tipo()
                capturar_salida(lambda: builder.agregar_habitacion(self.suite))
                builder.agregar_seguro_cancelacion()
                habitacion = CreadorSuite().crear_habitacion("Nueva", 100.0)
                reserva, _ = capturar_salida(
                    lambda: DirectorReserva(builder).construir_reserva_basica(
                        habitacion, 1, "Ana Pérez"
                    )
                )
                self.assertEqual(reserva.habitaciones, [habitacion])
                self.assertFalse(reserva.seguro_cancelacion)
                self.assertEqual(reserva.calcular_subtotal(), 100.0)

    def test_reset_descarta_producto_parcial_sin_modificar_entregados(self) -> None:
        for tipo in BUILDERS:
            with self.subTest(builder=tipo):
                builder = tipo()
                capturar_salida(lambda: builder.agregar_habitacion(self.suite))
                entregada = builder.set_noches(2).build()
                capturar_salida(lambda: builder.agregar_habitacion(self.suite))
                builder.set_huesped("Ana").agregar_seguro_cancelacion()
                builder.reset()
                nueva = builder.build()
                self.assertEqual(nueva.habitaciones, [])
                self.assertEqual(nueva.huesped, "")
                self.assertEqual(nueva.noches, 1)
                self.assertFalse(nueva.seguro_cancelacion)
                self.assertEqual(entregada.habitaciones, [self.suite])
                self.assertEqual(entregada.calcular_subtotal(), 599.98)

    def test_completa_descarta_configuracion_anterior(self) -> None:
        for tipo in BUILDERS:
            with self.subTest(builder=tipo):
                builder = tipo()
                capturar_salida(lambda: builder.agregar_habitacion(self.suite))
                nueva = CreadorSuite().crear_habitacion("Nueva", 50.0)
                reserva, _ = capturar_salida(
                    lambda: DirectorReserva(builder).construir_reserva_completa(
                        [nueva], 2, "Luis Gómez"
                    )
                )
                self.assertEqual(reserva.habitaciones, [nueva])
                self.assertEqual(reserva.calcular_subtotal(), 100.0)
                self.assertTrue(reserva.seguro_cancelacion)

    def test_director_descarta_parciales_despues_de_cada_error(self) -> None:
        for tipo in BUILDERS:
            for receta in ("basica", "completa"):
                for campo in ("noches", "huesped", "habitacion"):
                    if receta == "basica" and campo == "habitacion":
                        continue
                    with self.subTest(builder=tipo, receta=receta, campo=campo):
                        builder = tipo()
                        director = DirectorReserva(builder)
                        noches = 0 if campo == "noches" else 2
                        huesped = None if campo == "huesped" else "Ana Pérez"
                        error = ValueError if campo == "noches" else TypeError
                        with self.assertRaises(error):
                            if receta == "basica":
                                capturar_salida(lambda: director.construir_reserva_basica(
                                    self.suite, noches, huesped
                                ))
                            else:
                                habitaciones = [self.suite]
                                if campo == "habitacion":
                                    habitaciones.append(object())
                                capturar_salida(lambda: director.construir_reserva_completa(
                                    habitaciones, noches, huesped
                                ))
                        parcial = builder.build()
                        self.assertEqual(parcial.habitaciones, [])
                        self.assertEqual(parcial.noches, 1)
                        self.assertEqual(parcial.huesped, "")
                        self.assertFalse(parcial.seguro_cancelacion)
                        reserva, _ = capturar_salida(
                            lambda: director.construir_reserva_basica(self.suite, 1, "Ana")
                        )
                        self.assertEqual(reserva.habitaciones, [self.suite])

    def test_reserva_completa_premium(self) -> None:
        director = DirectorReserva(ReservaEstandarBuilder())
        director.set_builder(ReservaPremiumBuilder())
        reserva, _ = capturar_salida(
            lambda: director.construir_reserva_completa([self.suite], 1, "Ana Pérez")
        )
        self.assertTrue(reserva.seguro_cancelacion)
        self.assertEqual(reserva.huesped, "Ana Pérez")
        self.assertEqual(reserva.noches, 1)
        # 299.99 + 40 servicio + 9.0 seguro (3% de 299.99 = 8.9997 -> 9.0)
        self.assertEqual(reserva.calcular_total(), 348.99)

    def test_reserva_basica_sin_extras(self) -> None:
        director = DirectorReserva(ReservaEstandarBuilder())
        reserva, _ = capturar_salida(
            lambda: director.construir_reserva_basica(self.suite, 2, "Luis Gómez")
        )
        self.assertFalse(reserva.seguro_cancelacion)
        self.assertEqual(reserva.huesped, "Luis Gómez")
        self.assertEqual(reserva.noches, 2)
        self.assertEqual(reserva.habitaciones, [self.suite])
        self.assertEqual(reserva.calcular_total(), 609.98)

    def test_reserva_completa_acepta_varias_habitaciones(self) -> None:
        doble = CreadorHabitacionEstandar().crear_habitacion("Doble 101", 100.0)
        director = DirectorReserva(ReservaEstandarBuilder())
        reserva, _ = capturar_salida(
            lambda: director.construir_reserva_completa([doble, doble], 2, "Ana Pérez")
        )
        self.assertEqual(len(reserva.habitaciones), 2)
        # 400 subtotal + 10 servicio + 12 seguro
        self.assertEqual(reserva.calcular_total(), 422.0)

    def test_set_builder_permite_reutilizar_el_director(self) -> None:
        director = DirectorReserva(ReservaEstandarBuilder())
        primera, _ = capturar_salida(
            lambda: director.construir_reserva_basica(self.suite, 1, "Ana Pérez")
        )
        director.set_builder(ReservaPremiumBuilder())
        segunda, _ = capturar_salida(
            lambda: director.construir_reserva_basica(self.suite, 1, "Ana Pérez")
        )
        self.assertEqual(primera.tipo_servicio, "Estándar")
        self.assertEqual(segunda.tipo_servicio, "Premium")


class TestReservaValidaciones(unittest.TestCase):
    """Verifica las validaciones de entrada y la integridad del estado."""

    def test_alta_fallida_no_contamina_builders(self) -> None:
        for tipo in BUILDERS:
            with self.subTest(builder=tipo):
                builder = tipo()
                with self.assertRaises(TypeError):
                    builder.agregar_habitacion(object())
                self.assertEqual(builder.build().habitaciones, [])

    def test_habitacion_sin_contrato_lanza_type_error_con_mensaje(self) -> None:
        with self.assertRaises(TypeError) as contexto:
            ReservaEstandarBuilder().agregar_habitacion(SimpleNamespace(nombre="X"))
        self.assertEqual(str(contexto.exception), "La habitación debe exponer nombre y tarifa")

    def test_altas_invalidas_preservan_habitaciones_anteriores(self) -> None:
        casos = (
            (float("nan"), ValueError), (-1, ValueError), (float("inf"), ValueError),
            (True, TypeError), ("10", TypeError), (None, TypeError),
        )
        for tipo in BUILDERS:
            for tarifa, error in casos:
                with self.subTest(builder=tipo, tarifa=tarifa):
                    builder = tipo()
                    valida = CreadorSuite().crear_habitacion("Suite", 10)
                    capturar_salida(lambda: builder.agregar_habitacion(valida))
                    invalida = SimpleNamespace(nombre="X", tarifa=tarifa)
                    with self.assertRaises(error):
                        capturar_salida(lambda: builder.agregar_habitacion(invalida))
                    self.assertEqual(builder.build().habitaciones, [valida])

    def test_builders_admiten_habitacion_ajena_con_nombre_y_tarifa(self) -> None:
        for tipo, total in ((ReservaEstandarBuilder, 30), (ReservaPremiumBuilder, 60)):
            with self.subTest(builder=tipo):
                builder = tipo()
                ajena = SimpleNamespace(nombre="Cabaña", tarifa=20)
                capturar_salida(lambda: builder.agregar_habitacion(ajena))
                self.assertEqual(builder.build().calcular_total(), total)

    def test_altas_rechazan_entero_fuera_de_rango_sin_modificar_estado(self) -> None:
        for tipo in BUILDERS:
            with self.subTest(builder=tipo):
                builder = tipo()
                ajena = SimpleNamespace(nombre="X", tarifa=10 ** 400)
                with self.assertRaises(ValueError):
                    builder.agregar_habitacion(ajena)
                self.assertEqual(builder.build().habitaciones, [])

    def test_reserva_revalida_tarifa_externa_al_calcular(self) -> None:
        casos = ((float("nan"), ValueError), (-1, ValueError), (True, TypeError))
        for tipo in BUILDERS:
            for tarifa, error in casos:
                with self.subTest(builder=tipo, tarifa=tarifa):
                    habitacion = SimpleNamespace(nombre="X", tarifa=10)
                    builder = tipo()
                    capturar_salida(lambda: builder.agregar_habitacion(habitacion))
                    reserva = builder.build()
                    habitacion.tarifa = tarifa
                    with self.assertRaises(error):
                        reserva.calcular_total()

    def test_reserva_se_recupera_al_corregir_tarifa_externa(self) -> None:
        for tipo, esperado in ((ReservaEstandarBuilder, 30), (ReservaPremiumBuilder, 60)):
            with self.subTest(builder=tipo):
                habitacion = SimpleNamespace(nombre="X", tarifa=10)
                builder = tipo()
                capturar_salida(lambda: builder.agregar_habitacion(habitacion))
                reserva = builder.build()
                habitacion.tarifa = float("inf")
                with self.assertRaises(ValueError):
                    reserva.calcular_total()
                habitacion.tarifa = 20
                self.assertEqual(reserva.calcular_total(), esperado)

    def test_reserva_rechaza_total_infinito(self) -> None:
        builder = ReservaEstandarBuilder()
        capturar_salida(lambda: builder.agregar_habitacion(
            CreadorSuite().crear_habitacion("X", 1e308)))
        with self.assertRaises(ValueError):
            builder.set_noches(2).build().calcular_total()

    def test_subtotal_entero_enorme_se_rechaza_con_value_error(self) -> None:
        reserva = Reserva()
        reserva.agregar_habitacion(SimpleNamespace(nombre="X", tarifa=10 ** 300))
        reserva.set_noches(10 ** 20)
        with self.assertRaises(ValueError):
            reserva.calcular_subtotal()

    def test_noches_invalidas(self) -> None:
        for builder in (ReservaEstandarBuilder(), Reserva()):
            for noches, error in ((0, ValueError), (-2, ValueError), (True, TypeError),
                                  (1.5, TypeError), ("2", TypeError), (None, TypeError)):
                with self.subTest(destino=type(builder), noches=noches):
                    with self.assertRaises(error):
                        builder.set_noches(noches)

    def test_noche_invalida_no_modifica_el_estado(self) -> None:
        reserva = Reserva()
        reserva.set_noches(4)
        with self.assertRaises(ValueError):
            reserva.set_noches(0)
        self.assertEqual(reserva.noches, 4)

    def test_huesped_debe_ser_texto(self) -> None:
        reserva = Reserva()
        with self.assertRaises(TypeError):
            reserva.set_huesped(123)
        reserva.set_huesped("Ana Pérez")
        self.assertEqual(reserva.huesped, "Ana Pérez")

    def test_costo_de_servicio_se_valida(self) -> None:
        reserva = Reserva()
        for costo, error in ((-1, ValueError), (float("nan"), ValueError),
                             (float("inf"), ValueError), (True, TypeError), ("5", TypeError)):
            with self.subTest(costo=costo):
                with self.assertRaises(error):
                    reserva.set_tipo_servicio("X", costo)
        self.assertEqual(reserva.costo_servicio, 0.0)
        reserva.set_tipo_servicio("Cortesía", 0)
        self.assertEqual(reserva.tipo_servicio, "Cortesía")

    def test_habitaciones_devuelve_copia_y_no_expone_el_estado(self) -> None:
        reserva = Reserva()
        reserva.agregar_habitacion(CreadorSuite().crear_habitacion("S", 10.0))
        reserva.habitaciones.clear()
        self.assertEqual(len(reserva.habitaciones), 1)


class TestReservaSalida(unittest.TestCase):
    """Verifica el resumen impreso y la representación de la reserva."""

    def setUp(self) -> None:
        self.doble = CreadorHabitacionEstandar().crear_habitacion("Doble 101", 80.0)
        director = DirectorReserva(ReservaPremiumBuilder())
        self.reserva, _ = capturar_salida(
            lambda: director.construir_reserva_completa([self.doble], 3, "Ana Pérez")
        )

    def test_mostrar_resumen_incluye_todas_las_lineas(self) -> None:
        _, salida = capturar_salida(self.reserva.mostrar_resumen)
        self.assertIn("Huésped: Ana Pérez", salida)
        self.assertIn("Noches: 3", salida)
        self.assertIn("Habitaciones:", salida)
        self.assertIn("  - Doble 101 | $80.00/noche", salida)
        self.assertIn("Servicio: Premium ($40.00)", salida)
        self.assertIn("Seguro de cancelación: Sí (+$7.20)", salida)
        self.assertIn("Subtotal: $240.00", salida)
        self.assertIn("TOTAL: $287.20", salida)

    def test_mostrar_resumen_sin_seguro_lo_indica(self) -> None:
        reserva, _ = capturar_salida(
            lambda: DirectorReserva(ReservaEstandarBuilder()).construir_reserva_basica(
                self.doble, 1, "Luis Gómez")
        )
        _, salida = capturar_salida(reserva.mostrar_resumen)
        self.assertIn("Seguro de cancelación: No", salida)
        self.assertIn("TOTAL: $90.00", salida)

    def test_repr_describe_la_reserva(self) -> None:
        self.assertEqual(
            repr(self.reserva),
            "Reserva(huesped='Ana Pérez', habitaciones=['Doble 101'], noches=3, "
            "servicio='Premium', total=287.20)",
        )


if __name__ == "__main__":
    unittest.main()

"""Tests del patrón Decorator (servicios opcionales sobre habitaciones)."""

import unittest

from patrones.estructurales.decorator import (
    ComponenteHabitacion,
    DecoradorHabitacion,
    DesayunoIncluido,
    HabitacionBasica,
    LateCheckout,
    SeguroViaje,
)


class TestDecoradores(unittest.TestCase):
    """Verifica el apilamiento de precio y descripción."""

    def test_habitacion_base_sin_decorar(self) -> None:
        habitacion = HabitacionBasica("X", 10.0)
        self.assertEqual(habitacion.descripcion, "X")
        self.assertEqual(habitacion.precio, 10.0)

    def test_desayuno_suma_costo_fijo(self) -> None:
        self.assertEqual(DesayunoIncluido(HabitacionBasica("X", 10.0)).precio, 25.0)

    def test_late_checkout_suma_costo_fijo(self) -> None:
        self.assertEqual(LateCheckout(HabitacionBasica("X", 10.0)).precio, 35.0)

    def test_seguro_se_calcula_sobre_el_precio_ya_decorado(self) -> None:
        habitacion = SeguroViaje(DesayunoIncluido(HabitacionBasica("X", 85.0)))
        self.assertEqual(habitacion.precio, 102.0)  # (85 + 15) * 1.02

    def test_apilado_completo_coincide_con_el_ejemplo_documentado(self) -> None:
        habitacion = LateCheckout(
            SeguroViaje(DesayunoIncluido(HabitacionBasica("Suite Presidencial", 899.99)))
        )
        # (899.99 + 15) * 1.02 = 933.2898 -> 933.29; + 25 = 958.29
        self.assertEqual(habitacion.precio, 958.29)
        self.assertEqual(
            habitacion.descripcion,
            "Suite Presidencial + Desayuno incluido + Seguro de viaje + Late checkout",
        )

    def test_docstring_del_modulo_documenta_el_precio_real(self) -> None:
        import patrones.estructurales.decorator.decorador_habitacion as modulo
        self.assertIn("958.29", modulo.__doc__)
        self.assertNotIn("958.99", modulo.__doc__)

    def test_un_decorador_puede_aplicarse_dos_veces(self) -> None:
        doble = DesayunoIncluido(DesayunoIncluido(HabitacionBasica("X", 10.0)))
        self.assertEqual(doble.precio, 40.0)
        self.assertEqual(doble.descripcion, "X + Desayuno incluido + Desayuno incluido")

    def test_el_orden_de_apilado_altera_el_precio_del_seguro(self) -> None:
        seguro_primero = DesayunoIncluido(SeguroViaje(HabitacionBasica("X", 100.0)))
        seguro_ultimo = SeguroViaje(DesayunoIncluido(HabitacionBasica("X", 100.0)))
        self.assertEqual(seguro_primero.precio, 117.0)  # 100 * 1.02 + 15
        self.assertEqual(seguro_ultimo.precio, 117.3)  # (100 + 15) * 1.02
        self.assertNotEqual(seguro_primero.precio, seguro_ultimo.precio)

    def test_componente_abstracto_no_se_puede_instanciar(self) -> None:
        with self.assertRaises(TypeError):
            ComponenteHabitacion()

    def test_precio_base_negativo_lanza_value_error(self) -> None:
        with self.assertRaises(ValueError):
            HabitacionBasica("X", -1.0)

    def test_decorador_base_delega_en_el_componente(self) -> None:
        decorador = DecoradorHabitacion(HabitacionBasica("X", 10.0))
        self.assertIsInstance(decorador, ComponenteHabitacion)
        self.assertEqual(decorador.descripcion, "X")
        self.assertEqual(decorador.precio, 10.0)

    def test_decoradores_son_intercambiables_con_el_componente(self) -> None:
        for decorador in (DesayunoIncluido, SeguroViaje, LateCheckout):
            with self.subTest(decorador=decorador):
                self.assertIsInstance(decorador(HabitacionBasica("X", 10.0)),
                                      ComponenteHabitacion)

    def test_repr_de_la_habitacion_basica(self) -> None:
        self.assertEqual(repr(HabitacionBasica("Doble 101", 80.0)),
                         "HabitacionBasica('Doble 101', 80.0)")


class TestValidacionPrecioBase(unittest.TestCase):
    """Verifica las validaciones numéricas de HabitacionBasica."""

    def test_precio_cero_es_valido(self) -> None:
        self.assertEqual(HabitacionBasica("Cortesía", 0).precio, 0)

    def test_precio_entero_es_valido(self) -> None:
        self.assertEqual(HabitacionBasica("X", 100).precio, 100)

    def test_precio_bool_lanza_type_error(self) -> None:
        for valor in (True, False):
            with self.subTest(valor=valor), self.assertRaises(TypeError):
                HabitacionBasica("X", valor)

    def test_precio_no_numerico_lanza_type_error(self) -> None:
        for valor in ("10", None, [10]):
            with self.subTest(valor=valor), self.assertRaises(TypeError):
                HabitacionBasica("X", valor)

    def test_precio_no_finito_lanza_value_error(self) -> None:
        for valor in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                HabitacionBasica("X", valor)

    def test_precio_entero_fuera_de_rango_lanza_value_error(self) -> None:
        for valor in (10 ** 400, -(10 ** 400)):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                HabitacionBasica("X", valor)

    def test_mensajes_de_error_exactos(self) -> None:
        with self.assertRaises(TypeError) as ctx:
            HabitacionBasica("X", "10")
        self.assertEqual(str(ctx.exception), "El precio debe ser un número")
        with self.assertRaises(ValueError) as ctx:
            HabitacionBasica("X", float("nan"))
        self.assertEqual(str(ctx.exception), "El precio debe ser finito")
        with self.assertRaises(ValueError) as ctx:
            HabitacionBasica("X", -5.0)
        self.assertEqual(str(ctx.exception), "El precio no puede ser negativo: -5.0")

    def test_valores_grandes_representables_siguen_funcionando(self) -> None:
        self.assertEqual(HabitacionBasica("X", 10 ** 100).precio, 10 ** 100)
        self.assertEqual(SeguroViaje(HabitacionBasica("X", 100)).precio, 102)


class TestSeguroViaje(unittest.TestCase):
    """Verifica el cálculo del 2% y su robustez numérica."""

    def test_seguro_suma_dos_por_ciento(self) -> None:
        self.assertEqual(SeguroViaje(HabitacionBasica("X", 200.0)).precio, 204.0)

    def test_seguro_redondea_a_dos_decimales(self) -> None:
        # 33.33 * 1.02 = 33.9966 -> 34.0 al redondear a 2 decimales
        self.assertEqual(SeguroViaje(HabitacionBasica("X", 33.33)).precio, 34.0)

    def test_seguro_rechaza_precio_resultante_infinito(self) -> None:
        habitacion = SeguroViaje(HabitacionBasica("X", 1.79e308))
        with self.assertRaises(ValueError):
            _ = habitacion.precio

    def test_seguro_usa_el_porcentaje_documentado(self) -> None:
        self.assertEqual(SeguroViaje.PORCENTAJE, 0.02)
        self.assertEqual(DesayunoIncluido.COSTO, 15.00)
        self.assertEqual(LateCheckout.COSTO, 25.00)


if __name__ == "__main__":
    unittest.main()

"""Tests del patrón Adapter (traslados aeropuerto-hotel con taxi y shuttle)."""

import unittest

from patrones.estructurales.adapter import (
    AdaptadorShuttle,
    AdaptadorTaxi,
    ServicioTraslado,
    SistemaLegadoShuttle,
    SistemaLegadoTaxi,
)
from tests.utilidades import capturar_salida


class TestAdaptadorTaxi(unittest.TestCase):
    """Verifica la traducción km→metros y el parseo de minutos del taxi."""

    def setUp(self) -> None:
        self.adaptador = AdaptadorTaxi()

    def test_implementa_la_interfaz_unificada(self) -> None:
        self.assertIsInstance(self.adaptador, ServicioTraslado)

    def test_interfaz_abstracta_no_se_puede_instanciar(self) -> None:
        with self.assertRaises(TypeError):
            ServicioTraslado()

    def test_calcular_costo_convierte_km_a_metros_zona_cercana(self) -> None:
        # 2.5 km = 2500 m, zona cercana -> 2.50 + 2500 * 0.0015 = 6.25
        self.assertEqual(self.adaptador.calcular_costo(2.5, "Palermo"), 6.25)

    def test_calcular_costo_zona_lejana_usa_tarifa_mayor(self) -> None:
        # 2.5 km = 2500 m, zona lejana -> 2.50 + 2500 * 0.0025 = 8.75
        self.assertEqual(self.adaptador.calcular_costo(2.5, "Belgrano"), 8.75)

    def test_calcular_costo_redondea_metros_en_vez_de_truncar(self) -> None:
        # 0.0039 km = 3.9 m -> 4 m -> 2.50 + 0.006 = 2.506 -> 2.51 (truncando daría 2.50)
        self.assertEqual(self.adaptador.calcular_costo(0.0039, "Palermo"), 2.51)
        # 0.0029 km = 2.9 m -> 3 m -> 2.50 + 0.0075 = 2.5075 -> 2.51 (truncando daría 2.50)
        self.assertEqual(self.adaptador.calcular_costo(0.0029, "Belgrano"), 2.51)

    def test_calcular_costo_acepta_distancia_entera(self) -> None:
        # 1 km = 1000 m, zona cercana -> 2.50 + 1000 * 0.0015 = 4.00
        self.assertEqual(self.adaptador.calcular_costo(1, "Centro"), 4.0)

    def test_estimar_minutos_zona_cercana(self) -> None:
        self.assertEqual(self.adaptador.estimar_minutos("Palermo"), 10)

    def test_estimar_minutos_zona_lejana(self) -> None:
        self.assertEqual(self.adaptador.estimar_minutos("Belgrano"), 25)

    def test_estimar_minutos_ignora_tildes_mayusculas_y_espacios(self) -> None:
        self.assertEqual(self.adaptador.estimar_minutos("Recoleta"), 10)
        self.assertEqual(self.adaptador.estimar_minutos("  RECOLETA "), 10)
        self.assertEqual(self.adaptador.estimar_minutos("  PALERMÓ "), 10)
        self.assertEqual(self.adaptador.estimar_minutos("San Telmo"), 10)

    def test_crear_traslado_genera_id_de_movil(self) -> None:
        movil, _ = capturar_salida(
            lambda: self.adaptador.crear_traslado("res-001", "Palermo")
        )
        self.assertEqual(movil, "TAXI-RES-001-PAL")

    def test_crear_traslado_usa_tres_letras_de_la_zona_normalizada(self) -> None:
        movil, _ = capturar_salida(
            lambda: self.adaptador.crear_traslado("res-002", "  Núñez ")
        )
        self.assertEqual(movil, "TAXI-RES-002-NUN")

    def test_crear_traslado_imprime_la_asignacion(self) -> None:
        _, salida = capturar_salida(
            lambda: self.adaptador.crear_traslado("res-001", "Palermo")
        )
        self.assertEqual(salida, "[Taxi] Móvil asignado para res-001 hacia Palermo\n")


class TestAdaptadorShuttle(unittest.TestCase):
    """Verifica la traducción km→millas y los códigos de zona del shuttle."""

    def setUp(self) -> None:
        self.adaptador = AdaptadorShuttle()

    def test_implementa_la_interfaz_unificada(self) -> None:
        self.assertIsInstance(self.adaptador, ServicioTraslado)

    def test_constante_de_conversion_documentada(self) -> None:
        self.assertEqual(AdaptadorShuttle.KM_A_MILLAS, 0.621)

    def test_calcular_costo_convierte_km_a_millas(self) -> None:
        # 2.5 km = 1.5525 mi -> 1.552 mi (3 decimales) -> 4.00 + 1.552 * 1.80 = 6.7936 -> 6.79
        self.assertAlmostEqual(self.adaptador.calcular_costo(2.5, "Z1"), 6.79, places=2)

    def test_calcular_costo_con_otra_distancia(self) -> None:
        # 10 km = 6.21 mi -> 4.00 + 6.21 * 1.80 = 15.178 -> 15.18
        self.assertEqual(self.adaptador.calcular_costo(10, "Z2"), 15.18)

    def test_estimar_minutos_segun_codigo_de_zona(self) -> None:
        self.assertEqual(self.adaptador.estimar_minutos("Z1"), 20)
        self.assertEqual(self.adaptador.estimar_minutos("Z2"), 35)

    def test_estimar_minutos_codigo_desconocido_usa_valor_por_defecto(self) -> None:
        self.assertEqual(self.adaptador.estimar_minutos("Z3"), 50)
        self.assertEqual(self.adaptador.estimar_minutos("Z9"), 50)

    def test_estimar_minutos_normaliza_el_codigo_de_zona(self) -> None:
        # reservar_asiento() ya pasaba el código a mayúsculas: minutos_estimados() también
        self.assertEqual(self.adaptador.estimar_minutos("z1"), 20)
        self.assertEqual(self.adaptador.estimar_minutos(" z2 "), 35)
        self.assertEqual(self.adaptador.estimar_minutos(" z9 "), 50)

    def test_crear_traslado_genera_reserva_de_asiento(self) -> None:
        asiento, _ = capturar_salida(
            lambda: self.adaptador.crear_traslado("res-001", "Z1")
        )
        self.assertEqual(asiento, "SHTRES-001Z1")

    def test_crear_traslado_pone_el_codigo_en_mayusculas(self) -> None:
        asiento, _ = capturar_salida(
            lambda: self.adaptador.crear_traslado("res-002", "z2")
        )
        self.assertEqual(asiento, "SHTRES-002Z2")

    def test_crear_traslado_normaliza_codigo_desconocido_con_espacios(self) -> None:
        """Normaliza también códigos sin una estimación específica de minutos."""
        asiento, salida = capturar_salida(
            lambda: self.adaptador.crear_traslado("res-003", "\tz9\n")
        )
        self.assertEqual(asiento, "SHTRES-003Z9")
        self.assertEqual(self.adaptador.estimar_minutos("\tz9\n"), 50)
        self.assertEqual(salida, "[Shuttle] Asiento reservado para res-003 (\tz9\n)\n")

    def test_crear_traslado_imprime_la_reserva(self) -> None:
        _, salida = capturar_salida(
            lambda: self.adaptador.crear_traslado("res-001", "Z1")
        )
        self.assertEqual(salida, "[Shuttle] Asiento reservado para res-001 (Z1)\n")

    def test_crear_traslado_normaliza_espacios_del_codigo_en_el_id(self) -> None:
        """Evita que espacios externos formen parte del asiento asignado."""
        asiento, _ = capturar_salida(
            lambda: self.adaptador.crear_traslado("res-002", " z2 ")
        )
        self.assertEqual(asiento, "SHTRES-002Z2")


class TestSistemasLegados(unittest.TestCase):
    """Verifica las APIs incompatibles que los adaptadores esconden."""

    def test_taxi_trabaja_en_metros_y_distingue_zonas(self) -> None:
        taxi = SistemaLegadoTaxi()
        self.assertEqual(taxi.calcular_tarifa_taxi(1000, "Centro"), 4.0)
        self.assertEqual(taxi.calcular_tarifa_taxi(1000, "Otra zona"), 5.0)

    def test_taxi_zonas_cercanas_documentadas(self) -> None:
        self.assertEqual(
            SistemaLegadoTaxi.ZONAS_CERCANAS,
            {"centro", "recoleta", "palermo", "san telmo"},
        )

    def test_taxi_devuelve_el_tiempo_como_texto(self) -> None:
        taxi = SistemaLegadoTaxi()
        self.assertEqual(taxi.tiempo_espera_taxi("Centro"), "10-15 minutos")
        self.assertEqual(taxi.tiempo_espera_taxi("Otra zona"), "25-40 minutos")

    def test_taxi_rechaza_metros_fuera_de_rango_con_value_error(self) -> None:
        with self.assertRaises(ValueError):
            SistemaLegadoTaxi().calcular_tarifa_taxi(10 ** 400, "Centro")

    def test_shuttle_trabaja_en_millas(self) -> None:
        shuttle = SistemaLegadoShuttle()
        self.assertEqual(shuttle.obtener_precio_shuttle(1, "Z1"), 5.8)
        self.assertEqual(shuttle.minutos_estimados("Z1"), 20)
        self.assertEqual(shuttle.minutos_estimados("Z2"), 35)
        self.assertEqual(shuttle.minutos_estimados("Z3"), 50)

    def test_shuttle_minutos_estimados_normaliza_el_codigo(self) -> None:
        shuttle = SistemaLegadoShuttle()
        self.assertEqual(shuttle.minutos_estimados("z1"), 20)
        self.assertEqual(shuttle.minutos_estimados(" z2 "), 35)


class TestValidacionDistancia(unittest.TestCase):
    """Replica la robustez de los adaptadores originales (peso → distancia)."""

    def setUp(self) -> None:
        self.adaptadores = ((AdaptadorTaxi(), "Palermo"), (AdaptadorShuttle(), "Z1"))

    def test_rechazan_distancia_negativa(self) -> None:
        for adaptador, zona in self.adaptadores:
            with self.subTest(adaptador=adaptador), self.assertRaises(ValueError):
                adaptador.calcular_costo(-1, zona)

    def test_rechazan_distancia_cero_y_no_finita(self) -> None:
        for adaptador, zona in self.adaptadores:
            for distancia in (0, 0.0, float("nan"), float("inf"), float("-inf")):
                with self.subTest(adaptador=adaptador, distancia=distancia), \
                        self.assertRaises(ValueError):
                    adaptador.calcular_costo(distancia, zona)

    def test_rechazan_tipo_de_distancia_incorrecto(self) -> None:
        for adaptador, zona in self.adaptadores:
            for distancia in ("5", None, True, False, [1]):
                with self.subTest(adaptador=adaptador, distancia=distancia), \
                        self.assertRaises(TypeError):
                    adaptador.calcular_costo(distancia, zona)

    def test_mensajes_de_error_exactos(self) -> None:
        for adaptador, zona in self.adaptadores:
            with self.assertRaises(TypeError) as ctx:
                adaptador.calcular_costo("5", zona)
            self.assertEqual(str(ctx.exception), "La distancia debe ser un número")
            with self.assertRaises(ValueError) as ctx:
                adaptador.calcular_costo(0, zona)
            self.assertEqual(
                str(ctx.exception), "La distancia debe ser finita y mayor que cero"
            )

    def test_conversion_a_metros_no_puede_desbordar(self) -> None:
        for distancia in (1e308, 10 ** 400):
            with self.subTest(distancia=distancia), self.assertRaises(ValueError):
                AdaptadorTaxi().calcular_costo(distancia, "Palermo")

    def test_mensaje_de_desborde_en_la_conversion_a_metros(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            AdaptadorTaxi().calcular_costo(1e308, "Palermo")
        self.assertEqual(
            str(ctx.exception), "La conversión de la distancia excede el rango numérico"
        )

    def test_shuttle_rechaza_entero_fuera_de_rango(self) -> None:
        with self.assertRaises(ValueError):
            AdaptadorShuttle().calcular_costo(10 ** 400, "Z1")

    def test_shuttle_rechaza_tarifa_infinita_con_conversion_finita(self) -> None:
        # 1.7e308 km * 0.621 sigue siendo finito, pero 4 + millas * 1.80 desborda
        with self.assertRaises(ValueError) as ctx:
            AdaptadorShuttle().calcular_costo(1.7e308, "Z1")
        self.assertEqual(str(ctx.exception), "La tarifa excede el rango numérico")

    def test_valores_grandes_representables_siguen_funcionando(self) -> None:
        self.assertEqual(AdaptadorTaxi().calcular_costo(1, "Palermo"), 4.0)
        self.assertEqual(AdaptadorShuttle().calcular_costo(1, "Z1"), 5.12)


if __name__ == "__main__":
    unittest.main()

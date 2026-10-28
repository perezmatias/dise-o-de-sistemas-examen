"""Tests del patrón Singleton (CentralReservas)."""

import contextlib
import io
import threading
import time
import unittest

from patrones.creacionales.singleton import CentralReservas
from tests.utilidades import capturar_salida


class SalidaLenta(io.StringIO):
    """Stream que demora cada escritura para forzar la intercalación de hilos."""

    def write(self, texto: str) -> int:
        """Escribe el texto tras una pausa breve.

        Args:
            texto: Texto a escribir en el buffer.

        Returns:
            int: Cantidad de caracteres escritos.
        """
        time.sleep(0.02)
        return super().write(texto)


class TestCentralReservas(unittest.TestCase):
    """Verifica la unicidad de la instancia y la no reinicialización."""

    def setUp(self) -> None:
        """Resetea el Singleton para que cada test arranque limpio."""
        CentralReservas._instance = None

    def test_get_instance_devuelve_siempre_el_mismo_objeto(self) -> None:
        (c1, c2), _ = capturar_salida(
            lambda: (CentralReservas.get_instance(), CentralReservas.get_instance())
        )
        self.assertIs(c1, c2)

    def test_constructor_directo_tambien_devuelve_la_misma_instancia(self) -> None:
        (c1, c2), _ = capturar_salida(
            lambda: (CentralReservas(), CentralReservas.get_instance())
        )
        self.assertIs(c1, c2)

    def test_la_central_se_inicializa_una_sola_vez(self) -> None:
        _, salida = capturar_salida(
            lambda: [CentralReservas.get_instance() for _ in range(3)]
        )
        self.assertEqual(salida.count("Conectando a la central de reservas"), 1)

    def test_mensaje_de_conexion_exacto(self) -> None:
        _, salida = capturar_salida(CentralReservas.get_instance)
        self.assertEqual(
            salida, "Conectando a la central de reservas de Hotel Los Cortez...\n"
        )

    def test_reiniciar_la_instancia_vuelve_a_inicializar(self) -> None:
        _, primera = capturar_salida(CentralReservas.get_instance)
        CentralReservas._instance = None
        _, segunda = capturar_salida(CentralReservas.get_instance)
        self.assertEqual(primera, segunda)
        self.assertIn("Conectando", segunda)

    def test_acceso_concurrente_inicializa_una_sola_vez(self) -> None:
        cantidad_hilos = 8
        barrera = threading.Barrier(cantidad_hilos, timeout=5)
        instancias = []

        def tarea() -> None:
            barrera.wait()
            instancias.append(CentralReservas.get_instance())

        salida = SalidaLenta()
        with contextlib.redirect_stdout(salida):
            hilos = [threading.Thread(target=tarea, daemon=True) for _ in range(cantidad_hilos)]
            for hilo in hilos:
                hilo.start()
            for hilo in hilos:
                hilo.join(timeout=5)

        self.assertFalse(any(hilo.is_alive() for hilo in hilos), "Hilos bloqueados")

        self.assertEqual(salida.getvalue().count("Conectando a la central de reservas"), 1)
        self.assertEqual(len(instancias), cantidad_hilos)
        self.assertTrue(all(instancia is instancias[0] for instancia in instancias))

    def test_consultar_imprime_la_consulta(self) -> None:
        central, _ = capturar_salida(CentralReservas.get_instance)
        _, salida = capturar_salida(lambda: central.consultar("SELECT 1"))
        self.assertEqual(salida, "[CentralReservas] Ejecutando: SELECT 1\n")

    def test_consultar_con_otra_consulta_usa_el_mismo_formato(self) -> None:
        central, _ = capturar_salida(CentralReservas.get_instance)
        _, salida = capturar_salida(lambda: central.consultar("RESERVAS HOY"))
        self.assertIn("Ejecutando: RESERVAS HOY", salida)

    def test_propiedades_hotel_y_conectado(self) -> None:
        central, _ = capturar_salida(CentralReservas.get_instance)
        self.assertEqual(central.hotel, "Hotel Los Cortez")
        self.assertIs(central.conectado, True)

    def test_propiedades_son_de_solo_lectura(self) -> None:
        central, _ = capturar_salida(CentralReservas.get_instance)
        with self.assertRaises(AttributeError):
            central.hotel = "Otro"
        with self.assertRaises(AttributeError):
            central.conectado = False


if __name__ == "__main__":
    unittest.main()

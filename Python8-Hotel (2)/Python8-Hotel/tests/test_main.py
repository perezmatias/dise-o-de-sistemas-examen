"""Tests de humo del punto de entrada main.py (criterios de HU-040)."""

import ast
import os
import re
import subprocess
import sys
import unittest

import main
from patrones.creacionales.singleton import CentralReservas
from tests.utilidades import capturar_salida

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_MAIN = os.path.join(RAIZ, "main.py")
ORDEN_CATEGORIAS = ["creacionales", "estructurales", "comportamiento"]


def ejecutar_demo() -> str:
    """Ejecuta main.main() desde un Singleton limpio y devuelve la salida."""
    CentralReservas._instance = None
    _, salida = capturar_salida(main.main)
    return salida


def seccion_de(salida: str, numero: int) -> str:
    """Devuelve el texto de la sección numerada de la demostración.

    Args:
        salida: Salida completa de main.main().
        numero: Número de sección (1 a 8).

    Returns:
        str: Texto entre la cabecera de la sección y la siguiente (o el cierre).
    """
    partes = re.split(r">>> \d\. PATRÓN .+? <<<", salida)
    return partes[numero]


class TestMain(unittest.TestCase):
    """Verifica que la demostración completa cumple HU-040."""

    def test_shebang_esta_en_la_primera_linea(self) -> None:
        with open(RUTA_MAIN, encoding="utf-8") as archivo:
            primera_linea = archivo.readline()
        self.assertTrue(primera_linea.startswith("#!"))

    def test_demo_completa_termina_sin_errores(self) -> None:
        salida = ejecutar_demo()
        for seccion in range(1, 9):
            self.assertIn(">>> {}. PATRÓN".format(seccion), salida)
        self.assertIn("FIN DE LA DEMOSTRACIÓN", salida)

    def test_cabecera_con_titulo_y_subtitulo_del_dominio(self) -> None:
        lineas = ejecutar_demo().splitlines()
        self.assertEqual(lineas[1], "DEMOSTRACIÓN DE PATRONES DE DISEÑO EN PYTHON")
        self.assertEqual(lineas[2], "SISTEMA DE GESTIÓN HOTELERA")

    def test_demo_no_imprime_trazas_de_error(self) -> None:
        salida = ejecutar_demo()
        self.assertNotIn("Traceback", salida)
        self.assertNotIn("Error", salida)

    def test_script_se_ejecuta_directamente_con_codigo_de_salida_cero(self) -> None:
        entorno = dict(os.environ, PYTHONIOENCODING="utf-8")
        proceso = subprocess.run(
            [sys.executable, RUTA_MAIN], cwd=RAIZ, env=entorno,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(proceso.returncode, 0)
        self.assertEqual(proceso.stderr, b"")
        self.assertIn("FIN DE LA DEMOSTRACIÓN", proceso.stdout.decode("utf-8"))

    def test_demo_es_reproducible_en_ejecuciones_consecutivas(self) -> None:
        self.assertEqual(ejecutar_demo(), ejecutar_demo())

    def test_imports_organizados_en_tres_bloques_por_categoria(self) -> None:
        with open(RUTA_MAIN, encoding="utf-8") as archivo:
            arbol = ast.parse(archivo.read())
        categorias = [
            nodo.module.split(".")[1]
            for nodo in arbol.body
            if isinstance(nodo, ast.ImportFrom) and nodo.module.startswith("patrones.")
        ]
        indices = [ORDEN_CATEGORIAS.index(categoria) for categoria in categorias]
        self.assertEqual(indices, sorted(indices))

    def test_numeracion_del_docstring_coincide_con_las_secciones(self) -> None:
        documentados = {
            int(numero): nombre.upper()
            for numero, nombre in re.findall(r"^\s+(\d)\.\s+(\w+)", main.__doc__, re.M)
        }
        secciones = {
            int(numero): nombre.split()[0]
            for numero, nombre in re.findall(r">>> (\d)\. PATRÓN (.+?) <<<", ejecutar_demo())
        }
        self.assertEqual(len(secciones), 8)
        self.assertEqual(documentados, secciones)

    def test_secciones_en_el_orden_del_original(self) -> None:
        nombres = re.findall(r">>> \d\. PATRÓN (.+?) <<<", ejecutar_demo())
        self.assertEqual(
            nombres,
            ["SINGLETON", "FACTORY METHOD", "OBSERVER", "STRATEGY", "BUILDER", "DECORATOR",
             "ADAPTER", "CHAIN OF RESPONSIBILITY"],
        )

    def test_seccion_singleton_demuestra_una_unica_central(self) -> None:
        seccion = seccion_de(ejecutar_demo(), 1)
        self.assertIn("¿Son la misma instancia? True", seccion)
        self.assertEqual(seccion.count("Conectando a la central de reservas"), 1)

    def test_seccion_factory_demuestra_propiedades_nombre_y_tarifa(self) -> None:
        salida = ejecutar_demo()
        seccion = salida.split(">>> 2. PATRÓN FACTORY METHOD <<<")[1].split(">>> 3.")[0]
        lineas = [linea for linea in seccion.splitlines() if "Acceso por propiedades" in linea]
        self.assertEqual(len(lineas), 1)
        self.assertIn("Doble 101", lineas[0])
        self.assertIn("80.00", lineas[0])

    def test_seccion_factory_crea_habitaciones_estandar_y_suites(self) -> None:
        seccion = seccion_de(ejecutar_demo(), 2)
        self.assertEqual(seccion.count("Habitación Estándar:"), 2)
        self.assertEqual(seccion.count("Suite:"), 2)

    def test_seccion_observer_muestra_suscripcion_promociones_y_baja(self) -> None:
        seccion = seccion_de(ejecutar_demo(), 3)
        self.assertEqual(seccion.count("Huésped suscrito al hotel"), 3)
        self.assertEqual(seccion.count("¡Nueva promoción en Hotel Los Cortez!"), 2)
        self.assertIn("--- Notificando a 3 huéspedes ---", seccion)
        self.assertIn("Huésped desuscrito del hotel", seccion)
        self.assertIn("--- Notificando a 2 huéspedes ---", seccion)

    def test_seccion_observer_el_huesped_dado_de_baja_no_recibe_la_segunda(self) -> None:
        seccion = seccion_de(ejecutar_demo(), 3)
        segunda = seccion.split("--- Notificando a 2 huéspedes ---")[1]
        self.assertNotIn("Luis Gómez", segunda)
        self.assertIn("Ana Pérez", segunda)
        self.assertIn("Marta Díaz", segunda)

    def test_seccion_strategy_muestra_las_tres_tarifas(self) -> None:
        seccion = seccion_de(ejecutar_demo(), 4)
        self.assertIn("[Temporada Alta] Recargo del 30% sobre $280.00: total $364.00", seccion)
        self.assertIn("[Temporada Baja] Descuento del 20% sobre $135.50: total $108.40", seccion)
        self.assertIn("[Corporativa - Acme S.A.] Descuento del 10% sobre $350.00: total $315.00",
                      seccion)
        self.assertEqual(seccion.count("¡Cotización confirmada!"), 3)

    def test_seccion_builder_reutiliza_habitaciones_del_factory(self) -> None:
        seccion = seccion_de(ejecutar_demo(), 5)
        self.assertIn("Doble 101 | $80.00/noche", seccion)
        self.assertIn("Suite 501 | $200.00/noche", seccion)
        self.assertIn("Suite 301 | $150.00/noche", seccion)

    def test_seccion_builder_muestra_servicio_estandar_y_premium(self) -> None:
        seccion = seccion_de(ejecutar_demo(), 5)
        self.assertIn("Servicio: Estándar ($10.00)", seccion)
        self.assertIn("Servicio: Premium ($40.00)", seccion)
        self.assertIn("TOTAL: $250.00", seccion)
        self.assertIn("TOTAL: $761.00", seccion)
        self.assertIn("Seguro de cancelación: No", seccion)
        self.assertIn("Seguro de cancelación: Sí (+$21.00)", seccion)

    def test_seccion_decorator_apila_los_tres_servicios(self) -> None:
        seccion = seccion_de(ejecutar_demo(), 6)
        self.assertIn(
            "Suite Presidencial + Desayuno incluido + Seguro de viaje + Late checkout", seccion
        )
        for precio in ("$899.99", "$914.99", "$933.29", "$958.29"):
            self.assertIn("Precio: " + precio, seccion)

    def test_seccion_adapter_muestra_los_dos_proveedores(self) -> None:
        seccion = seccion_de(ejecutar_demo(), 7)
        self.assertIn("[Taxi] Costo: $6.25 | Minutos estimados: 10", seccion)
        self.assertIn("[Taxi] Identificador: TAXI-RES-001-PAL", seccion)
        self.assertIn("[Shuttle] Costo: $6.79 | Minutos estimados: 20", seccion)
        self.assertIn("[Shuttle] Identificador: SHTRES-001Z1", seccion)

    def test_seccion_chain_aprueba_una_reserva_y_rechaza_dos(self) -> None:
        seccion = seccion_de(ejecutar_demo(), 8)
        self.assertEqual(seccion.count("Resultado: APROBADA"), 1)
        self.assertEqual(seccion.count("Resultado: RECHAZADA"), 2)
        self.assertIn("[Régimen] RECHAZADO", seccion)
        self.assertIn("[Monto] RECHAZADO", seccion)


if __name__ == "__main__":
    unittest.main()

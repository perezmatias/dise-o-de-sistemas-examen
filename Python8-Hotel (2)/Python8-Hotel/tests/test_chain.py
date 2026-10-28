"""Tests del patrón Chain of Responsibility (validadores de reserva)."""

import unittest
from typing import Any, Dict

from patrones.comportamiento.chain import (
    ValidadorDisponibilidad,
    ValidadorHuesped,
    ValidadorMontoMaximo,
    ValidadorRegimen,
    ValidadorReserva,
)
from tests.utilidades import capturar_salida


def reserva_valida(**cambios: Any) -> Dict[str, Any]:
    """Devuelve una reserva válida, opcionalmente con campos modificados."""
    reserva = {
        "habitaciones": ["Doble 101"],
        "regimen": "desayuno",
        "huesped": "Ana Pérez",
        "total": 100.0,
    }
    reserva.update(cambios)
    return reserva


class TestCadenaCompleta(unittest.TestCase):
    """Verifica el recorrido Disponibilidad → Régimen → Huésped → Monto máximo."""

    def setUp(self) -> None:
        self.cadena = ValidadorDisponibilidad()
        self.cadena.set_siguiente(ValidadorRegimen()) \
            .set_siguiente(ValidadorHuesped()) \
            .set_siguiente(ValidadorMontoMaximo())

    def _validar(self, reserva: Any) -> bool:
        resultado, _ = capturar_salida(lambda: self.cadena.validar(reserva))
        return resultado

    def test_reserva_valida_pasa_toda_la_cadena(self) -> None:
        self.assertTrue(self._validar(reserva_valida()))

    def test_reserva_valida_imprime_los_cuatro_ok_en_orden(self) -> None:
        _, salida = capturar_salida(lambda: self.cadena.validar(reserva_valida()))
        posiciones = [salida.index(etiqueta) for etiqueta in (
            "[Disponibilidad] OK", "[Régimen] OK", "[Huésped] OK", "[Monto] OK")]
        self.assertEqual(posiciones, sorted(posiciones))

    def test_rechazo_corta_la_cadena(self) -> None:
        _, salida = capturar_salida(
            lambda: self.cadena.validar(reserva_valida(regimen="todo incluido"))
        )
        self.assertIn("[Régimen] RECHAZADO", salida)
        self.assertNotIn("[Huésped]", salida)
        self.assertNotIn("[Monto]", salida)

    def test_rechazo_inicial_no_ejecuta_validadores_posteriores(self) -> None:
        _, salida = capturar_salida(
            lambda: self.cadena.validar(reserva_valida(habitaciones=[]))
        )
        self.assertIn("[Disponibilidad] RECHAZADO", salida)
        self.assertNotIn("[Régimen]", salida)

    def test_set_siguiente_devuelve_el_validador_recibido(self) -> None:
        a, b = ValidadorDisponibilidad(), ValidadorRegimen()
        self.assertIs(a.set_siguiente(b), b)

    def test_cadena_con_ciclo_lanza_value_error(self) -> None:
        a, b = ValidadorDisponibilidad(), ValidadorRegimen()
        a.set_siguiente(b)
        with self.assertRaises(ValueError):
            b.set_siguiente(a)

    def test_ciclo_largo_lanza_value_error(self) -> None:
        a, b, c = ValidadorDisponibilidad(), ValidadorRegimen(), ValidadorHuesped()
        a.set_siguiente(b).set_siguiente(c)
        with self.assertRaises(ValueError):
            c.set_siguiente(a)

    def test_validador_no_puede_apuntarse_a_si_mismo(self) -> None:
        a = ValidadorDisponibilidad()
        with self.assertRaises(ValueError):
            a.set_siguiente(a)

    def test_ciclo_rechazado_no_modifica_la_cadena(self) -> None:
        a, b = ValidadorDisponibilidad(), ValidadorRegimen()
        a.set_siguiente(b)
        with self.assertRaises(ValueError):
            b.set_siguiente(a)
        self.assertIsNone(b._siguiente)
        self.assertTrue(self._validar_con(a, reserva_valida()))

    def _validar_con(self, validador: ValidadorReserva, reserva: Any) -> bool:
        resultado, _ = capturar_salida(lambda: validador.validar(reserva))
        return resultado

    def test_cadena_sin_siguiente_aprueba_al_final(self) -> None:
        self.assertTrue(self._validar_con(ValidadorDisponibilidad(), reserva_valida()))

    def test_validador_reserva_es_abstracto(self) -> None:
        with self.assertRaises(TypeError):
            ValidadorReserva()  # type: ignore[abstract]


class TestValidadoresIndividuales(unittest.TestCase):
    """Verifica cada regla, incluyendo datos faltantes o mal tipados."""

    def _validar(self, validador: ValidadorReserva, reserva: Any) -> bool:
        resultado, _ = capturar_salida(lambda: validador.validar(reserva))
        return resultado

    # --- Disponibilidad ---------------------------------------------------

    def test_disponibilidad_rechaza_reserva_sin_habitaciones(self) -> None:
        validador = ValidadorDisponibilidad()
        self.assertFalse(self._validar(validador, reserva_valida(habitaciones=[])))
        self.assertFalse(self._validar(validador, reserva_valida(habitaciones=None)))

    def test_disponibilidad_rechaza_habitaciones_faltantes(self) -> None:
        reserva = reserva_valida()
        del reserva["habitaciones"]
        self.assertFalse(self._validar(ValidadorDisponibilidad(), reserva))

    def test_disponibilidad_rechaza_tipos_incorrectos_sin_excepcion(self) -> None:
        for valor in ("x", 1, True, {"x": 1}, ("x",), None, []):
            with self.subTest(valor=valor):
                reserva = reserva_valida(habitaciones=valor)
                self.assertFalse(self._validar(ValidadorDisponibilidad(), reserva))

    def test_disponibilidad_informa_la_cantidad_de_habitaciones(self) -> None:
        reserva = reserva_valida(habitaciones=["A", "B", "C"])
        _, salida = capturar_salida(lambda: ValidadorDisponibilidad().validar(reserva))
        self.assertIn("  [Disponibilidad] OK: 3 habitación(es) solicitada(s).", salida)

    def test_disponibilidad_informa_el_motivo_del_rechazo(self) -> None:
        reserva = reserva_valida(habitaciones=[])
        _, salida = capturar_salida(lambda: ValidadorDisponibilidad().validar(reserva))
        self.assertIn(
            "  [Disponibilidad] RECHAZADO: la reserva no incluye habitaciones.", salida
        )

    # --- Régimen ----------------------------------------------------------

    def test_regimen_es_insensible_a_mayusculas_y_espacios(self) -> None:
        validador = ValidadorRegimen()
        self.assertTrue(self._validar(validador, reserva_valida(regimen="Desayuno")))
        self.assertTrue(self._validar(validador, reserva_valida(regimen="  PENSION COMPLETA ")))

    def test_regimen_acepta_los_cuatro_regimenes(self) -> None:
        for regimen in ("solo alojamiento", "desayuno", "media pension", "pension completa"):
            with self.subTest(regimen=regimen):
                self.assertTrue(
                    self._validar(ValidadorRegimen(), reserva_valida(regimen=regimen))
                )

    def test_regimen_rechaza_regimen_desconocido(self) -> None:
        self.assertFalse(self._validar(ValidadorRegimen(), reserva_valida(regimen="all inclusive")))

    def test_regimen_rechaza_none_sin_romper(self) -> None:
        self.assertFalse(self._validar(ValidadorRegimen(), reserva_valida(regimen=None)))

    def test_regimen_rechaza_regimen_faltante(self) -> None:
        reserva = reserva_valida()
        del reserva["regimen"]
        self.assertFalse(self._validar(ValidadorRegimen(), reserva))

    def test_regimen_rechaza_tipos_no_texto(self) -> None:
        for valor in (1, True, ["desayuno"]):
            with self.subTest(valor=valor):
                self.assertFalse(self._validar(ValidadorRegimen(), reserva_valida(regimen=valor)))

    def test_regimen_lista_aceptados_en_orden_determinista(self) -> None:
        _, salida = capturar_salida(
            lambda: ValidadorRegimen().validar(reserva_valida(regimen="all inclusive"))
        )
        self.assertIn(
            "Aceptados: desayuno, media pension, pension completa, solo alojamiento.", salida
        )

    def test_regimen_ok_muestra_el_regimen_normalizado(self) -> None:
        _, salida = capturar_salida(
            lambda: ValidadorRegimen().validar(reserva_valida(regimen=" Desayuno "))
        )
        self.assertIn("  [Régimen] OK: régimen 'desayuno' aceptado.", salida)

    # --- Huésped ----------------------------------------------------------

    def test_huesped_rechaza_nombre_corto(self) -> None:
        self.assertFalse(self._validar(ValidadorHuesped(), reserva_valida(huesped="Ana")))

    def test_huesped_acepta_nombre_en_el_limite(self) -> None:
        self.assertTrue(self._validar(ValidadorHuesped(), reserva_valida(huesped="Marta")))

    def test_huesped_ignora_espacios_al_contar_caracteres(self) -> None:
        self.assertFalse(self._validar(ValidadorHuesped(), reserva_valida(huesped="  Ana  ")))

    def test_huesped_rechaza_none_sin_romper(self) -> None:
        self.assertFalse(self._validar(ValidadorHuesped(), reserva_valida(huesped=None)))

    def test_huesped_rechaza_tipos_no_texto_y_faltante(self) -> None:
        for valor in (12345678, True, ["Ana Pérez"]):
            with self.subTest(valor=valor):
                self.assertFalse(self._validar(ValidadorHuesped(), reserva_valida(huesped=valor)))
        reserva = reserva_valida()
        del reserva["huesped"]
        self.assertFalse(self._validar(ValidadorHuesped(), reserva))

    def test_huesped_informa_el_motivo_del_rechazo(self) -> None:
        _, salida = capturar_salida(
            lambda: ValidadorHuesped().validar(reserva_valida(huesped="Ana"))
        )
        self.assertIn(
            "  [Huésped] RECHAZADO: nombre incompleto (mínimo 5 caracteres).", salida
        )

    # --- Monto máximo -----------------------------------------------------

    def test_monto_rechaza_total_sobre_el_limite(self) -> None:
        self.assertFalse(self._validar(ValidadorMontoMaximo(), reserva_valida(total=19999.99)))

    def test_monto_acepta_total_en_el_limite(self) -> None:
        self.assertTrue(self._validar(ValidadorMontoMaximo(), reserva_valida(total=10000.00)))

    def test_monto_rechaza_apenas_sobre_el_limite(self) -> None:
        self.assertFalse(self._validar(ValidadorMontoMaximo(), reserva_valida(total=10000.01)))

    def test_monto_rechaza_total_negativo(self) -> None:
        self.assertFalse(self._validar(ValidadorMontoMaximo(), reserva_valida(total=-100)))

    def test_monto_rechaza_total_no_numerico_sin_romper(self) -> None:
        self.assertFalse(self._validar(ValidadorMontoMaximo(), reserva_valida(total="100")))
        self.assertFalse(self._validar(ValidadorMontoMaximo(), reserva_valida(total=None)))

    def test_monto_rechaza_no_finitos_y_conserva_limites(self) -> None:
        casos = ((float("nan"), False), (float("inf"), False), (float("-inf"), False),
                 (True, False), (False, False), (0, True), (10000, True), (10000.01, False))
        for total, esperado in casos:
            with self.subTest(total=total):
                resultado = self._validar(ValidadorMontoMaximo(), {"total": total})
                self.assertEqual(resultado, esperado)

    def test_monto_rechaza_entero_fuera_de_rango_sin_excepcion(self) -> None:
        for total in (10 ** 400, -(10 ** 400)):
            with self.subTest(total=total):
                self.assertFalse(self._validar(ValidadorMontoMaximo(), {"total": total}))

    def test_monto_ausente_equivale_a_cero(self) -> None:
        # HU-039: un total faltante se interpreta como cero
        self.assertTrue(self._validar(ValidadorMontoMaximo(), {}))

    def test_monto_informa_el_motivo_del_rechazo(self) -> None:
        _, salida = capturar_salida(
            lambda: ValidadorMontoMaximo().validar(reserva_valida(total=20000))
        )
        self.assertIn("[Monto] RECHAZADO: total $20000.00 supera el límite de $10000.00.", salida)

    def test_constantes_de_los_validadores(self) -> None:
        self.assertEqual(ValidadorMontoMaximo.MONTO_MAXIMO, 10000.00)
        self.assertEqual(ValidadorHuesped.LONGITUD_MINIMA, 5)
        self.assertEqual(
            ValidadorRegimen.REGIMENES_ACEPTADOS,
            {"solo alojamiento", "desayuno", "media pension", "pension completa"},
        )

    # --- Reserva que no es un diccionario ---------------------------------

    def test_validadores_rechazan_reserva_que_no_es_diccionario(self) -> None:
        tipos = (ValidadorDisponibilidad, ValidadorRegimen, ValidadorHuesped,
                 ValidadorMontoMaximo)
        for tipo in tipos:
            for reserva in (None, [], "reserva", 42):
                with self.subTest(tipo=tipo, reserva=reserva):
                    self.assertFalse(self._validar(tipo(), reserva))

    def test_reserva_no_diccionario_informa_que_se_requiere_un_diccionario(self) -> None:
        _, salida = capturar_salida(lambda: ValidadorHuesped().validar(None))
        self.assertIn("  [Reserva] RECHAZADO: se requiere un diccionario.", salida)

    def test_cadena_rechaza_nan_y_disponibilidad_invalida(self) -> None:
        cadena = ValidadorDisponibilidad()
        cadena.set_siguiente(ValidadorRegimen()).set_siguiente(ValidadorHuesped()) \
            .set_siguiente(ValidadorMontoMaximo())
        for cambios in ({"habitaciones": "x"}, {"total": float("nan")}):
            with self.subTest(cambios=cambios):
                self.assertFalse(self._validar(cadena, reserva_valida(**cambios)))


if __name__ == "__main__":
    unittest.main()

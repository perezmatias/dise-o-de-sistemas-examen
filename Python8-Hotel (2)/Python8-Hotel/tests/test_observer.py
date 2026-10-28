"""Tests del patrón Observer (Hotel y Huesped)."""

import unittest
from typing import List

from patrones.comportamiento.observer import Huesped, Hotel, Observer
from tests.utilidades import capturar_salida


class ObservadorEspia(Observer):
    """Observador de prueba que registra los mensajes recibidos."""

    def __init__(self) -> None:
        self.mensajes: List[str] = []

    def actualizar(self, mensaje: str) -> None:
        self.mensajes.append(mensaje)


class ObservadorQueSeDesuscribe(ObservadorEspia):
    """Observador que se desuscribe del hotel al recibir el primer aviso."""

    def __init__(self, hotel: Hotel) -> None:
        super().__init__()
        self._hotel = hotel

    def actualizar(self, mensaje: str) -> None:
        super().actualizar(mensaje)
        self._hotel.desuscribir(self)


class TestHotel(unittest.TestCase):
    """Verifica suscripción, desuscripción y notificación."""

    def setUp(self) -> None:
        self.hotel = Hotel("Test")

    def test_notifica_a_todos_los_suscritos(self) -> None:
        a, b = ObservadorEspia(), ObservadorEspia()
        capturar_salida(lambda: (self.hotel.suscribir(a), self.hotel.suscribir(b)))
        capturar_salida(lambda: self.hotel.nueva_promocion("20% off"))
        self.assertEqual(a.mensajes, ["Nueva promoción: 20% off"])
        self.assertEqual(b.mensajes, ["Nueva promoción: 20% off"])

    def test_no_notifica_a_desuscritos(self) -> None:
        a = ObservadorEspia()
        capturar_salida(lambda: (self.hotel.suscribir(a), self.hotel.desuscribir(a)))
        capturar_salida(lambda: self.hotel.nueva_promocion("x"))
        self.assertEqual(a.mensajes, [])

    def test_rechaza_suscripcion_duplicada(self) -> None:
        huesped = Huesped("Ana")
        capturar_salida(lambda: (self.hotel.suscribir(huesped), self.hotel.suscribir(huesped)))
        self.assertEqual(len(self.hotel._huespedes), 1)

    def test_suscripcion_duplicada_informa_sin_lanzar_error(self) -> None:
        huesped = Huesped("Ana")
        capturar_salida(lambda: self.hotel.suscribir(huesped))
        _, salida = capturar_salida(lambda: self.hotel.suscribir(huesped))
        self.assertIn("ya está suscrito", salida)

    def test_rechaza_objetos_que_no_son_observer(self) -> None:
        with self.assertRaises(TypeError) as contexto:
            self.hotel.suscribir("no soy observer")
        # Mensaje exacto exigido por HU-024 (historias1.md)
        self.assertEqual(str(contexto.exception), "El objeto debe ser una instancia de Observer")

    def test_objeto_rechazado_no_queda_suscrito(self) -> None:
        with self.assertRaises(TypeError):
            self.hotel.suscribir(None)
        self.assertEqual(self.hotel._huespedes, [])

    def test_desuscribir_inexistente_no_lanza_error(self) -> None:
        _, salida = capturar_salida(lambda: self.hotel.desuscribir(Huesped("Ana")))
        self.assertIn("no está suscrito", salida)

    def test_desuscribir_conserva_a_los_demas(self) -> None:
        a, b = ObservadorEspia(), ObservadorEspia()
        capturar_salida(lambda: (self.hotel.suscribir(a), self.hotel.suscribir(b)))
        capturar_salida(lambda: self.hotel.desuscribir(a))
        self.assertEqual(self.hotel._huespedes, [b])

    def test_desuscribirse_durante_la_notificacion_no_saltea_a_otros(self) -> None:
        que_se_va = ObservadorQueSeDesuscribe(self.hotel)
        siguiente = ObservadorEspia()
        capturar_salida(
            lambda: (self.hotel.suscribir(que_se_va), self.hotel.suscribir(siguiente))
        )
        capturar_salida(lambda: self.hotel.nueva_promocion("oferta"))
        self.assertEqual(que_se_va.mensajes, ["Nueva promoción: oferta"])
        self.assertEqual(siguiente.mensajes, ["Nueva promoción: oferta"])
        self.assertEqual(self.hotel._huespedes, [siguiente])

    def test_notificar_huespedes_envia_el_mensaje_tal_cual(self) -> None:
        a = ObservadorEspia()
        capturar_salida(lambda: self.hotel.suscribir(a))
        capturar_salida(lambda: self.hotel.notificar_huespedes("Piscina cerrada"))
        self.assertEqual(a.mensajes, ["Piscina cerrada"])

    def test_notificar_sin_suscriptores_informa_cero_huespedes(self) -> None:
        _, salida = capturar_salida(lambda: self.hotel.notificar_huespedes("hola"))
        self.assertIn("--- Notificando a 0 huéspedes ---", salida)

    def test_nueva_promocion_imprime_encabezado_con_el_nombre_del_hotel(self) -> None:
        _, salida = capturar_salida(lambda: self.hotel.nueva_promocion("2x1"))
        self.assertIn("¡Nueva promoción en Test!", salida)

    def test_suscribir_imprime_confirmacion(self) -> None:
        _, salida = capturar_salida(lambda: self.hotel.suscribir(Huesped("Ana")))
        self.assertEqual(salida.strip(), "Huésped suscrito al hotel Test")

    def test_desuscribir_imprime_confirmacion(self) -> None:
        huesped = Huesped("Ana")
        capturar_salida(lambda: self.hotel.suscribir(huesped))
        _, salida = capturar_salida(lambda: self.hotel.desuscribir(huesped))
        self.assertEqual(salida.strip(), "Huésped desuscrito del hotel Test")

    def test_nombre_del_hotel(self) -> None:
        self.assertEqual(self.hotel.nombre, "Test")
        self.assertEqual(Hotel("Hotel Los Cortez").nombre, "Hotel Los Cortez")


class TestHuesped(unittest.TestCase):
    """Verifica el observador concreto."""

    def test_actualizar_imprime_el_mensaje(self) -> None:
        _, salida = capturar_salida(lambda: Huesped("Ana").actualizar("hola"))
        self.assertEqual(salida.strip(), "Huésped Ana recibió notificación: hola")

    def test_actualizar_usa_el_nombre_de_cada_huesped(self) -> None:
        _, salida = capturar_salida(lambda: Huesped("Luis").actualizar("chau"))
        self.assertEqual(salida.strip(), "Huésped Luis recibió notificación: chau")

    def test_nombre_y_repr(self) -> None:
        huesped = Huesped("Ana")
        self.assertEqual(huesped.nombre, "Ana")
        self.assertEqual(repr(huesped), "Huesped('Ana')")

    def test_huesped_es_un_observer(self) -> None:
        self.assertIsInstance(Huesped("Ana"), Observer)

    def test_observer_es_abstracto(self) -> None:
        with self.assertRaises(TypeError):
            Observer()  # type: ignore[abstract]


if __name__ == "__main__":
    unittest.main()

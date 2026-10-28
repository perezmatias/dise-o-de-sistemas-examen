"""Comprueba el banco del examen y ejecuta las claves contra las clases del hotel."""

import importlib
import inspect
import io
import json
import unittest
from collections import Counter
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Dict, List

from patrones.creacionales.singleton import CentralReservas


RAIZ = Path(__file__).resolve().parent.parent
PAQUETES = (
    "patrones.creacionales.singleton",
    "patrones.creacionales.factory",
    "patrones.creacionales.builder",
    "patrones.estructurales.decorator",
    "patrones.estructurales.adapter",
    "patrones.comportamiento.observer",
    "patrones.comportamiento.strategy",
    "patrones.comportamiento.chain",
)
TEMAS = {
    "Singleton", "Factory Method", "Builder", "Decorator", "Adapter",
    "Observer", "Strategy", "Chain of Responsibility",
}


def ejecutar_pregunta(pregunta: Dict[str, Any]) -> Dict[str, Any]:
    """Ejecuta una pregunta aislada y captura solo la salida del código visible."""
    espacio: Dict[str, Any] = {}
    for paquete in PAQUETES:
        modulo = importlib.import_module(paquete)
        for nombre, valor in vars(modulo).items():
            if not nombre.startswith("_") and inspect.isclass(valor):
                espacio[nombre] = valor
    codigo = pregunta["codigo"]
    for indice, inciso in enumerate(pregunta["incisos"], 1):
        codigo = codigo.replace("({})".format(indice), inciso["respuesta"])
    verificacion = pregunta["verificacion"]
    instancia_anterior = CentralReservas._instance
    CentralReservas._instance = None
    try:
        with redirect_stdout(io.StringIO()):
            exec(verificacion["preparacion"], espacio)
        salida = io.StringIO()
        espacio["salida"] = salida
        with redirect_stdout(salida):
            exec(codigo, espacio)
        resultados = [
            None if expresion is None else eval(expresion, espacio)
            for expresion in verificacion["expresiones"]
        ]
        return {"resultados": resultados, "salida": salida.getvalue()}
    finally:
        CentralReservas._instance = instancia_anterior


class TestEjecucionPreguntas(unittest.TestCase):
    """Protege la captura del fragmento real y las verificaciones parciales."""

    def test_captura_fragmento_sin_ejecutarlo_en_preparacion(self) -> None:
        """Cuenta solo los efectos producidos por el fragmento mostrado."""
        pregunta = {
            "codigo": "a = CentralReservas()\nb = CentralReservas()",
            "incisos": [{"respuesta": "True"}, {"respuesta": "1"}],
            "verificacion": {
                "preparacion": "",
                "expresiones": [
                    "a is b", "salida.getvalue().count('Conectando a la central')",
                ],
            },
        }
        resultado = ejecutar_pregunta(pregunta)
        self.assertEqual(resultado["resultados"], [True, 1])
        self.assertEqual(resultado["salida"].count("Conectando a la central"), 1)

    def test_verificacion_parcial_no_evalua_inciso_conceptual(self) -> None:
        """Permite comprobar una salida y dejar una razón conceptual para revisión."""
        pregunta = {
            "codigo": "print('Salida real')\nvalor = 90",
            "incisos": [{"respuesta": "90"}, {"respuesta": "Razón conceptual"}],
            "verificacion": {"preparacion": "", "expresiones": ["valor", None]},
        }
        resultado = ejecutar_pregunta(pregunta)
        self.assertEqual(resultado["resultados"], [90, None])
        self.assertEqual(resultado["salida"], "Salida real\n")

    def test_preparacion_no_contamina_salida_visible(self) -> None:
        """Excluye diagnósticos del montaje y admite un primer inciso conceptual."""
        pregunta = {
            "codigo": "print('Fragmento')",
            "incisos": [{"respuesta": "Conceptual"}, {"respuesta": "1"}],
            "verificacion": {
                "preparacion": "print('Preparación')",
                "expresiones": [None, "len(salida.getvalue().splitlines())"],
            },
        }
        resultado = ejecutar_pregunta(pregunta)
        self.assertEqual(resultado["resultados"], [None, 1])
        self.assertEqual(resultado["salida"], "Fragmento\n")


class TestEvaluacionContenido(unittest.TestCase):
    """Verifica estructura, cobertura temática y respuestas reproducibles."""

    @classmethod
    def setUpClass(cls) -> None:
        """Carga los dos bancos mantenidos junto al examen HTML."""
        cls.preguntas: List[Dict[str, Any]] = []
        for nombre in ("preguntas_01_20.json", "preguntas_21_40.json"):
            ruta = RAIZ / "evaluacion" / nombre
            cls.preguntas.extend(json.loads(ruta.read_text(encoding="utf-8")))

    def test_identificadores_temas_y_niveles(self) -> None:
        """Conserva las cuarenta preguntas y los dos niveles del examen."""
        self.assertEqual([p["id"] for p in self.preguntas], list(range(1, 41)))
        self.assertEqual({p["tema"] for p in self.preguntas}, TEMAS)
        self.assertEqual(Counter(p["tema"] for p in self.preguntas),
                         {tema: 5 for tema in TEMAS})
        self.assertEqual(Counter(p["nivel"] for p in self.preguntas), {1: 20, 2: 20})
        self.assertTrue(all(p["nivel"] == 1 for p in self.preguntas[:20]))
        self.assertTrue(all(p["nivel"] == 2 for p in self.preguntas[20:]))

    def test_inciso_opciones_y_clave(self) -> None:
        """Exige dos respuestas por pregunta y cuatro opciones sin ambigüedad."""
        for pregunta in self.preguntas:
            with self.subTest(pregunta=pregunta["id"]):
                self.assertEqual(len(pregunta["incisos"]), 2)
                for inciso in pregunta["incisos"]:
                    self.assertIsInstance(inciso["respuesta"], str)
                    self.assertTrue(inciso["respuesta"].strip())
                    opciones = inciso["opciones"]
                    if opciones is None:
                        float(inciso["respuesta"])
                        self.assertIn(inciso.get("tipo_respuesta"), ("entero", "decimal"))
                        if inciso["tipo_respuesta"] == "entero":
                            self.assertEqual(float(inciso["respuesta"]),
                                             int(inciso["respuesta"]))
                    else:
                        self.assertEqual(len(opciones), 4)
                        self.assertEqual(len(set(opciones)), 4)
                        self.assertTrue(all(isinstance(o, str) for o in opciones))
                        self.assertIn(inciso["respuesta"], opciones)

    def test_claves_ejecutables_contra_implementacion_real(self) -> None:
        """Resuelve los huecos y compara los resultados reales con cada clave."""
        for pregunta in self.preguntas:
            verificacion = pregunta["verificacion"]
            if verificacion is None:
                continue
            with self.subTest(pregunta=pregunta["id"]):
                expresiones = verificacion["expresiones"]
                self.assertEqual(len(expresiones), 2)
                resultados = ejecutar_pregunta(pregunta)["resultados"]
                for expresion, resultado, inciso in zip(
                        expresiones, resultados, pregunta["incisos"]):
                    if expresion is None:
                        continue
                    if inciso["opciones"] is None:
                        self.assertEqual(float(resultado), float(inciso["respuesta"]))
                    else:
                        self.assertEqual(str(resultado), inciso["respuesta"])

"""Tests de las convenciones de código declaradas en CLAUDE.md."""

import ast
import glob
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LONGITUD_MAXIMA = 100


def archivos_fuente() -> list:
    """Devuelve main.py y todos los módulos del paquete patrones."""
    patron = os.path.join(RAIZ, "patrones", "**", "*.py")
    return [os.path.join(RAIZ, "main.py")] + sorted(glob.glob(patron, recursive=True))


def _textos_literales(arbol: ast.AST) -> set:
    """Devuelve los strings literales del árbol (compatible con Python 3.6+)."""
    if sys.version_info >= (3, 8):
        return {n.value for n in ast.walk(arbol)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    return {n.s for n in ast.walk(arbol) if isinstance(n, ast.Str)}


class TestConvenciones(unittest.TestCase):
    """Verifica largo de línea y type hints en todo el código fuente."""

    def test_lineas_de_hasta_100_caracteres(self) -> None:
        excedidas = []
        for ruta in archivos_fuente():
            with open(ruta, encoding="utf-8") as archivo:
                for numero, linea in enumerate(archivo, start=1):
                    if len(linea.rstrip("\n")) > LONGITUD_MAXIMA:
                        excedidas.append("{}:{}".format(os.path.relpath(ruta, RAIZ), numero))
        self.assertEqual(excedidas, [])

    def test_todas_las_firmas_tienen_type_hints(self) -> None:
        sin_hints = []
        for ruta in archivos_fuente():
            with open(ruta, encoding="utf-8") as archivo:
                arbol = ast.parse(archivo.read())
            for nodo in ast.walk(arbol):
                if not isinstance(nodo, ast.FunctionDef):
                    continue
                parametros = [a for a in nodo.args.args if a.arg not in ("self", "cls")]
                if nodo.returns is None or any(a.annotation is None for a in parametros):
                    sin_hints.append(
                        "{}:{} {}".format(os.path.relpath(ruta, RAIZ), nodo.lineno, nodo.name)
                    )
        self.assertEqual(sin_hints, [])


    def test_no_hay_imports_sin_usar(self) -> None:
        sin_usar = []
        for ruta in archivos_fuente():
            if ruta.endswith("__init__.py"):
                continue  # los __init__ importan para re-exportar
            with open(ruta, encoding="utf-8") as archivo:
                arbol = ast.parse(archivo.read())
            importados = {}
            for nodo in ast.walk(arbol):
                if isinstance(nodo, (ast.Import, ast.ImportFrom)):
                    for alias in nodo.names:
                        importados[(alias.asname or alias.name).split(".")[0]] = nodo.lineno
            usados = {n.id for n in ast.walk(arbol) if isinstance(n, ast.Name)}
            usados |= _textos_literales(arbol)  # anotaciones como string: -> "PedidoBuilder"
            for nombre, linea in importados.items():
                if nombre not in usados:
                    sin_usar.append("{}:{} {}".format(os.path.relpath(ruta, RAIZ), linea, nombre))
        self.assertEqual(sin_usar, [])


if __name__ == "__main__":
    unittest.main()

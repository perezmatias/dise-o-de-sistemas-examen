"""
Utilidades compartidas por los tests.

Todo el proyecto comunica resultados vía print(), así que los tests necesitan
capturar stdout para verificar la salida sin ensuciar la consola.
"""

import contextlib
import io
from typing import Any, Callable, Tuple


def capturar_salida(funcion: Callable[[], Any]) -> Tuple[Any, str]:
    """Ejecuta una función capturando todo lo que imprime en stdout.

    Args:
        funcion: Callable sin argumentos a ejecutar.

    Returns:
        tuple: (valor retornado por la función, texto impreso en stdout).
    """
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        resultado = funcion()
    return resultado, buffer.getvalue()

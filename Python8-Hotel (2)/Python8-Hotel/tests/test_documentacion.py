"""Verifica ejecutando los ejemplos que el README refleja el programa."""

import os
import re
import subprocess
import sys
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent


class TestDocumentacion(unittest.TestCase):
    """Comprueba ejemplos independientes y salida completa publicada."""

    def _ejecutar(self, argumentos: list) -> str:
        entorno = os.environ.copy()
        entorno['PYTHONIOENCODING'] = 'utf-8'
        resultado = subprocess.run(
            [sys.executable] + argumentos, cwd=str(RAIZ), env=entorno,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', timeout=15,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(resultado.stderr, '')
        return resultado.stdout

    def test_salida_completa_readme_coincide_con_main(self) -> None:
        contenido = (RAIZ / 'README.md').read_text(encoding='utf-8')
        bloques = re.findall(r'```[^\n]*\n(.*?)```', contenido, re.S)
        salidas = [b for b in bloques if 'DEMOSTRACIÓN DE PATRONES DE DISEÑO EN PYTHON' in b]
        self.assertEqual(len(salidas), 1)
        self.assertEqual(self._ejecutar(['main.py']).strip(), salidas[0].strip())

    def test_ejemplos_python_readme_coinciden_con_su_salida_publicada(self) -> None:
        contenido = (RAIZ / 'README.md').read_text(encoding='utf-8')
        ejemplos = list(re.finditer(r'```python\s*\n(.*?)```', contenido, re.S))
        self.assertTrue(ejemplos)
        for numero, ejemplo in enumerate(ejemplos, 1):
            with self.subTest(ejemplo=numero):
                salida = re.match(
                    r'\s*\*\*Salida esperada:\*\*\s*\n```text\n(.*?)```',
                    contenido[ejemplo.end():], re.S,
                )
                self.assertIsNotNone(salida, 'Falta la salida esperada del ejemplo')
                self.assertEqual(self._ejecutar(['-c', ejemplo.group(1)]), salida.group(1))

"""Verifica estructura, contratos de respuestas y autonomía del examen generado."""

import json
import importlib.util
import shutil
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent


class DocumentoExamen(HTMLParser):
    """Recoge elementos para comprobar los vínculos reales del formulario."""

    def __init__(self) -> None:
        super().__init__()
        self.elementos = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        self.elementos.append((tag, dict(attrs)))


class TestEvaluacionHTML(unittest.TestCase):
    """Comprueba los controles que utiliza el alumno y sus claves publicadas."""

    def test_entregables_publicados_corresponden_al_banco_y_generador_actuales(self) -> None:
        """Detecta cambios de contenido o corrector que quedaron sin regenerar."""
        ruta = RAIZ / 'evaluacion/generar_examen.py'
        spec = importlib.util.spec_from_file_location('generador_examen', str(ruta))
        generador = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generador)
        preguntas = generador.cargar_preguntas()
        for nombre, contenido in (
                ('examen_patrones.html', generador.generar_html(preguntas)),
                ('guia_docente.md', generador.generar_guia(preguntas))):
            with self.subTest(archivo=nombre):
                self.assertEqual(
                    (RAIZ / 'evaluacion' / nombre).read_text(encoding='utf-8'), contenido,
                    'Regenerar con python evaluacion/generar_examen.py',
                )

    def _comprobar_corrector(self, escenario: str) -> None:
        """Ejecuta el JavaScript real; omite explícitamente si falta Node.js."""
        node = shutil.which('node')
        if node is None:
            self.skipTest('Node.js no está instalado: corrector JavaScript sin ejecutar')
        resultado = subprocess.run(
            [node, str(RAIZ / 'tests/evaluacion_corrector.js'),
             str(RAIZ / 'evaluacion/examen_patrones.html'), escenario],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
            timeout=15,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)

    def test_corrector_rechaza_fracciones_de_conteos_y_acepta_importes(self) -> None:
        self._comprobar_corrector('numeros')

    def test_corrector_revela_corrige_totaliza_e_invalida_ediciones(self) -> None:
        self._comprobar_corrector('estado')

    def test_html_contiene_cuarenta_preguntas_y_ochenta_respuestas_accesibles(self) -> None:
        self.assertTrue((RAIZ / 'evaluacion/examen_patrones.html').is_file())
        documento = DocumentoExamen()
        documento.feed((RAIZ / 'evaluacion/examen_patrones.html').read_text(encoding='utf-8'))
        elementos = documento.elementos
        ids = [a['id'] for _, a in elementos if 'id' in a]
        self.assertEqual(len(ids), len(set(ids)))
        preguntas = [a['id'] for t, a in elementos if t == 'section' and a.get('class') == 'q']
        self.assertEqual(preguntas, ['q{}'.format(i) for i in range(1, 41)])
        campos = [a for t, a in elementos if t in ('input', 'select')]
        self.assertEqual(len(campos), 80)
        etiquetas = [a.get('for') for t, a in elementos if t == 'label']
        for campo in campos:
            self.assertIn(campo['id'], etiquetas)
            self.assertIn(campo['aria-describedby'], ids)
        for _, atributos in elementos:
            for atributo in ('aria-controls', 'aria-describedby'):
                if atributo in atributos:
                    self.assertIn(atributos[atributo], ids)
            if atributos.get('href', '').startswith('#'):
                self.assertIn(atributos['href'][1:], ids)

    def test_claves_opciones_y_recursos_corresponden_al_banco_local(self) -> None:
        self.assertTrue((RAIZ / 'evaluacion/examen_patrones.html').is_file())
        documento = DocumentoExamen()
        documento.feed((RAIZ / 'evaluacion/examen_patrones.html').read_text(encoding='utf-8'))
        bancos = sorted((RAIZ / 'evaluacion').glob('preguntas_*.json'))
        preguntas = [p for banco in bancos for p in json.loads(banco.read_text(encoding='utf-8'))]
        campos = [a for t, a in documento.elementos if t in ('input', 'select')]
        self.assertEqual(len(preguntas), 40)
        for campo, inciso in zip(campos, [i for p in preguntas for i in p['incisos']]):
            self.assertEqual(campo['data-answer'], inciso['respuesta'])
            if inciso['opciones'] is None:
                self.assertEqual(campo.get('data-tipo-respuesta'), inciso['tipo_respuesta'])
        opciones = [a.get('value') for t, a in documento.elementos if t == 'option']
        esperadas = [valor for p in preguntas for i in p['incisos']
                     if i['opciones'] for valor in [''] + i['opciones']]
        self.assertEqual(opciones, esperadas)
        for tag, atributos in documento.elementos:
            recurso = atributos.get('src') or atributos.get('href')
            if recurso and not recurso.startswith('#'):
                self.assertNotIn('://', recurso)
                self.assertTrue((RAIZ / 'evaluacion' / recurso).is_file())


if __name__ == '__main__':
    unittest.main()

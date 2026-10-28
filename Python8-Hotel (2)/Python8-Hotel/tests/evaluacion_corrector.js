// Ejecuta el corrector publicado con un DOM mínimo, sin navegador ni paquetes externos.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(process.argv[2], 'utf8');
const script = html.match(/<script type="module">([\s\S]*?)<\/script>/);
assert.ok(script, 'El examen debe incluir su corrector ejecutable');

function control(value, answer, tagName, tipo) {
  const atributos = {};
  const clases = new Set();
  const feedback = { textContent: '' };
  return {
    value, tagName, dataset: { answer, tipoRespuesta: tipo },
    parentElement: { querySelector: () => feedback },
    feedback, atributos,
    classList: {
      toggle: (clase, activo) => activo ? clases.add(clase) : clases.delete(clase),
      remove: (...nombres) => nombres.forEach(nombre => clases.delete(nombre)),
    },
    setAttribute: (nombre, valor) => { atributos[nombre] = valor; },
    removeAttribute: nombre => { delete atributos[nombre]; },
  };
}

function pregunta(campos) {
  const nodos = {};
  for (const nombre of ['.score', '.exp', '.corr', '.ver']) {
    nodos[nombre] = {
      textContent: '', hidden: true, atributos: {},
      setAttribute(nombre, valor) { this.atributos[nombre] = valor; },
      addEventListener(nombre, accion) { this[nombre] = accion; },
    };
  }
  return {
    dataset: {}, nodos, campos,
    querySelector: nombre => nodos[nombre],
    querySelectorAll: nombre => nombre === '[data-answer]' ? campos : [],
    addEventListener(nombre, accion) { this[nombre] = accion; },
  };
}

const uno = pregunta([
  control('True', 'True', 'SELECT'), control('1', '1', 'INPUT', 'entero'),
]);
const dos = pregunta([
  control('5,50', '5.5', 'INPUT', 'decimal'), control('', '10', 'INPUT', 'entero'),
]);
const global = { textContent: '' };
const todo = { addEventListener(nombre, accion) { this[nombre] = accion; } };
const contexto = vm.createContext({
  document: {
    querySelectorAll: () => [uno, dos],
    querySelector: nombre => nombre === '#global' ? global : todo,
  },
});
vm.runInContext(script[1], contexto);

if (process.argv[3] === 'numeros') {
  const correcta = contexto.esCorrecta;
  assert.equal(correcta('1.0000000001', '1', 'entero'), false);
  assert.equal(correcta('0.0000000001', '0', 'entero'), false);
  assert.equal(correcta('1.0000000000000001', '1', 'entero'), false);
  assert.equal(correcta('1,0', '1', 'entero'), true);
  assert.equal(correcta('117,30', '117.3', 'decimal'), true);
  for (const valor of ['', 'NaN', 'Infinity', '1e2', '1,2,3']) {
    assert.equal(correcta(valor, '0', 'entero'), false);
    assert.equal(correcta(valor, '0', 'decimal'), false);
  }
} else {
  assert.match(global.textContent, /^0 \/ 80/);
  uno.nodos['.ver'].click();
  assert.equal(uno.nodos['.exp'].hidden, false);
  assert.equal(uno.nodos['.ver'].atributos['aria-expanded'], 'true');
  assert.equal(uno.dataset.score, undefined);
  assert.equal(uno.campos[0].value, 'True');
  todo.click();
  assert.equal(uno.dataset.score, 2);
  assert.equal(dos.dataset.score, 1);
  assert.match(global.textContent, /^3 \/ 80.*2 \/ 40.*0\.38 \/ 10$/);
  assert.equal(dos.campos[1].feedback.textContent, 'Sin responder.');
  assert.equal(dos.campos[1].atributos['aria-invalid'], 'true');
  uno.campos[0].value = 'False';
  uno.input();
  assert.equal(uno.dataset.score, undefined);
  assert.match(global.textContent, /^1 \/ 80.*1 \/ 40/);
  assert.equal(uno.campos[0].feedback.textContent, '');
  uno.nodos['.corr'].click();
  assert.equal(uno.dataset.score, 1);
  assert.equal(uno.campos[0].feedback.textContent, 'Incorrecto.');
  assert.equal(uno.campos[1].feedback.textContent, 'Correcto.');
}

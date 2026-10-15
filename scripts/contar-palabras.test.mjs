import { describe, it } from 'node:test';
import assert from 'node:assert';
import words from './contar-palabras.mjs';

describe('contar-palabras', () => {
  it('el conteo es mayor que 100', () => {
    assert.ok(words.length > 100, `esperado > 100, obtenido ${words.length}`);
  });
});

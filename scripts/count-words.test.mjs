import { describe, it } from 'node:test';
import assert from 'node:assert';
import words from './count-words.mjs';

describe('count-words', () => {
  it('the count is greater than 100', () => {
    assert.ok(words.length > 100, `expected > 100, got ${words.length}`);
  });
});

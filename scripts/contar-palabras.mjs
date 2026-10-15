import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const text = readFileSync(join(__dirname, '..', 'brief.md'), 'utf8');
const words = text.split(/\s+/).filter((w) => w.length > 0);
console.log(words.length);

export default words;

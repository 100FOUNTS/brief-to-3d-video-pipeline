// Saca fotogramas sueltos de una escena con seek(t) y los junta en una hoja de contactos. Sirve para iterar sin renderizar el vídeo.
// Uso: node scripts/capturar.mjs webgl/agua.html 0,2.5,5,7.5 out/frames/agua-hoja.png [columnas]
import { chromium } from 'playwright-core';
import { spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve, dirname } from 'node:path';
import { pathToFileURL } from 'node:url';

const [escena, tiempos, salida, columnas = '4'] = process.argv.slice(2);
if (!escena || !tiempos || !salida) { console.error('Uso: node scripts/capturar.mjs escena.html t1,t2,... salida.png [columnas]'); process.exit(2); }
const ts = tiempos.split(',').map(Number);
const tmp = mkdtempSync(join(tmpdir(), 'cap-'));
mkdirSync(dirname(resolve(salida)), { recursive: true });

const nav = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
const p = await nav.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
const errores = [];
p.on('pageerror', (e) => errores.push(e.message)); p.on('console', (m) => m.type() === 'error' && errores.push(m.text()));
await p.goto(pathToFileURL(resolve(escena)).href + '#render');
const archivos = [];
for (const [i, t] of ts.entries()) {
  await p.evaluate((x) => window.seek(x), t);
  const f = join(tmp, `f${i}.png`);
  await p.screenshot({ path: f }); archivos.push(f);
}
await nav.close();
if (errores.length) console.error('Errores en la página:\n' + [...new Set(errores)].join('\n'));

const n = archivos.length, c = Math.min(Number(columnas), n), filas = Math.ceil(n / c);
const entradas = archivos.flatMap((f) => ['-i', f]);
const rellenos = Array.from({ length: filas * c - n }, () => ['-f', 'lavfi', '-i', 'color=c=0x0f1115:s=1920x1080:d=1']).flat();
const total = n + rellenos.length / 4;
const escalas = Array.from({ length: total }, (_, i) => `[${i}]scale=640:360[s${i}]`).join(';');
const filasF = Array.from({ length: filas }, (_, r) => { const e = Array.from({ length: c }, (_, k) => `[s${r * c + k}]`).join(''); return c > 1 ? `${e}hstack=inputs=${c}[r${r}]` : `${e}copy[r${r}]`; }).join(';');   // hstack exige >= 2 entradas
const apilado = filas > 1 ? `${Array.from({ length: filas }, (_, r) => `[r${r}]`).join('')}vstack=inputs=${filas}` : '[r0]copy';
const r = spawnSync('ffmpeg', ['-loglevel', 'error', '-y', ...entradas, ...rellenos, '-filter_complex', `${escalas};${filasF};${apilado}`, '-frames:v', '1', resolve(salida)], { stdio: 'inherit' });
process.exit(r.status ?? 1);

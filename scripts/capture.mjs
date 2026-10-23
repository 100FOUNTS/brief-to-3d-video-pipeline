// Takes single frames of a scene with seek(t) and joins them into a contact sheet. Useful for iterating without rendering the video.
// Usage: node scripts/capture.mjs webgl/water.html 0,2.5,5,7.5 out/frames/water-sheet.png [columns]
import { chromium } from 'playwright-core';
import { spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve, dirname } from 'node:path';
import { pathToFileURL } from 'node:url';

const [scene, times, output, columns = '4'] = process.argv.slice(2);
if (!scene || !times || !output) { console.error('Usage: node scripts/capture.mjs scene.html t1,t2,... output.png [columns]'); process.exit(2); }
const ts = times.split(',').map(Number);
const tmp = mkdtempSync(join(tmpdir(), 'cap-'));
mkdirSync(dirname(resolve(output)), { recursive: true });

const browser = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
const p = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
const errors = [];
p.on('pageerror', (e) => errors.push(e.message)); p.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
await p.goto(pathToFileURL(resolve(scene)).href + '#render');
const files = [];
for (const [i, t] of ts.entries()) {
  await p.evaluate((x) => window.seek(x), t);
  const f = join(tmp, `f${i}.png`);
  await p.screenshot({ path: f }); files.push(f);
}
await browser.close();
if (errors.length) console.error('Errors on the page:\n' + [...new Set(errors)].join('\n'));

const n = files.length, c = Math.min(Number(columns), n), rows = Math.ceil(n / c);
const inputs = files.flatMap((f) => ['-i', f]);
const fillers = Array.from({ length: rows * c - n }, () => ['-f', 'lavfi', '-i', 'color=c=0x0f1115:s=1920x1080:d=1']).flat();
const total = n + fillers.length / 4;
const scales = Array.from({ length: total }, (_, i) => `[${i}]scale=640:360[s${i}]`).join(';');
const rowFilters = Array.from({ length: rows }, (_, r) => { const e = Array.from({ length: c }, (_, k) => `[s${r * c + k}]`).join(''); return c > 1 ? `${e}hstack=inputs=${c}[r${r}]` : `${e}copy[r${r}]`; }).join(';');   // hstack needs >= 2 inputs
const stacked = rows > 1 ? `${Array.from({ length: rows }, (_, r) => `[r${r}]`).join('')}vstack=inputs=${rows}` : '[r0]copy';
const r = spawnSync('ffmpeg', ['-loglevel', 'error', '-y', ...inputs, ...fillers, '-filter_complex', `${scales};${rowFilters};${stacked}`, '-frames:v', '1', resolve(output)], { stdio: 'inherit' });
process.exit(r.status ?? 1);

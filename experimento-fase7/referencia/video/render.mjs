// Renderiza una escena HTML con seek(t) a MP4: Chrome sin interfaz + FFmpeg.
// Uso: node video/render.mjs [escena.html] [salida.mp4] [--fps 30] [--png]
import { chromium } from 'playwright-core';
import { spawn } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const args = process.argv.slice(2);
const flag = (n, def) => { const i = args.indexOf(n); return i >= 0 ? args.splice(i, 2)[1] : def; };
const usaPng = args.includes('--png') && !!args.splice(args.indexOf('--png'), 1);
const fps = Number(flag('--fps', 30));
const [escena = 'video/scene.html', salida = 'out/titulo.mp4'] = args;

mkdirSync(dirname(resolve(salida)), { recursive: true });

const inicio = Date.now();
const browser = await chromium.launch({ executablePath: CHROME, headless: true });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
const errores = [];
page.on('pageerror', (e) => errores.push(e.message));
page.on('console', (m) => m.type() === 'error' && errores.push(m.text()));

await page.goto(pathToFileURL(resolve(escena)).href + '#render');   // '#render' avisa a la escena de que no se anime sola
await page.evaluate(() => document.fonts.ready);

const duracion = await page.evaluate(() => window.DURATION);
const tipoSeek = await page.evaluate(() => typeof window.seek);
if (!(duracion > 0) || tipoSeek !== 'function') {
  throw new Error('La escena debe definir window.DURATION (> 0) y window.seek(t)');
}

const total = Math.round(duracion * fps);
const formato = usaPng ? 'png' : 'jpeg';
const ffmpeg = spawn('ffmpeg', [
  '-y', '-loglevel', 'error',
  '-f', 'image2pipe', '-framerate', String(fps), '-c:v', usaPng ? 'png' : 'mjpeg', '-i', '-',
  '-vf', 'scale=in_range=full:out_range=limited:out_color_matrix=bt709,format=yuv420p',
  '-c:v', 'libx264', '-crf', '18', '-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
  '-movflags', '+faststart',
  resolve(salida),
], { stdio: ['pipe', 'inherit', 'inherit'] });
const ffmpegTermino = new Promise((ok, fallo) => {
  ffmpeg.on('close', (c) => (c === 0 ? ok() : fallo(new Error(`ffmpeg salió con código ${c}`))));
});

for (let i = 0; i < total; i++) {
  await page.evaluate((t) => window.seek(t), i / fps);
  const img = await page.screenshot({ type: formato, ...(usaPng ? {} : { quality: 92 }) });
  if (!ffmpeg.stdin.write(img)) await new Promise((r) => ffmpeg.stdin.once('drain', r));
}
ffmpeg.stdin.end();
await ffmpegTermino;
await browser.close();

if (errores.length) console.error('Errores en la página:\n' + errores.join('\n'));
console.log(`OK ${salida}: ${total} fotogramas, ${duracion} s, ${formato}, ${((Date.now() - inicio) / 1000).toFixed(1)} s de render`);

// Renders an HTML scene with seek(t) to MP4: headless Chrome + FFmpeg.
// Usage: node video/render.mjs [scene.html] [output.mp4] [--fps 30] [--png]
import { chromium } from 'playwright-core';
import { spawn } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const args = process.argv.slice(2);
const flag = (n, def) => { const i = args.indexOf(n); return i >= 0 ? args.splice(i, 2)[1] : def; };
const usePng = args.includes('--png') && !!args.splice(args.indexOf('--png'), 1);
const fps = Number(flag('--fps', 30));
const [scene = 'video/scene.html', output = 'out/title.mp4'] = args;

mkdirSync(dirname(resolve(output)), { recursive: true });

const startedAt = Date.now();
const browser = await chromium.launch({ executablePath: CHROME, headless: true });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
const errors = [];
page.on('pageerror', (e) => errors.push(e.message));
page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));

await page.goto(pathToFileURL(resolve(scene)).href + '#render');   // '#render' tells the scene not to animate by itself
await page.evaluate(() => document.fonts.ready);

const duration = await page.evaluate(() => window.DURATION);
const seekType = await page.evaluate(() => typeof window.seek);
if (!(duration > 0) || seekType !== 'function') {
  throw new Error('The scene must define window.DURATION (> 0) and window.seek(t)');
}

const total = Math.round(duration * fps);
const format = usePng ? 'png' : 'jpeg';
const ffmpeg = spawn('ffmpeg', [
  '-y', '-loglevel', 'error',
  '-f', 'image2pipe', '-framerate', String(fps), '-c:v', usePng ? 'png' : 'mjpeg', '-i', '-',
  '-vf', 'scale=in_range=full:out_range=limited:out_color_matrix=bt709,format=yuv420p',
  '-c:v', 'libx264', '-crf', '18', '-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
  '-movflags', '+faststart',
  resolve(output),
], { stdio: ['pipe', 'inherit', 'inherit'] });
const ffmpegDone = new Promise((ok, fallo) => {
  ffmpeg.on('close', (c) => (c === 0 ? ok() : fallo(new Error(`ffmpeg exited with code ${c}`))));
});

for (let i = 0; i < total; i++) {
  await page.evaluate((t) => window.seek(t), i / fps);
  const img = await page.screenshot({ type: format, ...(usePng ? {} : { quality: 92 }) });
  if (!ffmpeg.stdin.write(img)) await new Promise((r) => ffmpeg.stdin.once('drain', r));
}
ffmpeg.stdin.end();
await ffmpegDone;
await browser.close();

if (errors.length) console.error('Errors on the page:\n' + errors.join('\n'));
console.log(`OK ${output}: ${total} frames, ${duration} s, ${format}, ${((Date.now() - startedAt) / 1000).toFixed(1)} s of rendering`);

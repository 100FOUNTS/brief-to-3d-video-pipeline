import { chromium } from 'playwright-core';
import { execSync, spawn } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = join(__dirname, '..', 'out');
const FRAME_DIR = join(OUT_DIR, 'frames');
mkdirSync(FRAME_DIR, { recursive: true });

const WIDTH = 1920;
const HEIGHT = 1080;
const FPS = 30;
const DURATION = 8; // synced with scene.html
const TOTAL_FRAMES = DURATION * FPS;

const HTML_FILE = join(__dirname, 'scene.html');
const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

console.log(`Rendering ${TOTAL_FRAMES} frames at ${FPS} fps...`);

const browser = await chromium.launch({
  executablePath: CHROME_PATH,
  headless: true,
  args: ['--no-sandbox', '--disable-gpu'],
});

const page = await browser.newPage({ viewport: { width: WIDTH, height: HEIGHT } });

// Suppress console noise from the page
page.on('console', () => {});

for (let i = 0; i < TOTAL_FRAMES; i++) {
  const t = i / FPS;
  await page.goto(`file://${HTML_FILE}`);
  await page.evaluate(async (t) => {
    window.seek(t);
    // Wait for style to apply and layout to settle
    await new Promise(r => setTimeout(r, 50));
  }, t);

  const framePath = join(FRAME_DIR, String(i).padStart(4, '0') + '.jpg');
  const clipPath = await page.screenshot({
    path: framePath,
    type: 'jpeg',
    quality: 95,
  });
  if (i % 60 === 0 || i === TOTAL_FRAMES - 1) {
    console.log(`  Frame ${i}/${TOTAL_FRAMES}  (${t.toFixed(2)}s)`);
  }
}

console.log('All frames captured. Encoding video...');
await browser.close();

// Stitch frames into MP4 with ffmpeg
const ffmpegArgs = [
  '-y',
  '-r', String(FPS),
  '-i', join(FRAME_DIR, '%04d.jpg'),
  '-c:v', 'libx264',
  '-pix_fmt', 'yuv420p',
  '-r', String(FPS),
  join(OUT_DIR, 'titulo.mp4'),
];

execSync(`ffmpeg ${ffmpegArgs.join(' ')}`, { stdio: 'inherit' });

console.log('Done → out/titulo.mp4');

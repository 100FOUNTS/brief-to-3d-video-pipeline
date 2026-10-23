// Verifies the viewer with a real browser: opens the page, moves the slider, clicks parts and takes screenshots.
// Usage: npm run captures   (starts Vite by itself; saves to ../out/viewer/)
import { createServer } from 'vite';
import { chromium } from 'playwright-core';
import { mkdirSync, writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const outDir = resolve(here, '../../out/viewer');
mkdirSync(outDir, { recursive: true });
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const server = await createServer({ root: resolve(here, '..'), server: { port: 5199, strictPort: true }, logLevel: 'error' });
await server.listen();
const url = 'http://localhost:5199/?still=1';

const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ['--use-angle=metal', '--ignore-gpu-blocklist'] });
const report = { checks: [], errors: [] };
const ok = (name, cond, detail = '') => { report.checks.push({ name, ok: !!cond, detail }); console.log(`${cond ? 'OK   ' : 'FAIL '} ${name}${detail ? ' — ' + detail : ''}`); };

try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  page.on('console', (m) => { if (['error', 'warning'].includes(m.type())) report.errors.push(`${m.type()}: ${m.text()}`); });
  page.on('pageerror', (e) => report.errors.push('pageerror: ' + e.message));
  await page.goto(url);
  await page.waitForFunction(() => window.__arco?.ready, null, { timeout: 15000 });

  ok('the default model is the Blender .glb (it did not fall back to the primitives)', (await page.evaluate(() => window.__arco.state().model)) === 'glb');

  const gpu = await page.evaluate(() => {
    const gl = document.createElement('canvas').getContext('webgl2');
    const e = gl?.getExtension('WEBGL_debug_renderer_info');
    return gl ? (e ? gl.getParameter(e.UNMASKED_RENDERER_WEBGL) : 'webgl2') : 'no webgl2';
  });
  ok('WebGL2 available', gpu !== 'no webgl2', gpu);

  // 1) Slider at 0, 0.5 and 1
  for (const [s, name] of [[0, '0'], [0.5, '05'], [1, '1']]) {
    await page.evaluate((v) => window.__arco.setExplosion(v), s);
    await page.waitForTimeout(150);
    await page.screenshot({ path: `${outDir}/explosion-${name}.png` });
  }
  await page.evaluate(() => window.__arco.setExplosion(0));
  // the DOM slider really moves the state (with smooth animation)
  await page.locator('#explosion').fill('1');
  await page.waitForFunction(() => window.__arco.state().explosion > 0.98, null, { timeout: 5000 });
  ok('the DOM slider separates the parts', true);
  await page.locator('#explosion').fill('0');
  await page.waitForFunction(() => window.__arco.state().explosion < 0.02, null, { timeout: 5000 });

  // 2) Real click on the shade, the upper arm and the base (pixel coordinates)
  for (const name of ['shade', 'upper-arm', 'base']) {
    const p = await page.evaluate((n) => window.__arco.pixelOf(n), name);
    await page.mouse.click(p.x, p.y);
    await page.waitForTimeout(100);
    const sel = await page.evaluate(() => window.__arco.state().selected);
    ok(`clicking ${name} selects it`, sel === name, `selected: ${sel}`);
    if (name === 'shade') {
      const title = await page.locator('.info-title').textContent();
      ok('the panel shows the part name', title === 'Shade', title);
      await page.screenshot({ path: `${outDir}/selection-shade.png` });
    }
  }
  // clicking on empty space deselects
  await page.mouse.click(60, 560);
  ok('clicking on empty space deselects', (await page.evaluate(() => window.__arco.state().selected)) === null);

  // 3) Color button
  await page.evaluate(() => window.__arco.select(null));
  await page.locator('#colors button[data-color="Forest green"]').click();
  ok('the button changes the shade color', (await page.evaluate(() => window.__arco.state().color)) === 'Forest green');
  await page.waitForTimeout(100);
  await page.screenshot({ path: `${outDir}/color-green.png` });
  await page.locator('#colors button[data-color="Brass"]').click();

  // 4) A drag to rotate does not count as a click
  const c = await page.evaluate(() => window.__arco.pixelOf('shade'));
  await page.evaluate(() => window.__arco.select(null));
  await page.mouse.move(c.x, c.y); await page.mouse.down(); await page.mouse.move(c.x + 120, c.y + 10, { steps: 6 }); await page.mouse.up();
  ok('dragging to rotate does not select', (await page.evaluate(() => window.__arco.state().selected)) === null);

  // 5) Switching model on the fly: primitives and back to the .glb, keeping the color and clearing the selection
  await page.evaluate(() => { window.__arco.setExplosion(0); window.__arco.setColor('Midnight blue'); window.__arco.select('base'); });
  await page.locator('#models button[data-model="primitives"]').click();
  await page.waitForFunction(() => window.__arco.state().model === 'primitives', null, { timeout: 5000 });
  const state1 = await page.evaluate(() => ({ ...window.__arco.state(), hex: window.__arco.shadeColorHex() }));
  ok('switching to primitives clears the selection', state1.selected === null);
  ok('switching to primitives keeps the chosen color (Midnight blue = #27426b)', state1.color === 'Midnight blue' && state1.hex === '#27426b', state1.hex);
  await page.waitForTimeout(150);
  await page.screenshot({ path: `${outDir}/primitives-explosion-0.png` });
  for (const name of ['shade', 'lower-arm']) {
    const p = await page.evaluate((n) => window.__arco.pixelOf(n), name);
    await page.mouse.click(p.x, p.y); await page.waitForTimeout(80);
    ok(`(primitives) clicking ${name} selects it`, (await page.evaluate(() => window.__arco.state().selected)) === name);
  }
  await page.evaluate(() => window.__arco.setExplosion(1));
  await page.screenshot({ path: `${outDir}/primitives-explosion-1.png` });
  await page.locator('#models button[data-model="glb"]').click();
  await page.waitForFunction(() => window.__arco.state().model === 'glb', null, { timeout: 8000 });
  const state2 = await page.evaluate(() => ({ ...window.__arco.state(), hex: window.__arco.shadeColorHex() }));
  ok('switching back to the .glb keeps the color and the separation', state2.hex === '#27426b' && state2.explosion === 1, `${state2.hex} · explosion ${state2.explosion}`);
  await page.evaluate(() => { window.__arco.setExplosion(0); window.__arco.setColor('Brass'); });

  // 6) Mobile
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(200);
  await page.evaluate(() => window.__arco.setExplosion(0.6));
  await page.screenshot({ path: `${outDir}/mobile.png` });
} finally {
  await browser.close();
  await server.close();
}
report.errors = [...new Set(report.errors)];
ok('no errors or warnings in the console', report.errors.length === 0, report.errors.slice(0, 3).join(' | '));
writeFileSync(`${outDir}/report.json`, JSON.stringify(report, null, 2));
process.exit(report.checks.every((x) => x.ok) ? 0 : 1);

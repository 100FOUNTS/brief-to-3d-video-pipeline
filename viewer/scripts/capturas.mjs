// Verifica el visor con un navegador real: abre la página, mueve el deslizador, hace clic en piezas y saca capturas.
// Uso: npm run capturas   (arranca Vite solo; guarda en ../out/viewer/)
import { createServer } from 'vite';
import { chromium } from 'playwright-core';
import { mkdirSync, writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const aqui = dirname(fileURLToPath(import.meta.url));
const salida = resolve(aqui, '../../out/viewer');
mkdirSync(salida, { recursive: true });
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const servidor = await createServer({ root: resolve(aqui, '..'), server: { port: 5199, strictPort: true }, logLevel: 'error' });
await servidor.listen();
const url = 'http://localhost:5199/?quieto=1';

const navegador = await chromium.launch({ executablePath: CHROME, headless: true, args: ['--use-angle=metal', '--ignore-gpu-blocklist'] });
const informe = { comprobaciones: [], errores: [] };
const ok = (nombre, cond, detalle = '') => { informe.comprobaciones.push({ nombre, ok: !!cond, detalle }); console.log(`${cond ? 'OK   ' : 'FALLA'} ${nombre}${detalle ? ' — ' + detalle : ''}`); };

try {
  const pagina = await navegador.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  pagina.on('console', (m) => { if (['error', 'warning'].includes(m.type())) informe.errores.push(`${m.type()}: ${m.text()}`); });
  pagina.on('pageerror', (e) => informe.errores.push('pageerror: ' + e.message));
  await pagina.goto(url);
  await pagina.waitForFunction(() => window.__arco?.listo, null, { timeout: 15000 });

  const gpu = await pagina.evaluate(() => {
    const gl = document.createElement('canvas').getContext('webgl2');
    const e = gl?.getExtension('WEBGL_debug_renderer_info');
    return gl ? (e ? gl.getParameter(e.UNMASKED_RENDERER_WEBGL) : 'webgl2') : 'sin webgl2';
  });
  ok('WebGL2 disponible', gpu !== 'sin webgl2', gpu);

  // 1) Deslizador real a 0, 0,5 y 1
  for (const [s, nombre] of [[0, '0'], [0.5, '05'], [1, '1']]) {
    await pagina.evaluate((v) => window.__arco.setExplosion(v), s);
    await pagina.waitForTimeout(150);
    await pagina.screenshot({ path: `${salida}/explosion-${nombre}.png` });
  }
  await pagina.evaluate(() => window.__arco.setExplosion(0));
  // el deslizador del DOM mueve de verdad el estado (con animación suave)
  await pagina.locator('#explosion').fill('1');
  await pagina.waitForFunction(() => window.__arco.estado().explosion > 0.98, null, { timeout: 5000 });
  ok('el deslizador del DOM separa las piezas', true);
  await pagina.locator('#explosion').fill('0');
  await pagina.waitForFunction(() => window.__arco.estado().explosion < 0.02, null, { timeout: 5000 });

  // 2) Clic real sobre la pantalla y sobre la bombilla (coordenadas en píxeles)
  for (const nombre of ['pantalla', 'brazo-superior', 'base']) {
    const p = await pagina.evaluate((n) => window.__arco.pixelDe(n), nombre);
    await pagina.mouse.click(p.x, p.y);
    await pagina.waitForTimeout(100);
    const sel = await pagina.evaluate(() => window.__arco.estado().seleccionada);
    ok(`clic en ${nombre} lo selecciona`, sel === nombre, `seleccionada: ${sel}`);
    if (nombre === 'pantalla') {
      const titulo = await pagina.locator('.info-titulo').textContent();
      ok('el panel muestra el nombre de la pieza', titulo === 'Pantalla', titulo);
      await pagina.screenshot({ path: `${salida}/seleccion-pantalla.png` });
    }
  }
  // clic en vacío deselecciona
  await pagina.mouse.click(60, 560);
  ok('clic en vacío deselecciona', (await pagina.evaluate(() => window.__arco.estado().seleccionada)) === null);

  // 3) Botón de color
  await pagina.evaluate(() => window.__arco.seleccionar(null));
  await pagina.locator('#colores button[data-color="Verde bosque"]').click();
  ok('el botón cambia el color de la pantalla', (await pagina.evaluate(() => window.__arco.estado().color)) === 'Verde bosque');
  await pagina.waitForTimeout(100);
  await pagina.screenshot({ path: `${salida}/color-verde.png` });
  await pagina.locator('#colores button[data-color="Latón"]').click();

  // 4) Giro con arrastre no cuenta como clic
  const c = await pagina.evaluate(() => window.__arco.pixelDe('pantalla'));
  await pagina.evaluate(() => window.__arco.seleccionar(null));
  await pagina.mouse.move(c.x, c.y); await pagina.mouse.down(); await pagina.mouse.move(c.x + 120, c.y + 10, { steps: 6 }); await pagina.mouse.up();
  ok('arrastrar para girar no selecciona', (await pagina.evaluate(() => window.__arco.estado().seleccionada)) === null);

  // 5) Móvil
  await pagina.setViewportSize({ width: 390, height: 844 });
  await pagina.waitForTimeout(200);
  await pagina.evaluate(() => window.__arco.setExplosion(0.6));
  await pagina.screenshot({ path: `${salida}/movil.png` });
} finally {
  await navegador.close();
  await servidor.close();
}
informe.errores = [...new Set(informe.errores)];
ok('sin errores ni avisos en la consola', informe.errores.length === 0, informe.errores.slice(0, 3).join(' | '));
writeFileSync(`${salida}/informe.json`, JSON.stringify(informe, null, 2));
process.exit(informe.comprobaciones.every((x) => x.ok) ? 0 : 1);

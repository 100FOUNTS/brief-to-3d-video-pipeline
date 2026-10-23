import { chromium } from "playwright-core";
import { spawn } from "node:child_process";
import { mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const FPS = 30;
const WIDTH = 1920;
const HEIGHT = 1080;

const aquí = dirname(fileURLToPath(import.meta.url));
const escena = pathToFileURL(resolve(aquí, "scene.html")).href;
const salida = resolve(aquí, "..", "out", "titulo.mp4");
mkdirSync(dirname(salida), { recursive: true });

const browser = await chromium.launch({ executablePath: CHROME, headless: true });
const page = await browser.newPage({
  viewport: { width: WIDTH, height: HEIGHT },
  deviceScaleFactor: 1,
});
await page.goto(escena);
await page.evaluate(() => document.fonts.ready);

const duracion = await page.evaluate(() => window.DURATION);
const total = Math.round(duracion * FPS);

const ffmpeg = spawn(
  "ffmpeg",
  [
    "-y",
    "-loglevel", "error",
    "-f", "image2pipe",
    "-framerate", String(FPS),
    "-c:v", "mjpeg",
    "-i", "-",
    "-vf", "scale=in_range=pc:out_range=tv,format=yuv420p",
    "-c:v", "libx264",
    "-profile:v", "high",
    "-pix_fmt", "yuv420p",
    "-r", String(FPS),
    "-s", `${WIDTH}x${HEIGHT}`,
    "-movflags", "+faststart",
    salida,
  ],
  { stdio: ["pipe", "inherit", "inherit"] },
);

const terminado = new Promise((ok, fallo) => {
  ffmpeg.on("error", fallo);
  ffmpeg.on("close", (code) =>
    code === 0 ? ok() : fallo(new Error(`ffmpeg terminó con código ${code}`)),
  );
});
// Evita que un EPIPE (ffmpeg caído) tumbe el proceso antes de informar del código.
ffmpeg.stdin.on("error", () => {});

try {
  for (let i = 0; i < total; i++) {
    const t = i / FPS;
    await page.evaluate((s) => window.seek(s), t);
    const jpeg = await page.screenshot({ type: "jpeg", quality: 95 });
    if (!ffmpeg.stdin.write(jpeg)) {
      await new Promise((r) => ffmpeg.stdin.once("drain", r));
    }
  }
} finally {
  ffmpeg.stdin.end();
  await browser.close();
}

await terminado;
console.log(`Listo: ${salida} (${total} fotogramas, ${duracion} s)`);

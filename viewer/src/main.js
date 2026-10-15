import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { BRIEF } from './brief.generated.js';
import { crearMateriales, crearLampara, lamparaDesdeGLTF, aplicarExplosion, suavizar, piezas, limites, INFO, NOMBRES, COLORES_PANTALLA } from './lampara.js';

// El producto y su paleta salen de brief.json (vía brief.generated.js).
document.title = `${BRIEF.nombre} · visor 3D`;
document.querySelector('.cabecera h1').textContent = BRIEF.nombre;
document.querySelector('.cabecera p').textContent = BRIEF.descripcion;
document.getElementById('escena').setAttribute('aria-label', `${BRIEF.descripcion} ${BRIEF.nombre} en 3D. Arrastra para girar, rueda para acercar.`);
for (const [variable, clave] of [['--fondo', 'fondo'], ['--superficie', 'fondo2'], ['--texto', 'texto'], ['--acento', 'acento']]) {
  document.documentElement.style.setProperty(variable, BRIEF.paleta[clave]);
}

const params = new URLSearchParams(location.search);
const quieto = params.has('quieto'); // sin giro automático ni animación: para capturas reproducibles

const canvas = document.getElementById('escena');
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: quieto });
} catch (e) {
  document.querySelector('.info-detalle').textContent = 'Tu navegador no pudo iniciar WebGL, así que no se puede mostrar la lámpara.';
  throw e;
}
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;      // en Three.js 186 PCFSoftShadowMap ya no existe
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;

// ---------- escena ----------
const escena = new THREE.Scene();
escena.background = new THREE.Color(BRIEF.paleta.fondo);
escena.fog = new THREE.Fog(BRIEF.paleta.fondo, 10, 30); // el borde del suelo se difumina en el fondo (se ajusta en encuadrar)
const pmrem = new THREE.PMREMGenerator(renderer);
escena.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture; // reflejos suaves en el metal
escena.environmentIntensity = 0.42;

const luzPrincipal = new THREE.DirectionalLight('#fff3df', 0.9);
luzPrincipal.position.set(-5, 9, 6);
luzPrincipal.castShadow = true;
luzPrincipal.shadow.mapSize.set(2048, 2048);
Object.assign(luzPrincipal.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7, near: 1, far: 30 });
luzPrincipal.shadow.radius = 4;
luzPrincipal.shadow.bias = -0.0004;
escena.add(luzPrincipal);

const suelo = new THREE.Mesh(
  new THREE.CircleGeometry(18, 96),
  new THREE.MeshStandardMaterial({ color: BRIEF.paleta.suelo, roughness: 0.92, metalness: 0 }),
);
suelo.rotation.x = -Math.PI / 2;
suelo.receiveShadow = true;
escena.add(suelo);

// Se arranca con las primitivas (síncrono) para que todo lo demás se inicialice; después se carga el .glb de Blender y se sustituye.
let lampara = crearLampara(crearMateriales());
let modeloActual = 'primitivas';
escena.add(lampara);
const porNombre = (n) => lampara.getObjectByName(n);

// ---------- cámara ----------
const camara = new THREE.PerspectiveCamera(35, 1, 0.1, 100);
const controles = new OrbitControls(camara, canvas);
controles.enableDamping = true;
controles.dampingFactor = 0.08;
controles.minPolarAngle = 0.15;
controles.maxPolarAngle = Math.PI / 2 - 0.02;   // no baja del suelo
controles.autoRotate = !quieto;
controles.autoRotateSpeed = 0.7;

// La cámara se ajusta a la lámpara armada y, al separar las piezas, se aleja y se recentra sola.
const encuadre = { c0: new THREE.Vector3(), c1: new THREE.Vector3(), factor: 1, k: 1, centroAplicado: new THREE.Vector3() };

function distanciaPara(esfera) {
  const fovV = THREE.MathUtils.degToRad(camara.fov);
  const fovH = 2 * Math.atan(Math.tan(fovV / 2) * camara.aspect);
  return (esfera.radius / Math.sin(Math.min(fovV, fovH) / 2)) * 1.12;
}

function encuadrar(conservarDireccion = false) {
  aplicarExplosion(lampara, 0);
  const cajaArmada = limites(lampara);
  aplicarExplosion(lampara, 1);
  const cajaTotal = limites(lampara).union(cajaArmada);
  aplicarExplosion(lampara, explosionActual);
  const eA = cajaArmada.getBoundingSphere(new THREE.Sphere());
  const eT = cajaTotal.getBoundingSphere(new THREE.Sphere());
  const dA = distanciaPara(eA), dT = distanciaPara(eT);
  encuadre.c0.copy(eA.center); encuadre.c1.copy(eT.center);
  encuadre.k = dT / dA; encuadre.factor = 1; encuadre.centroAplicado.copy(eA.center);
  const direccion = conservarDireccion
    ? camara.position.clone().sub(controles.target).normalize()
    : new THREE.Vector3(0.55, 0.26, 1).normalize();
  controles.target.copy(eA.center);
  camara.position.copy(eA.center).addScaledVector(direccion, dA);
  controles.minDistance = dA * 0.3;
  controles.maxDistance = dA * 2.6;
  escena.fog.near = dA * 1.0;
  escena.fog.far = dA * 2.7;
  controles.update();
}

// Cada fotograma: mueve el objetivo y la distancia según cuánto está separada la lámpara (conserva el zoom que haya hecho la persona).
function seguirExplosion() {
  const e = suavizar(explosionActual);
  const centro = encuadre.c0.clone().lerp(encuadre.c1, e);
  const delta = centro.clone().sub(encuadre.centroAplicado);
  camara.position.add(delta);
  controles.target.add(delta);
  encuadre.centroAplicado.copy(centro);
  const factor = THREE.MathUtils.lerp(1, encuadre.k, e);
  const desplazamiento = camara.position.clone().sub(controles.target).multiplyScalar(factor / encuadre.factor);
  camara.position.copy(controles.target).add(desplazamiento);
  encuadre.factor = factor;
}

let interactuado = false;
let explosionActual = 0, explosionObjetivo = 0;
function ajustarTamano() {
  const w = window.innerWidth, h = window.innerHeight;
  renderer.setSize(w, h, false);
  camara.aspect = w / h;
  // pantallas anchas: la lámpara se desplaza a la izquierda (panel a la derecha); móviles: hacia arriba (controles abajo)
  if (w > 760) camara.setViewOffset(w, h, 150, 0, w, h); else camara.setViewOffset(w, h, 0, 150, w, h);
  camara.updateProjectionMatrix();
  encuadrar(interactuado);
}
window.addEventListener('resize', ajustarTamano);
ajustarTamano();

// ---------- estado e interfaz ----------
let seleccionada = null;
let colorActual = 'Latón';

const slider = document.getElementById('explosion');
const panelInfo = document.getElementById('info');
const lista = document.getElementById('lista-piezas');
const contenedorColores = document.getElementById('colores');

slider.addEventListener('input', () => { explosionObjetivo = Number(slider.value); });

NOMBRES.forEach((nombre, i) => {
  const li = document.createElement('li');
  const b = document.createElement('button');
  b.type = 'button';
  b.dataset.pieza = nombre;
  b.setAttribute('aria-pressed', 'false');
  b.innerHTML = `<span class="num">${String(i + 1).padStart(2, '0')}</span><span>${INFO[nombre].titulo}</span>`;
  b.addEventListener('click', () => seleccionar(seleccionada === nombre ? null : nombre));
  li.appendChild(b);
  lista.appendChild(li);
});

Object.entries(COLORES_PANTALLA).forEach(([nombre, hex]) => {
  const b = document.createElement('button');
  b.type = 'button';
  b.title = nombre;
  b.dataset.color = nombre;
  b.setAttribute('role', 'radio');
  b.setAttribute('aria-label', nombre);
  b.setAttribute('aria-checked', String(nombre === colorActual));
  b.style.background = hex;
  b.addEventListener('click', () => colorear(nombre));
  contenedorColores.appendChild(b);
});

function colorear(nombre) {
  if (!COLORES_PANTALLA[nombre]) return;
  colorActual = nombre;
  const hex = COLORES_PANTALLA[nombre];
  const pantalla = porNombre('pantalla');
  const material = pantalla.userData.materialColor;      // material propio de la pantalla (en las primitivas y en el .glb)
  material.color.set(hex);
  // si la pantalla está resaltada, su material es una copia: se actualiza también
  pantalla.traverse((o) => { if (o.isMesh && o.userData.matOriginal === material) o.material.color.set(hex); });
  contenedorColores.querySelectorAll('button').forEach((b) => b.setAttribute('aria-checked', String(b.dataset.color === nombre)));
}

function resaltar(nombre, activo) {
  const grupo = porNombre(nombre);
  grupo.traverse((o) => {
    if (!o.isMesh) return;
    if (activo) {
      if (!o.userData.matOriginal) { o.userData.matOriginal = o.material; o.material = o.material.clone(); }
      if (nombre === 'bombilla') { o.material.emissiveIntensity = 4; }
      else { o.material.emissive.set(BRIEF.paleta.acento); o.material.emissiveIntensity = 0.3; }
    } else if (o.userData.matOriginal) {
      o.material.dispose();
      o.material = o.userData.matOriginal;
      delete o.userData.matOriginal;
    }
  });
}

function seleccionar(nombre) {
  if (seleccionada) resaltar(seleccionada, false);
  seleccionada = nombre && INFO[nombre] ? nombre : null;
  if (seleccionada) resaltar(seleccionada, true);
  lista.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.pieza === seleccionada)));
  if (!seleccionada) {
    panelInfo.innerHTML = '<p class="etiqueta">Selecciona una pieza</p><p class="info-detalle">Pulsa sobre la lámpara o elige una de la lista.</p>';
    return;
  }
  const i = INFO[seleccionada];
  panelInfo.innerHTML = '';
  const partes = [['p', 'etiqueta', `Pieza ${String(NOMBRES.indexOf(seleccionada) + 1).padStart(2, '0')} de 07`], ['h2', 'info-titulo', i.titulo], ['p', 'info-material', i.material], ['p', 'info-detalle', i.detalle]];
  for (const [tag, clase, texto] of partes) { const el = document.createElement(tag); el.className = clase; el.textContent = texto; panelInfo.appendChild(el); }
}

// ---------- clic y hover sobre piezas ----------
const rayo = new THREE.Raycaster();
const puntero = new THREE.Vector2();
function piezaBajo(evento) {
  const r = canvas.getBoundingClientRect();
  puntero.set(((evento.clientX - r.left) / r.width) * 2 - 1, -((evento.clientY - r.top) / r.height) * 2 + 1);
  rayo.setFromCamera(puntero, camara);
  const mallas = [];
  for (const p of piezas(lampara)) p.traverse((o) => { if (o.isMesh) mallas.push(o); });
  const golpe = rayo.intersectObjects(mallas, false)[0];
  if (!golpe) return null;
  let o = golpe.object;
  while (o && !o.userData.esPieza) o = o.parent;
  return o ? o.name : null;
}

let inicioPuntero = null;
canvas.addEventListener('pointerdown', (e) => { inicioPuntero = { x: e.clientX, y: e.clientY }; interactuado = true; controles.autoRotate = false; });
canvas.addEventListener('pointerup', (e) => {
  if (!inicioPuntero) return;
  const movimiento = Math.hypot(e.clientX - inicioPuntero.x, e.clientY - inicioPuntero.y);
  inicioPuntero = null;
  if (movimiento > 5) return;                       // fue un arrastre para girar, no un clic
  const nombre = piezaBajo(e);
  seleccionar(nombre === seleccionada ? null : nombre);
});
canvas.addEventListener('pointermove', (e) => { if (!inicioPuntero) canvas.style.cursor = piezaBajo(e) ? 'pointer' : 'grab'; });
canvas.addEventListener('wheel', () => { interactuado = true; controles.autoRotate = false; }, { passive: true });

// ---------- bucle ----------
let ultimo = performance.now();
function dibujar() {
  seguirExplosion();
  const base = porNombre('base');
  suelo.position.y = base.position.y - base.userData.reposo.y; // el suelo acompaña a la base cuando se separa (0 en reposo, sea cual sea el origen de la pieza)
  controles.update();
  renderer.render(escena, camara);
}
function bucle(ahora) {
  const dt = Math.min(0.05, (ahora - ultimo) / 1000);
  ultimo = ahora;
  explosionActual += (explosionObjetivo - explosionActual) * (1 - Math.exp(-dt * 9));
  if (Math.abs(explosionObjetivo - explosionActual) < 0.0005) explosionActual = explosionObjetivo;
  aplicarExplosion(lampara, explosionActual);
  dibujar();
  requestAnimationFrame(bucle);
}
requestAnimationFrame(bucle);

// ---------- modelo: .glb de Blender o primitivas ----------
const botonesModelo = document.querySelectorAll('#modelos button');
function liberar(grupo) {
  grupo.traverse((o) => { if (o.isMesh) { o.geometry?.dispose(); (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) => m.dispose()); } });
}
async function cambiarModelo(tipo) {
  let nueva;
  if (tipo === 'glb') {
    const gltf = await new GLTFLoader().loadAsync(`${import.meta.env.BASE_URL}lampara.glb`);
    nueva = lamparaDesdeGLTF(gltf.scene);
  } else {
    nueva = crearLampara(crearMateriales());
  }
  if (seleccionada) seleccionar(null);               // quita el resaltado del modelo viejo antes de retirarlo
  escena.remove(lampara);
  liberar(lampara);
  lampara = nueva;
  escena.add(lampara);
  modeloActual = tipo;
  colorear(colorActual);                             // conserva el color elegido para la pantalla
  aplicarExplosion(lampara, explosionActual);
  encuadrar(interactuado);
  botonesModelo.forEach((b) => b.setAttribute('aria-checked', String(b.dataset.modelo === tipo)));
  dibujar();
}
botonesModelo.forEach((b) => b.setAttribute('aria-checked', String(b.dataset.modelo === modeloActual)));
botonesModelo.forEach((b) => b.addEventListener('click', () => { cambiarModelo(b.dataset.modelo).catch(avisoCarga); }));
function avisoCarga(e) {
  console.warn('No se pudo cargar el modelo .glb; se queda el de primitivas:', e?.message || e);
  panelInfo.innerHTML = '<p class="etiqueta">Modelo</p><p class="info-detalle">No se pudo cargar el modelo de Blender (lampara.glb). Se muestra el modelo hecho con primitivas.</p>';
}

// ---------- API para pruebas y capturas ----------
window.__arco = {
  listo: false,                                      // pasa a true cuando ya se decidió qué modelo se muestra
  setModelo: (tipo) => cambiarModelo(tipo),
  setExplosion(s) {                                  // salta directamente a s, sin animación
    explosionObjetivo = explosionActual = Math.min(1, Math.max(0, s));
    slider.value = String(explosionObjetivo);
    aplicarExplosion(lampara, explosionActual);
    dibujar();
  },
  seleccionar,
  colorear,
  colorPantallaHex: () => '#' + porNombre('pantalla').userData.materialColor.color.getHexString(),
  estado: () => ({ explosion: explosionActual, seleccionada, color: colorActual, modelo: modeloActual }),
  pixelDe(nombre) {                                  // centro de una pieza en píxeles de la ventana
    const v = new THREE.Box3().setFromObject(porNombre(nombre)).getCenter(new THREE.Vector3()).project(camara);
    const r = canvas.getBoundingClientRect();
    return { x: r.left + ((v.x + 1) / 2) * r.width, y: r.top + ((1 - v.y) / 2) * r.height };
  },
};

// Modelo por defecto: el .glb de Blender (con ?modelo=primitivas se fuerza el de código). Si no carga, se queda el de primitivas.
(params.get('modelo') === 'primitivas' ? Promise.resolve() : cambiarModelo('glb')).catch(avisoCarga).finally(() => { window.__arco.listo = true; });

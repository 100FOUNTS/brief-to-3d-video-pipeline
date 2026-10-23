import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { BRIEF } from './brief.generated.js';
import { createMaterials, createLamp, lampFromGLTF, applyExplosion, ease, parts, bounds, INFO, PART_NAMES, SHADE_COLORS } from './lamp.js';

// The product and its palette come from brief.json (via brief.generated.js).
document.title = `${BRIEF.name} · 3D viewer`;
document.querySelector('.header h1').textContent = BRIEF.name;
document.querySelector('.header p').textContent = BRIEF.description;
document.getElementById('scene').setAttribute('aria-label', `${BRIEF.description} ${BRIEF.name} in 3D. Drag to rotate, scroll to zoom.`);
for (const [variable, key] of [['--bg', 'background'], ['--surface', 'background2'], ['--text', 'text'], ['--accent', 'accent']]) {
  document.documentElement.style.setProperty(variable, BRIEF.palette[key]);
}

const params = new URLSearchParams(location.search);
const still = params.has('still'); // no auto-rotation or animation: for reproducible screenshots

const canvas = document.getElementById('scene');
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: still });
} catch (e) {
  document.querySelector('.info-detail').textContent = 'Your browser could not start WebGL, so the lamp cannot be shown.';
  throw e;
}
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;      // in Three.js 186 PCFSoftShadowMap no longer exists
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;

// ---------- scene ----------
const scene = new THREE.Scene();
scene.background = new THREE.Color(BRIEF.palette.background);
scene.fog = new THREE.Fog(BRIEF.palette.background, 10, 30); // the floor edge fades into the background (adjusted in frameCamera)
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture; // soft reflections on the metal
scene.environmentIntensity = 0.42;

const keyLight = new THREE.DirectionalLight('#fff3df', 0.9);
keyLight.position.set(-5, 9, 6);
keyLight.castShadow = true;
keyLight.shadow.mapSize.set(2048, 2048);
Object.assign(keyLight.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7, near: 1, far: 30 });
keyLight.shadow.radius = 4;
keyLight.shadow.bias = -0.0004;
scene.add(keyLight);

const floor = new THREE.Mesh(
  new THREE.CircleGeometry(18, 96),
  new THREE.MeshStandardMaterial({ color: BRIEF.palette.floor, roughness: 0.92, metalness: 0 }),
);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

// It starts with the primitives (synchronous) so everything else initializes; then the Blender .glb is loaded and swapped in.
let lamp = createLamp(createMaterials());
let currentModel = 'primitives';
scene.add(lamp);
const byName = (n) => lamp.getObjectByName(n);

// ---------- camera ----------
const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 100);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minPolarAngle = 0.15;
controls.maxPolarAngle = Math.PI / 2 - 0.02;   // does not go below the floor
controls.autoRotate = !still;
controls.autoRotateSpeed = 0.7;

// The camera fits the assembled lamp and, when the parts separate, it moves back and re-centers by itself.
const framing = { c0: new THREE.Vector3(), c1: new THREE.Vector3(), factor: 1, k: 1, appliedCenter: new THREE.Vector3() };

function distanceFor(sphere) {
  const fovV = THREE.MathUtils.degToRad(camera.fov);
  const fovH = 2 * Math.atan(Math.tan(fovV / 2) * camera.aspect);
  return (sphere.radius / Math.sin(Math.min(fovV, fovH) / 2)) * 1.12;
}

function frameCamera(keepDirection = false) {
  applyExplosion(lamp, 0);
  const assembledBox = bounds(lamp);
  applyExplosion(lamp, 1);
  const totalBox = bounds(lamp).union(assembledBox);
  applyExplosion(lamp, currentExplosion);
  const sA = assembledBox.getBoundingSphere(new THREE.Sphere());
  const sT = totalBox.getBoundingSphere(new THREE.Sphere());
  const dA = distanceFor(sA), dT = distanceFor(sT);
  framing.c0.copy(sA.center); framing.c1.copy(sT.center);
  framing.k = dT / dA; framing.factor = 1; framing.appliedCenter.copy(sA.center);
  const direction = keepDirection
    ? camera.position.clone().sub(controls.target).normalize()
    : new THREE.Vector3(0.55, 0.26, 1).normalize();
  controls.target.copy(sA.center);
  camera.position.copy(sA.center).addScaledVector(direction, dA);
  controls.minDistance = dA * 0.3;
  controls.maxDistance = dA * 2.6;
  scene.fog.near = dA * 1.0;
  scene.fog.far = dA * 2.7;
  controls.update();
}

// Every frame: moves the target and the distance according to how separated the lamp is (keeps whatever zoom the person applied).
function followExplosion() {
  const e = ease(currentExplosion);
  const center = framing.c0.clone().lerp(framing.c1, e);
  const delta = center.clone().sub(framing.appliedCenter);
  camera.position.add(delta);
  controls.target.add(delta);
  framing.appliedCenter.copy(center);
  const factor = THREE.MathUtils.lerp(1, framing.k, e);
  const offset = camera.position.clone().sub(controls.target).multiplyScalar(factor / framing.factor);
  camera.position.copy(controls.target).add(offset);
  framing.factor = factor;
}

let interacted = false;
let currentExplosion = 0, targetExplosion = 0;
function resize() {
  const w = window.innerWidth, h = window.innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  // wide screens: the lamp shifts to the left (panel on the right); phones: upwards (controls at the bottom)
  if (w > 760) camera.setViewOffset(w, h, 150, 0, w, h); else camera.setViewOffset(w, h, 0, 150, w, h);
  camera.updateProjectionMatrix();
  frameCamera(interacted);
}
window.addEventListener('resize', resize);
resize();

// ---------- state and interface ----------
let selected = null;
let currentColor = 'Brass';

const slider = document.getElementById('explosion');
const infoPanel = document.getElementById('info');
const list = document.getElementById('part-list');
const colorContainer = document.getElementById('colors');

slider.addEventListener('input', () => { targetExplosion = Number(slider.value); });

PART_NAMES.forEach((name, i) => {
  const li = document.createElement('li');
  const b = document.createElement('button');
  b.type = 'button';
  b.dataset.part = name;
  b.setAttribute('aria-pressed', 'false');
  b.innerHTML = `<span class="num">${String(i + 1).padStart(2, '0')}</span><span>${INFO[name].title}</span>`;
  b.addEventListener('click', () => select(selected === name ? null : name));
  li.appendChild(b);
  list.appendChild(li);
});

Object.entries(SHADE_COLORS).forEach(([name, hex]) => {
  const b = document.createElement('button');
  b.type = 'button';
  b.title = name;
  b.dataset.color = name;
  b.setAttribute('role', 'radio');
  b.setAttribute('aria-label', name);
  b.setAttribute('aria-checked', String(name === currentColor));
  b.style.background = hex;
  b.addEventListener('click', () => setColor(name));
  colorContainer.appendChild(b);
});

function setColor(name) {
  if (!SHADE_COLORS[name]) return;
  currentColor = name;
  const hex = SHADE_COLORS[name];
  const shade = byName('shade');
  const material = shade.userData.colorMaterial;      // the shade's own material (in the primitives and in the .glb)
  material.color.set(hex);
  // if the shade is highlighted, its material is a copy: update it too
  shade.traverse((o) => { if (o.isMesh && o.userData.originalMaterial === material) o.material.color.set(hex); });
  colorContainer.querySelectorAll('button').forEach((b) => b.setAttribute('aria-checked', String(b.dataset.color === name)));
}

function highlight(name, active) {
  const group = byName(name);
  group.traverse((o) => {
    if (!o.isMesh) return;
    if (active) {
      if (!o.userData.originalMaterial) { o.userData.originalMaterial = o.material; o.material = o.material.clone(); }
      if (name === 'bulb') { o.material.emissiveIntensity = 4; }
      else { o.material.emissive.set(BRIEF.palette.accent); o.material.emissiveIntensity = 0.3; }
    } else if (o.userData.originalMaterial) {
      o.material.dispose();
      o.material = o.userData.originalMaterial;
      delete o.userData.originalMaterial;
    }
  });
}

function select(name) {
  if (selected) highlight(selected, false);
  selected = name && INFO[name] ? name : null;
  if (selected) highlight(selected, true);
  list.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.part === selected)));
  if (!selected) {
    infoPanel.innerHTML = '<p class="label">Select a part</p><p class="info-detail">Click on the lamp or pick one from the list.</p>';
    return;
  }
  const i = INFO[selected];
  infoPanel.innerHTML = '';
  const fields = [['p', 'label', `Part ${String(PART_NAMES.indexOf(selected) + 1).padStart(2, '0')} of 07`], ['h2', 'info-title', i.title], ['p', 'info-material', i.material], ['p', 'info-detail', i.detail]];
  for (const [tag, cls, text] of fields) { const el = document.createElement(tag); el.className = cls; el.textContent = text; infoPanel.appendChild(el); }
}

// ---------- click and hover on parts ----------
const ray = new THREE.Raycaster();
const pointer = new THREE.Vector2();
function partUnder(event) {
  const r = canvas.getBoundingClientRect();
  pointer.set(((event.clientX - r.left) / r.width) * 2 - 1, -((event.clientY - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(pointer, camera);
  const meshes = [];
  for (const p of parts(lamp)) p.traverse((o) => { if (o.isMesh) meshes.push(o); });
  const hit = ray.intersectObjects(meshes, false)[0];
  if (!hit) return null;
  let o = hit.object;
  while (o && !o.userData.isPart) o = o.parent;
  return o ? o.name : null;
}

let pointerStart = null;
canvas.addEventListener('pointerdown', (e) => { pointerStart = { x: e.clientX, y: e.clientY }; interacted = true; controls.autoRotate = false; });
canvas.addEventListener('pointerup', (e) => {
  if (!pointerStart) return;
  const movement = Math.hypot(e.clientX - pointerStart.x, e.clientY - pointerStart.y);
  pointerStart = null;
  if (movement > 5) return;                       // it was a drag to rotate, not a click
  const name = partUnder(e);
  select(name === selected ? null : name);
});
canvas.addEventListener('pointermove', (e) => { if (!pointerStart) canvas.style.cursor = partUnder(e) ? 'pointer' : 'grab'; });
canvas.addEventListener('wheel', () => { interacted = true; controls.autoRotate = false; }, { passive: true });

// ---------- loop ----------
let last = performance.now();
function draw() {
  followExplosion();
  const base = byName('base');
  floor.position.y = base.position.y - base.userData.rest.y; // the floor follows the base when it separates (0 at rest, whatever the part's origin is)
  controls.update();
  renderer.render(scene, camera);
}
function loop(now) {
  const dt = Math.min(0.05, (now - last) / 1000);
  last = now;
  currentExplosion += (targetExplosion - currentExplosion) * (1 - Math.exp(-dt * 9));
  if (Math.abs(targetExplosion - currentExplosion) < 0.0005) currentExplosion = targetExplosion;
  applyExplosion(lamp, currentExplosion);
  draw();
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

// ---------- model: Blender .glb or primitives ----------
const modelButtons = document.querySelectorAll('#models button');
function release(group) {
  group.traverse((o) => { if (o.isMesh) { o.geometry?.dispose(); (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) => m.dispose()); } });
}
async function switchModel(type) {
  let next;
  if (type === 'glb') {
    const gltf = await new GLTFLoader().loadAsync(`${import.meta.env.BASE_URL}lamp.glb`);
    next = lampFromGLTF(gltf.scene);
  } else {
    next = createLamp(createMaterials());
  }
  if (selected) select(null);               // removes the highlight from the old model before discarding it
  scene.remove(lamp);
  release(lamp);
  lamp = next;
  scene.add(lamp);
  currentModel = type;
  setColor(currentColor);                   // keeps the shade color the person chose
  applyExplosion(lamp, currentExplosion);
  frameCamera(interacted);
  modelButtons.forEach((b) => b.setAttribute('aria-checked', String(b.dataset.model === type)));
  draw();
}
modelButtons.forEach((b) => b.setAttribute('aria-checked', String(b.dataset.model === currentModel)));
modelButtons.forEach((b) => b.addEventListener('click', () => { switchModel(b.dataset.model).catch(loadWarning); }));
function loadWarning(e) {
  console.warn('Could not load the .glb model; keeping the primitives one:', e?.message || e);
  infoPanel.innerHTML = '<p class="label">Model</p><p class="info-detail">Could not load the Blender model (lamp.glb). The model built with primitives is shown.</p>';
}

// ---------- API for tests and screenshots ----------
window.__arco = {
  ready: false,                                      // becomes true once it is decided which model is shown
  setModel: (type) => switchModel(type),
  setExplosion(s) {                                  // jumps straight to s, with no animation
    targetExplosion = currentExplosion = Math.min(1, Math.max(0, s));
    slider.value = String(targetExplosion);
    applyExplosion(lamp, currentExplosion);
    draw();
  },
  select,
  setColor,
  shadeColorHex: () => '#' + byName('shade').userData.colorMaterial.color.getHexString(),
  state: () => ({ explosion: currentExplosion, selected, color: currentColor, model: currentModel }),
  pixelOf(name) {                                    // center of a part in window pixels
    const v = new THREE.Box3().setFromObject(byName(name)).getCenter(new THREE.Vector3()).project(camera);
    const r = canvas.getBoundingClientRect();
    return { x: r.left + ((v.x + 1) / 2) * r.width, y: r.top + ((1 - v.y) / 2) * r.height };
  },
};

// Default model: the Blender .glb (?model=primitives forces the code one). If it does not load, the primitives one stays.
(params.get('model') === 'primitives' ? Promise.resolve() : switchModel('glb')).catch(loadWarning).finally(() => { window.__arco.ready = true; });

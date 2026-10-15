// Lámpara "Arco" construida con primitivas de Three.js. Sin modelos externos.
// Convención: ejes de Three.js, Y hacia arriba. 1 unidad ≈ 10 cm.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

export const NOMBRES = [
  'base',
  'brazo-inferior',
  'articulacion-inferior',
  'brazo-superior',
  'articulacion-superior',
  'pantalla',
  'bombilla',
];

export const INFO = {
  'base': { titulo: 'Base', material: 'Acero negro mate', detalle: 'Cilindro achatado: da peso y estabilidad.' },
  'brazo-inferior': { titulo: 'Brazo inferior', material: 'Aluminio anodizado negro', detalle: 'Primer tramo del brazo. Ligero y rígido.' },
  'articulacion-inferior': { titulo: 'Articulación inferior', material: 'Acero negro con anillo de latón', detalle: 'Gira para cambiar la altura de la lámpara.' },
  'brazo-superior': { titulo: 'Brazo superior', material: 'Aluminio anodizado negro', detalle: 'Segundo tramo. Lleva la luz sobre el escritorio.' },
  'articulacion-superior': { titulo: 'Articulación superior', material: 'Acero negro con anillo de latón', detalle: 'Gira para dirigir la luz donde la necesitas.' },
  'pantalla': { titulo: 'Pantalla', material: 'Latón cepillado', detalle: 'Cono abierto que concentra la luz hacia abajo.' },
  'bombilla': { titulo: 'Bombilla', material: 'LED de luz cálida (2700 K)', detalle: 'Luz cálida para trabajar sin cansar los ojos.' },
};

export const COLORES_PANTALLA = {
  'Latón': '#b8893a',
  'Cobre': '#a8532f',
  'Verde bosque': '#2f5d4a',
  'Azul noche': '#27426b',
  'Negro mate': '#1d2027',
};

// Postura de la lámpara (grados desde la vertical; positivo = hacia la derecha). Misma que la POSE_A del vídeo.
export const POSE = { a1: -30, a2: 58, a3: 162, largo1: 2.4, largo2: 2.3, largoPantalla: 1.1 };

// Desplazamiento (en unidades) de cada pieza cuando la vista explosionada vale 1.
export const EXPLOSION = {
  'base': new THREE.Vector3(0, -1.0, 0.0),
  'brazo-inferior': new THREE.Vector3(-1.6, 0.0, 1.0),
  'articulacion-inferior': new THREE.Vector3(-1.0, 1.2, -1.0),
  'brazo-superior': new THREE.Vector3(0.2, 1.6, 1.0),
  'articulacion-superior': new THREE.Vector3(1.2, 1.4, -1.0),
  'pantalla': new THREE.Vector3(2.0, 0.4, 1.0),
  'bombilla': new THREE.Vector3(2.4, -0.8, -0.6),
};

const dir = (grados) => new THREE.Vector3(Math.sin(THREE.MathUtils.degToRad(grados)), Math.cos(THREE.MathUtils.degToRad(grados)), 0);
const EJE_Y = new THREE.Vector3(0, 1, 0);
const alinear = (objeto, direccion) => objeto.quaternion.setFromUnitVectors(EJE_Y, direccion.clone().normalize());

export function crearMateriales() {
  return {
    negro: new THREE.MeshStandardMaterial({ color: '#242933', metalness: 0.85, roughness: 0.42 }),
    laton: new THREE.MeshStandardMaterial({ color: COLORES_PANTALLA['Latón'], metalness: 1, roughness: 0.3, side: THREE.DoubleSide }),
    // Material propio de la pantalla: así el botón de color no cambia también los anillos de latón de las articulaciones
    pantalla: new THREE.MeshStandardMaterial({ color: COLORES_PANTALLA['Latón'], metalness: 1, roughness: 0.3, side: THREE.DoubleSide }),
    bombilla: new THREE.MeshStandardMaterial({ color: '#fff3d6', emissive: '#ffb703', emissiveIntensity: 2.2, roughness: 0.4 }),
    interior: new THREE.MeshStandardMaterial({ color: '#f4e3b8', emissive: '#ffb703', emissiveIntensity: 0.45, roughness: 0.8, side: THREE.BackSide }),
  };
}

function pieza(nombre, posicion, meshes) {
  const g = new THREE.Group();
  g.name = nombre;
  g.position.copy(posicion);
  g.userData = { esPieza: true, nombre, reposo: posicion.clone(), explosion: EXPLOSION[nombre].clone(), info: INFO[nombre] };
  for (const m of meshes) {
    m.castShadow = true;
    m.receiveShadow = true;
    g.add(m);
  }
  return g;
}

function anillo(radio, material) {
  const m = new THREE.Mesh(new THREE.TorusGeometry(radio, 0.035, 16, 48), material);
  return m; // el anillo mira hacia +Z (eje de giro de la articulación)
}

export function crearLampara(materiales = crearMateriales()) {
  const raiz = new THREE.Group();
  raiz.name = 'lampara';
  const { a1, a2, a3, largo1, largo2, largoPantalla } = POSE;

  // Puntos clave de la cadena
  const j0 = new THREE.Vector3(0, 0.26, 0);                        // arriba de la base
  const d1 = dir(a1), d2 = dir(a2), d3 = dir(a3);
  const j1 = j0.clone().addScaledVector(d1, largo1);               // articulación inferior
  const j2 = j1.clone().addScaledVector(d2, largo2);               // articulación superior

  // 1. Base
  const baseCuerpo = new THREE.Mesh(new THREE.CylinderGeometry(1.0, 1.08, 0.16, 64), materiales.negro);
  const collar = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.42, 0.2, 48), materiales.negro);
  collar.position.y = 0.09;                                        // posiciones locales: la base está en y = 0,08
  const anilloBase = anillo(0.4, materiales.laton);
  anilloBase.rotation.x = Math.PI / 2;
  anilloBase.position.y = 0.19;
  const base = pieza('base', new THREE.Vector3(0, 0.08, 0), [baseCuerpo, collar, anilloBase]);

  // 2. Brazo inferior (de j0 a j1)
  const mid1 = j0.clone().add(j1).multiplyScalar(0.5);
  const cuerpo1 = new THREE.Mesh(new RoundedBoxGeometry(0.2, largo1, 0.2, 4, 0.06), materiales.negro);
  alinear(cuerpo1, d1);
  const brazoInf = pieza('brazo-inferior', mid1, [cuerpo1]);
  brazoInf.userData.extremos = { a: j0.clone(), b: j1.clone() };

  // 3. Articulación inferior
  const esf1 = new THREE.Mesh(new THREE.SphereGeometry(0.26, 32, 24), materiales.negro);
  const art1 = pieza('articulacion-inferior', j1, [esf1, anillo(0.27, materiales.laton)]);

  // 4. Brazo superior (de j1 a j2)
  const mid2 = j1.clone().add(j2).multiplyScalar(0.5);
  const cuerpo2 = new THREE.Mesh(new RoundedBoxGeometry(0.18, largo2, 0.18, 4, 0.055), materiales.negro);
  alinear(cuerpo2, d2);
  const brazoSup = pieza('brazo-superior', mid2, [cuerpo2]);
  brazoSup.userData.extremos = { a: j1.clone(), b: j2.clone() };

  // 5. Articulación superior
  const esf2 = new THREE.Mesh(new THREE.SphereGeometry(0.23, 32, 24), materiales.negro);
  const art2 = pieza('articulacion-superior', j2, [esf2, anillo(0.24, materiales.laton)]);

  // 6. Pantalla: cono truncado abierto. Estrecho junto a j2, ancho en la dirección d3.
  const centroPantalla = j2.clone().addScaledVector(d3, largoPantalla / 2 + 0.05);
  const conoExterior = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.64, largoPantalla, 64, 1, true), materiales.pantalla);
  const conoInterior = new THREE.Mesh(new THREE.CylinderGeometry(0.195, 0.635, largoPantalla - 0.01, 64, 1, true), materiales.interior);
  const cuello = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.2, 0.18, 32), materiales.negro);
  for (const m of [conoExterior, conoInterior, cuello]) alinearEjeInvertido(m, d3);
  cuello.position.copy(d3.clone().multiplyScalar(-(largoPantalla / 2 - 0.02))); // en el extremo estrecho, junto a la articulación
  const pantalla = pieza('pantalla', centroPantalla, [conoExterior, conoInterior, cuello]);
  pantalla.children.forEach((m) => { m.castShadow = false; });
  pantalla.userData.materialColor = materiales.pantalla;

  // 7. Bombilla (con su foco de luz, que viaja con ella)
  const posBombilla = j2.clone().addScaledVector(d3, largoPantalla * 0.72);
  const esfBombilla = new THREE.Mesh(new THREE.SphereGeometry(0.24, 32, 24), materiales.bombilla);
  const bombilla = pieza('bombilla', posBombilla, [esfBombilla]);
  esfBombilla.castShadow = false;
  const foco = new THREE.SpotLight('#ffcf70', 120, 14, 0.95, 0.7, 1.4);
  foco.name = 'foco';
  foco.castShadow = true;
  foco.shadow.mapSize.set(1024, 1024);
  foco.shadow.bias = -0.0005;
  const objetivo = new THREE.Object3D();
  objetivo.position.copy(d3.clone().multiplyScalar(6));
  bombilla.add(objetivo, foco);
  foco.target = objetivo;

  raiz.add(base, brazoInf, art1, brazoSup, art2, pantalla, bombilla);
  return raiz;
}

// El eje local -Y del cono (parte ancha) debe apuntar a lo largo de d3.
function alinearEjeInvertido(objeto, d3) {
  objeto.quaternion.setFromUnitVectors(EJE_Y, d3.clone().negate().normalize());
}

// s en [0,1]. Interpolación suave: arranca y termina despacio. s=0 es la lámpara armada.
export function suavizar(s) {
  const k = THREE.MathUtils.clamp(s, 0, 1);
  return k * k * (3 - 2 * k);
}

export function aplicarExplosion(raiz, s) {
  const e = suavizar(s);
  for (const hijo of raiz.children) {
    if (!hijo.userData.esPieza) continue;
    hijo.position.copy(hijo.userData.reposo).addScaledVector(hijo.userData.explosion, e);
  }
}

export function piezas(raiz) {
  return raiz.children.filter((h) => h.userData.esPieza);
}

export function limites(raiz) {
  raiz.updateWorldMatrix(true, true);
  const caja = new THREE.Box3();
  for (const p of piezas(raiz)) {
    p.traverse((o) => { if (o.isMesh) caja.expandByObject(o); });
  }
  return caja;
}

// Articulated desk lamp built with Three.js primitives. No external models. The colors come from the brief.
// Convention: Three.js axes, Y up. 1 unit ≈ 10 cm.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { BRIEF } from './brief.generated.js';   // product name and palette (generated from brief.json)

export const PART_NAMES = [
  'base',
  'lower-arm',
  'lower-joint',
  'upper-arm',
  'upper-joint',
  'shade',
  'bulb',
];

export const INFO = {
  'base': { title: 'Base', material: 'Matte black steel', detail: 'Flattened cylinder: adds weight and stability.' },
  'lower-arm': { title: 'Lower arm', material: 'Black anodized aluminum', detail: 'First section of the arm. Light and rigid.' },
  'lower-joint': { title: 'Lower joint', material: 'Black steel with a brass ring', detail: 'Rotates to change the height of the lamp.' },
  'upper-arm': { title: 'Upper arm', material: 'Black anodized aluminum', detail: 'Second section. Carries the light over the desk.' },
  'upper-joint': { title: 'Upper joint', material: 'Black steel with a brass ring', detail: 'Rotates to aim the light where you need it.' },
  'shade': { title: 'Shade', material: 'Brushed brass', detail: 'Open cone that focuses the light downwards.' },
  'bulb': { title: 'Bulb', material: 'Warm-light LED (2700 K)', detail: 'Warm light to work without tiring your eyes.' },
};

export const SHADE_COLORS = {
  'Brass': BRIEF.palette.brass,
  'Copper': '#a8532f',
  'Forest green': '#2f5d4a',
  'Midnight blue': '#27426b',
  'Matte black': '#1d2027',
};

// Lamp pose (degrees from the vertical; positive = towards the right). Same as POSE_A in the video.
export const POSE = { a1: -30, a2: 58, a3: 162, length1: 2.4, length2: 2.3, shadeLength: 1.1 };

// Displacement (in units) of each part when the exploded view is 1.
export const EXPLOSION = {
  'base': new THREE.Vector3(0, -1.0, 0.0),
  'lower-arm': new THREE.Vector3(-1.6, 0.0, 1.0),
  'lower-joint': new THREE.Vector3(-1.0, 1.2, -1.0),
  'upper-arm': new THREE.Vector3(0.2, 1.6, 1.0),
  'upper-joint': new THREE.Vector3(1.2, 1.4, -1.0),
  'shade': new THREE.Vector3(2.0, 0.4, 1.0),
  'bulb': new THREE.Vector3(2.4, -0.8, -0.6),
};

const dir = (degrees) => new THREE.Vector3(Math.sin(THREE.MathUtils.degToRad(degrees)), Math.cos(THREE.MathUtils.degToRad(degrees)), 0);
const AXIS_Y = new THREE.Vector3(0, 1, 0);
const align = (object, direction) => object.quaternion.setFromUnitVectors(AXIS_Y, direction.clone().normalize());

export function createMaterials() {
  return {
    black: new THREE.MeshStandardMaterial({ color: BRIEF.palette.metal, metalness: 0.85, roughness: 0.42 }),
    brass: new THREE.MeshStandardMaterial({ color: SHADE_COLORS['Brass'], metalness: 1, roughness: 0.3, side: THREE.DoubleSide }),
    // The shade has its own material: this way the color button does not also change the brass rings of the joints
    shade: new THREE.MeshStandardMaterial({ color: SHADE_COLORS['Brass'], metalness: 1, roughness: 0.3, side: THREE.DoubleSide }),
    bulb: new THREE.MeshStandardMaterial({ color: BRIEF.palette.neutral_light, emissive: BRIEF.palette.accent, emissiveIntensity: 2.2, roughness: 0.4 }),
    inside: new THREE.MeshStandardMaterial({ color: '#f4e3b8', emissive: BRIEF.palette.accent, emissiveIntensity: 0.45, roughness: 0.8, side: THREE.BackSide }),
  };
}

function part(name, position, meshes) {
  const g = new THREE.Group();
  g.name = name;
  g.position.copy(position);
  g.userData = { isPart: true, name, rest: position.clone(), explosion: EXPLOSION[name].clone(), info: INFO[name] };
  for (const m of meshes) {
    m.castShadow = true;
    m.receiveShadow = true;
    g.add(m);
  }
  return g;
}

function ring(radius, material) {
  const m = new THREE.Mesh(new THREE.TorusGeometry(radius, 0.035, 16, 48), material);
  return m; // the ring faces +Z (the joint's rotation axis)
}

export function createLamp(materials = createMaterials()) {
  const root = new THREE.Group();
  root.name = 'lamp';
  const { a1, a2, a3, length1, length2, shadeLength } = POSE;

  // Key points of the chain
  const j0 = new THREE.Vector3(0, 0.26, 0);                        // top of the base
  const d1 = dir(a1), d2 = dir(a2), d3 = dir(a3);
  const j1 = j0.clone().addScaledVector(d1, length1);              // lower joint
  const j2 = j1.clone().addScaledVector(d2, length2);              // upper joint

  // 1. Base
  const baseBody = new THREE.Mesh(new THREE.CylinderGeometry(1.0, 1.08, 0.16, 64), materials.black);
  const collar = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.42, 0.2, 48), materials.black);
  collar.position.y = 0.09;                                        // local positions: the base sits at y = 0.08
  const baseRing = ring(0.4, materials.brass);
  baseRing.rotation.x = Math.PI / 2;
  baseRing.position.y = 0.19;
  const base = part('base', new THREE.Vector3(0, 0.08, 0), [baseBody, collar, baseRing]);

  // 2. Lower arm (from j0 to j1)
  const mid1 = j0.clone().add(j1).multiplyScalar(0.5);
  const body1 = new THREE.Mesh(new RoundedBoxGeometry(0.2, length1, 0.2, 4, 0.06), materials.black);
  align(body1, d1);
  const lowerArm = part('lower-arm', mid1, [body1]);
  lowerArm.userData.ends = { a: j0.clone(), b: j1.clone() };

  // 3. Lower joint
  const sphere1 = new THREE.Mesh(new THREE.SphereGeometry(0.26, 32, 24), materials.black);
  const joint1 = part('lower-joint', j1, [sphere1, ring(0.27, materials.brass)]);

  // 4. Upper arm (from j1 to j2)
  const mid2 = j1.clone().add(j2).multiplyScalar(0.5);
  const body2 = new THREE.Mesh(new RoundedBoxGeometry(0.18, length2, 0.18, 4, 0.055), materials.black);
  align(body2, d2);
  const upperArm = part('upper-arm', mid2, [body2]);
  upperArm.userData.ends = { a: j1.clone(), b: j2.clone() };

  // 5. Upper joint
  const sphere2 = new THREE.Mesh(new THREE.SphereGeometry(0.23, 32, 24), materials.black);
  const joint2 = part('upper-joint', j2, [sphere2, ring(0.24, materials.brass)]);

  // 6. Shade: open truncated cone. Narrow next to j2, wide in direction d3.
  const shadeCenter = j2.clone().addScaledVector(d3, shadeLength / 2 + 0.05);
  const outerCone = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.64, shadeLength, 64, 1, true), materials.shade);
  const innerCone = new THREE.Mesh(new THREE.CylinderGeometry(0.195, 0.635, shadeLength - 0.01, 64, 1, true), materials.inside);
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.2, 0.18, 32), materials.black);
  for (const m of [outerCone, innerCone, neck]) alignInvertedAxis(m, d3);
  neck.position.copy(d3.clone().multiplyScalar(-(shadeLength / 2 - 0.02))); // at the narrow end, next to the joint
  const shade = part('shade', shadeCenter, [outerCone, innerCone, neck]);
  shade.children.forEach((m) => { m.castShadow = false; });
  shade.userData.colorMaterial = materials.shade;

  // 7. Bulb (with its spotlight, which travels with it)
  const bulbPosition = j2.clone().addScaledVector(d3, shadeLength * 0.72);
  const bulbSphere = new THREE.Mesh(new THREE.SphereGeometry(0.24, 32, 24), materials.bulb);
  const bulb = part('bulb', bulbPosition, [bulbSphere]);
  bulbSphere.castShadow = false;
  addSpot(bulb, d3);

  root.add(base, lowerArm, joint1, upperArm, joint2, shade, bulb);
  return root;
}

// The bulb's spotlight (travels with it). Shared by the primitives model and the .glb one: the lights in the file are not used.
export function addSpot(bulb, direction) {
  // `direction` is in WORLD coordinates; the spot's target is placed in the bulb's LOCAL coordinates, which in the .glb inherit
  // the rotation of the pivots (in the primitives they do not rotate and both coincide). Without this conversion, the light pointed elsewhere.
  const rotation = bulb.getWorldQuaternion(new THREE.Quaternion()).invert();
  const spot = new THREE.SpotLight('#ffcf70', 120, 14, 0.95, 0.7, 1.4);
  spot.name = 'spot';
  spot.castShadow = true;
  spot.shadow.mapSize.set(1024, 1024);
  spot.shadow.bias = -0.0005;
  const target = new THREE.Object3D();
  target.position.copy(direction.clone().normalize().applyQuaternion(rotation).multiplyScalar(6));
  bulb.add(target, spot);
  spot.target = target;
  return spot;
}

/**
 * Builds the lamp from the .glb exported by Blender (`gltf.scene`, already loaded).
 * In the file the parts hang from a hierarchy of pivots (each arm moves with the previous one, so the unfolding can be animated).
 * The exploded view needs INDEPENDENT parts: they are moved to the root with `attach`, which keeps their world position and rotation.
 */
export function lampFromGLTF(gltfScene) {
  gltfScene.updateMatrixWorld(true);
  const nodes = {};
  for (const name of PART_NAMES) {
    nodes[name] = gltfScene.getObjectByName(name);
    if (!nodes[name]) throw new Error(`The .glb does not contain the part '${name}'`);
  }
  const root = new THREE.Group();
  root.name = 'lamp';
  for (const name of PART_NAMES) {
    const node = nodes[name];
    root.attach(node);                                   // keeps the world transform
    node.userData = { ...node.userData, isPart: true, name, rest: node.position.clone(), explosion: EXPLOSION[name].clone(), info: INFO[name] };
    node.traverse((o) => {
      if (o.isLight) o.userData.remove = true;           // the lights in the file (Blender candelas) are discarded
      if (o.isMesh) { o.castShadow = name !== 'shade' && name !== 'bulb'; o.receiveShadow = true; }
    });
  }
  const lights = [];
  root.traverse((o) => { if (o.userData.remove) lights.push(o); });
  lights.forEach((l) => l.removeFromParent());

  // In Blender the shade shares its material with the brass rings: it is cloned so the shade color does not change the rings.
  const outer = nodes['shade'].getObjectByName('shade-outer');
  if (outer) {
    outer.material = outer.material.clone();
    nodes['shade'].userData.colorMaterial = outer.material;
  }
  // The light leaves through the open end of the shade: direction upper joint -> bulb.
  const direction = nodes['bulb'].position.clone().sub(nodes['upper-joint'].position).normalize();
  addSpot(nodes['bulb'], direction);
  return root;
}

// The cone's local -Y axis (the wide part) must point along d3.
function alignInvertedAxis(object, d3) {
  object.quaternion.setFromUnitVectors(AXIS_Y, d3.clone().negate().normalize());
}

// s in [0,1]. Smooth interpolation: starts and ends slowly. s=0 is the assembled lamp.
export function ease(s) {
  const k = THREE.MathUtils.clamp(s, 0, 1);
  return k * k * (3 - 2 * k);
}

export function applyExplosion(root, s) {
  const e = ease(s);
  for (const child of root.children) {
    if (!child.userData.isPart) continue;
    child.position.copy(child.userData.rest).addScaledVector(child.userData.explosion, e);
  }
}

export function parts(root) {
  return root.children.filter((h) => h.userData.isPart);
}

export function bounds(root) {
  root.updateWorldMatrix(true, true);
  const box = new THREE.Box3();
  for (const p of parts(root)) {
    p.traverse((o) => { if (o.isMesh) box.expandByObject(o); });
  }
  return box;
}

import { describe, it, expect, beforeAll } from 'vitest';
import { readFileSync } from 'node:fs';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { createLamp, lampFromGLTF, applyExplosion, parts, bounds, PART_NAMES } from './lamp.js';

// The .glb is exported by Blender (blender/build_lamp.py) and copied to viewer/public/lamp.glb.
describe('lamp loaded from the Blender .glb', () => {
  let glb, primitives;
  beforeAll(async () => {
    const bytes = readFileSync(new URL('../public/lamp.glb', import.meta.url));
    const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
    glb = lampFromGLTF(gltf.scene);
    primitives = createLamp();
  });
  const pos = (root, n) => root.getObjectByName(n).position;

  it('has the 7 parts with their names, as direct children of the root', () => {
    expect(parts(glb).map((p) => p.name)).toEqual(PART_NAMES);
    expect(glb.children.filter((h) => h.userData.isPart)).toHaveLength(7);
  });

  it('the joints and the bulb are where the primitives model puts them (same pose, different program)', () => {
    for (const n of ['lower-joint', 'upper-joint', 'bulb']) {
      expect(pos(glb, n).distanceTo(pos(primitives, n)), n).toBeLessThan(0.02);
    }
  });

  it('the shade points the same way: direction upper joint → bulb', () => {
    const d = (r) => pos(r, 'bulb').clone().sub(pos(r, 'upper-joint')).normalize();
    expect(d(glb).distanceTo(d(primitives))).toBeLessThan(0.02);
    expect(d(glb).y).toBeLessThan(-0.8);                      // downwards
  });

  it('the overall size is similar to the primitives one (±0.35 units per axis)', () => {
    applyExplosion(glb, 0); applyExplosion(primitives, 0);
    const a = bounds(glb).getSize(new THREE.Vector3()), b = bounds(primitives).getSize(new THREE.Vector3());
    for (const axis of ['x', 'y', 'z']) expect(Math.abs(a[axis] - b[axis]), axis).toBeLessThan(0.35);
  });

  it('the exploded view moves each part by its full vector, and s = 0 leaves it at rest', () => {
    applyExplosion(glb, 1);
    for (const p of parts(glb)) expect(p.position.distanceTo(p.userData.rest.clone().add(p.userData.explosion)), p.name).toBeLessThan(1e-9);
    applyExplosion(glb, 0);
    for (const p of parts(glb)) expect(p.position.distanceTo(p.userData.rest), p.name).toBe(0);
  });

  it('each part moves on its own: moving one does not drag the others (the pivot hierarchy was broken)', () => {
    applyExplosion(glb, 0);
    const before = parts(glb).map((p) => p.getWorldPosition(new THREE.Vector3()));
    const arm = glb.getObjectByName('lower-arm');
    arm.position.add(new THREE.Vector3(3, 0, 0));
    glb.updateMatrixWorld(true);
    parts(glb).forEach((p, i) => {
      const d = p.getWorldPosition(new THREE.Vector3()).distanceTo(before[i]);
      if (p === arm) expect(d).toBeCloseTo(3, 6); else expect(d, p.name).toBeLessThan(1e-9);
    });
    applyExplosion(glb, 0);
  });

  it('the lights in the file are discarded and the bulb carries the viewer spotlight pointing downwards', () => {
    let lights = 0; glb.traverse((o) => { if (o.isLight) lights++; });
    expect(lights).toBe(1);                                     // only the SpotLight added by the viewer
    const spot = glb.getObjectByName('bulb').getObjectByName('spot');
    expect(spot?.isSpotLight).toBe(true);
    // the light direction is measured in the WORLD (the local position is misleading: the .glb bulb inherits the pivots' rotation)
    glb.updateMatrixWorld(true);
    const toward = spot.target.getWorldPosition(new THREE.Vector3()).sub(spot.getWorldPosition(new THREE.Vector3())).normalize();
    const axis = pos(glb, 'bulb').clone().sub(pos(glb, 'upper-joint')).normalize();
    expect(toward.y).toBeLessThan(-0.8);
    expect(toward.distanceTo(axis)).toBeLessThan(0.02);           // it leaves through the open end of the shade
  });

  it('the shade has its own material: changing its color does not change the joint rings', () => {
    const mat = glb.getObjectByName('shade').userData.colorMaterial;
    expect(mat).toBeTruthy();
    const rings = [];
    glb.traverse((o) => { if (o.isMesh && o.name.endsWith('-ring')) rings.push(o.material); });
    expect(rings.length).toBeGreaterThan(0);
    for (const m of rings) expect(m).not.toBe(mat);
  });

  it('a .glb that is missing a part gives a clear error', () => {
    const empty = new THREE.Group();
    expect(() => lampFromGLTF(empty)).toThrow(/does not contain the part 'base'/);
  });
});

import { describe, it, expect } from 'vitest';
import * as THREE from 'three';
import { createLamp, applyExplosion, parts, bounds, PART_NAMES, INFO, SHADE_COLORS } from './lamp.js';

describe('Arco lamp', () => {
  const lamp = createLamp();

  it('has exactly the 7 parts, with their names and in order', () => {
    expect(parts(lamp).map((p) => p.name)).toEqual(PART_NAMES);
    expect(PART_NAMES).toHaveLength(7);
  });

  it('each part has at least one mesh, info and an explosion vector', () => {
    for (const p of parts(lamp)) {
      const meshes = [];
      p.traverse((o) => o.isMesh && meshes.push(o));
      expect(meshes.length, p.name).toBeGreaterThan(0);
      expect(p.userData.info, p.name).toBe(INFO[p.name]);
      expect(p.userData.explosion.length(), p.name).toBeGreaterThan(0.5);
    }
  });

  it('assembled (s = 0) each part is at its rest position', () => {
    applyExplosion(lamp, 0);
    for (const p of parts(lamp)) expect(p.position.distanceTo(p.userData.rest), p.name).toBe(0);
  });

  it('fully exploded (s = 1) each part is displaced by its full vector', () => {
    applyExplosion(lamp, 1);
    for (const p of parts(lamp)) {
      const expected = p.userData.rest.clone().add(p.userData.explosion);
      expect(p.position.distanceTo(expected), p.name).toBeLessThan(1e-9);
    }
    applyExplosion(lamp, 0);
  });

  it('the separation grows monotonically with the slider and is clamped to [0, 1]', () => {
    let previous = -1;
    for (const s of [0, 0.1, 0.25, 0.5, 0.75, 0.9, 1]) {
      applyExplosion(lamp, s);
      const total = parts(lamp).reduce((a, p) => a + p.position.distanceTo(p.userData.rest), 0);
      expect(total).toBeGreaterThan(previous - 1e-12);
      previous = total;
    }
    applyExplosion(lamp, 7);
    const t7 = parts(lamp).reduce((a, p) => a + p.position.distanceTo(p.userData.rest), 0);
    expect(t7).toBeCloseTo(previous, 9);
    applyExplosion(lamp, -3);
    expect(parts(lamp).every((p) => p.position.distanceTo(p.userData.rest) === 0)).toBe(true);
  });

  it('assembled, the parts fit together: the arms end where the joints are', () => {
    applyExplosion(lamp, 0);
    const by = (n) => lamp.getObjectByName(n);
    const lower = by('lower-arm').userData.ends;
    const upper = by('upper-arm').userData.ends;
    expect(lower.b.distanceTo(by('lower-joint').position)).toBeLessThan(1e-9);
    expect(upper.a.distanceTo(by('lower-joint').position)).toBeLessThan(1e-9);
    expect(upper.b.distanceTo(by('upper-joint').position)).toBeLessThan(1e-9);
    // the lower arm starts on top of the base
    const base = by('base');
    expect(lower.a.y).toBeGreaterThan(base.position.y);
    expect(Math.abs(lower.a.x - base.position.x)).toBeLessThan(1e-9);
  });

  it('the bulb sits inside the shade and the spotlight points downwards', () => {
    applyExplosion(lamp, 0);
    const bulb = lamp.getObjectByName('bulb');
    const shade = lamp.getObjectByName('shade');
    expect(bulb.position.distanceTo(shade.position)).toBeLessThan(1.1);
    const spot = bulb.getObjectByName('spot');
    const toward = new THREE.Vector3().subVectors(spot.target.position, new THREE.Vector3(0, 0, 0)).normalize();
    expect(toward.y).toBeLessThan(-0.8);
  });

  it('everything fits in a reasonable frame, assembled and exploded', () => {
    applyExplosion(lamp, 0);
    const assembled = bounds(lamp).getSize(new THREE.Vector3());
    applyExplosion(lamp, 1);
    const exploded = bounds(lamp).getSize(new THREE.Vector3());
    expect(Math.max(assembled.x, assembled.y)).toBeLessThan(6);
    expect(Math.max(exploded.x, exploded.y, exploded.z)).toBeLessThan(10);
    applyExplosion(lamp, 0);
  });

  it('there are at least 4 shade colors, all valid', () => {
    const colors = Object.values(SHADE_COLORS);
    expect(colors.length).toBeGreaterThanOrEqual(4);
    for (const c of colors) expect(new THREE.Color(c).isColor).toBe(true);
  });
});

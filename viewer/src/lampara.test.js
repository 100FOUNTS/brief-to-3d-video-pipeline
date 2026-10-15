import { describe, it, expect } from 'vitest';
import * as THREE from 'three';
import { crearLampara, aplicarExplosion, piezas, limites, NOMBRES, INFO, COLORES_PANTALLA } from './lampara.js';

describe('lámpara Arco', () => {
  const lampara = crearLampara();

  it('tiene exactamente las 7 piezas, con sus nombres y en orden', () => {
    expect(piezas(lampara).map((p) => p.name)).toEqual(NOMBRES);
    expect(NOMBRES).toHaveLength(7);
  });

  it('cada pieza tiene al menos una malla, información y un vector de explosión', () => {
    for (const p of piezas(lampara)) {
      const mallas = [];
      p.traverse((o) => o.isMesh && mallas.push(o));
      expect(mallas.length, p.name).toBeGreaterThan(0);
      expect(p.userData.info, p.name).toBe(INFO[p.name]);
      expect(p.userData.explosion.length(), p.name).toBeGreaterThan(0.5);
    }
  });

  it('armada (s = 0) cada pieza está en su posición de reposo', () => {
    aplicarExplosion(lampara, 0);
    for (const p of piezas(lampara)) expect(p.position.distanceTo(p.userData.reposo), p.name).toBe(0);
  });

  it('totalmente explosionada (s = 1) cada pieza está desplazada su vector completo', () => {
    aplicarExplosion(lampara, 1);
    for (const p of piezas(lampara)) {
      const esperado = p.userData.reposo.clone().add(p.userData.explosion);
      expect(p.position.distanceTo(esperado), p.name).toBeLessThan(1e-9);
    }
    aplicarExplosion(lampara, 0);
  });

  it('la separación crece de forma monótona con el deslizador y se limita a [0, 1]', () => {
    let anterior = -1;
    for (const s of [0, 0.1, 0.25, 0.5, 0.75, 0.9, 1]) {
      aplicarExplosion(lampara, s);
      const total = piezas(lampara).reduce((a, p) => a + p.position.distanceTo(p.userData.reposo), 0);
      expect(total).toBeGreaterThan(anterior - 1e-12);
      anterior = total;
    }
    aplicarExplosion(lampara, 7);
    const t7 = piezas(lampara).reduce((a, p) => a + p.position.distanceTo(p.userData.reposo), 0);
    expect(t7).toBeCloseTo(anterior, 9);
    aplicarExplosion(lampara, -3);
    expect(piezas(lampara).every((p) => p.position.distanceTo(p.userData.reposo) === 0)).toBe(true);
  });

  it('armada, las piezas encajan: los brazos terminan donde están las articulaciones', () => {
    aplicarExplosion(lampara, 0);
    const por = (n) => lampara.getObjectByName(n);
    const inf = por('brazo-inferior').userData.extremos;
    const sup = por('brazo-superior').userData.extremos;
    expect(inf.b.distanceTo(por('articulacion-inferior').position)).toBeLessThan(1e-9);
    expect(sup.a.distanceTo(por('articulacion-inferior').position)).toBeLessThan(1e-9);
    expect(sup.b.distanceTo(por('articulacion-superior').position)).toBeLessThan(1e-9);
    // el brazo inferior arranca sobre la base
    const base = por('base');
    expect(inf.a.y).toBeGreaterThan(base.position.y);
    expect(Math.abs(inf.a.x - base.position.x)).toBeLessThan(1e-9);
  });

  it('la bombilla queda dentro de la pantalla y el foco apunta hacia abajo', () => {
    aplicarExplosion(lampara, 0);
    const bombilla = lampara.getObjectByName('bombilla');
    const pantalla = lampara.getObjectByName('pantalla');
    expect(bombilla.position.distanceTo(pantalla.position)).toBeLessThan(1.1);
    const foco = bombilla.getObjectByName('foco');
    const hacia = new THREE.Vector3().subVectors(foco.target.position, new THREE.Vector3(0, 0, 0)).normalize();
    expect(hacia.y).toBeLessThan(-0.8);
  });

  it('todo cabe en un encuadre razonable, armada y explosionada', () => {
    aplicarExplosion(lampara, 0);
    const armada = limites(lampara).getSize(new THREE.Vector3());
    aplicarExplosion(lampara, 1);
    const explosionada = limites(lampara).getSize(new THREE.Vector3());
    expect(Math.max(armada.x, armada.y)).toBeLessThan(6);
    expect(Math.max(explosionada.x, explosionada.y, explosionada.z)).toBeLessThan(10);
    aplicarExplosion(lampara, 0);
  });

  it('hay al menos 4 colores de pantalla, todos válidos', () => {
    const colores = Object.values(COLORES_PANTALLA);
    expect(colores.length).toBeGreaterThanOrEqual(4);
    for (const c of colores) expect(new THREE.Color(c).isColor).toBe(true);
  });
});

import { describe, it, expect, beforeAll } from 'vitest';
import { readFileSync } from 'node:fs';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { crearLampara, lamparaDesdeGLTF, aplicarExplosion, piezas, limites, NOMBRES } from './lampara.js';

// El .glb lo exporta Blender (blender/build_lamp.py) y se copia a viewer/public/lampara.glb.
describe('lámpara cargada desde el .glb de Blender', () => {
  let glb, primitivas;
  beforeAll(async () => {
    const bytes = readFileSync(new URL('../public/lampara.glb', import.meta.url));
    const gltf = await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength), '');
    glb = lamparaDesdeGLTF(gltf.scene);
    primitivas = crearLampara();
  });
  const pos = (raiz, n) => raiz.getObjectByName(n).position;

  it('trae las 7 piezas con su nombre, como hijos directos de la raíz', () => {
    expect(piezas(glb).map((p) => p.name)).toEqual(NOMBRES);
    expect(glb.children.filter((h) => h.userData.esPieza)).toHaveLength(7);
  });

  it('las articulaciones y la bombilla están donde las pone el modelo de primitivas (misma postura, otro programa)', () => {
    for (const n of ['articulacion-inferior', 'articulacion-superior', 'bombilla']) {
      expect(pos(glb, n).distanceTo(pos(primitivas, n)), n).toBeLessThan(0.02);
    }
  });

  it('la pantalla apunta igual: dirección articulación superior → bombilla', () => {
    const d = (r) => pos(r, 'bombilla').clone().sub(pos(r, 'articulacion-superior')).normalize();
    expect(d(glb).distanceTo(d(primitivas))).toBeLessThan(0.02);
    expect(d(glb).y).toBeLessThan(-0.8);                      // hacia abajo
  });

  it('el tamaño total es parecido al de las primitivas (±0,35 unidades por eje)', () => {
    aplicarExplosion(glb, 0); aplicarExplosion(primitivas, 0);
    const a = limites(glb).getSize(new THREE.Vector3()), b = limites(primitivas).getSize(new THREE.Vector3());
    for (const eje of ['x', 'y', 'z']) expect(Math.abs(a[eje] - b[eje]), eje).toBeLessThan(0.35);
  });

  it('la vista explosionada mueve cada pieza su vector completo, y s = 0 la deja en reposo', () => {
    aplicarExplosion(glb, 1);
    for (const p of piezas(glb)) expect(p.position.distanceTo(p.userData.reposo.clone().add(p.userData.explosion)), p.name).toBeLessThan(1e-9);
    aplicarExplosion(glb, 0);
    for (const p of piezas(glb)) expect(p.position.distanceTo(p.userData.reposo), p.name).toBe(0);
  });

  it('cada pieza se mueve sola: mover una no arrastra a las demás (se rompió la jerarquía de pivotes)', () => {
    aplicarExplosion(glb, 0);
    const antes = piezas(glb).map((p) => p.getWorldPosition(new THREE.Vector3()));
    const brazo = glb.getObjectByName('brazo-inferior');
    brazo.position.add(new THREE.Vector3(3, 0, 0));
    glb.updateMatrixWorld(true);
    piezas(glb).forEach((p, i) => {
      const d = p.getWorldPosition(new THREE.Vector3()).distanceTo(antes[i]);
      if (p === brazo) expect(d).toBeCloseTo(3, 6); else expect(d, p.name).toBeLessThan(1e-9);
    });
    aplicarExplosion(glb, 0);
  });

  it('las luces del archivo se descartan y la bombilla lleva el foco del visor apuntando hacia abajo', () => {
    let luces = 0; glb.traverse((o) => { if (o.isLight) luces++; });
    expect(luces).toBe(1);                                     // solo el SpotLight que añade el visor
    const foco = glb.getObjectByName('bombilla').getObjectByName('foco');
    expect(foco?.isSpotLight).toBe(true);
    // la dirección de la luz se mide en el MUNDO (la posición local engaña: la bombilla del .glb hereda el giro de los pivotes)
    glb.updateMatrixWorld(true);
    const haciaDonde = foco.target.getWorldPosition(new THREE.Vector3()).sub(foco.getWorldPosition(new THREE.Vector3())).normalize();
    const eje = pos(glb, 'bombilla').clone().sub(pos(glb, 'articulacion-superior')).normalize();
    expect(haciaDonde.y).toBeLessThan(-0.8);
    expect(haciaDonde.distanceTo(eje)).toBeLessThan(0.02);           // sale por el extremo abierto de la pantalla
  });

  it('la pantalla tiene su propio material: cambiarle el color no cambia los anillos de las articulaciones', () => {
    const mat = glb.getObjectByName('pantalla').userData.materialColor;
    expect(mat).toBeTruthy();
    const anillos = [];
    glb.traverse((o) => { if (o.isMesh && o.name.endsWith('-anillo')) anillos.push(o.material); });
    expect(anillos.length).toBeGreaterThan(0);
    for (const m of anillos) expect(m).not.toBe(mat);
  });

  it('un .glb al que le falta una pieza da un error claro', () => {
    const vacio = new THREE.Group();
    expect(() => lamparaDesdeGLTF(vacio)).toThrow(/no trae la pieza 'base'/);
  });
});

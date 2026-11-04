import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import {MeshInspection} from '../mesh-inspection.js';
import {makeTerrain,facadeMaterial} from '../world.js';
import {CityStreaming,disposeGroup} from '../streaming.js';
import {BridgeLayer} from '../bridges.js';
import {disposeOfficialModel} from '../official-model-assets.js';

const terrainData = {w: 3, h: 3, elev: Array(9).fill(8), vegetation: Array(9).fill(0), meta: {georef: {bE: 834500, bN: 816500, aE: 70, aN: -70}}};
const material = () => new THREE.MeshStandardMaterial({color: '#aacccc', roughness: .6});
const mesh = (mat = material()) => new THREE.Mesh(new THREE.BoxGeometry(10, 12, 10), mat);
const lighting = {night: {value: 0}, activity: {value: [1, 1, 1, 1]}, retail: {value: 1}, elapsed: {value: 0}, shimmer: {value: 1}};

function fixture() {
 const inspection = new MeshInspection(), scene = new THREE.Scene(), group = new THREE.Group(); scene.add(group);
 const source = mesh(); source.castShadow = source.receiveShadow = true; group.add(source); inspection.register(group, 'structures');
 return {inspection, scene, group, source};
}

test('off by default; source triangles, transforms, material and visibility restore after repeated modes', () => {
 const {inspection, group, source} = fixture(), original = source.material, geometry = source.geometry;
 source.position.set(14, 72, -5); source.rotation.y = .4; source.visible = false; source.updateMatrixWorld(true);
 const matrix = source.matrixWorld.clone(), position = geometry.attributes.position.array.slice(), index = geometry.index.array.slice();
 assert.equal(inspection.state.mode, 'solid'); assert.equal(source.children.length, 0); assert.equal(source.material, original);
 for (let i = 0; i < 3; i++) {
  inspection.set({mode: 'overlay', opacity: 45});
  const overlay = source.children[0]; assert.equal(overlay.geometry, geometry); assert.equal(overlay.material.wireframe, true);
  assert.equal(source.children.length, 1); assert.equal(source.material.opacity, .45); assert.equal(source.material.onBeforeCompile, original.onBeforeCompile);
  assert.equal(source.visible, false); assert.equal(source.castShadow, true); assert.equal(overlay.castShadow, false);
  inspection.set({mode: 'wireframe'}); assert.equal(source.children[0], overlay); assert.equal(source.material.colorWrite, false); assert.equal(source.material.depthWrite, true);
  assert.equal(source.material.wireframe, false, 'retain solid shadow silhouette');
  inspection.set({mode: 'solid'}); assert.equal(source.material, original); assert.equal(source.children.length, 0); assert.equal(inspection.state.materialPairs, 0);
 }
 source.updateMatrixWorld(true); assert.deepEqual(source.matrixWorld, matrix); assert.deepEqual(geometry.attributes.position.array, position); assert.deepEqual(geometry.index.array, index);
 assert.equal(source.visible, false); assert.equal(source.receiveShadow, true); disposeGroup(group); assert.equal(inspection.records.size, 0);
});

test('terrain includes patch triangles and target isolation respects hidden layers', () => {
 const inspection = new MeshInspection(), scene = new THREE.Scene();
 const patch = {...terrainData, w: 2, h: 2, elev: [8, 9, 10, 11], vegetation: [0, 0, 0, 0], coarseCells: [0, 0, 1, 1], meta: {georef: {...terrainData.meta.georef, aE: 35, aN: -35}}};
 const terrain = makeTerrain({...terrainData, patches: [patch]}), structures = mesh(); scene.add(terrain, structures);
 inspection.register(terrain, 'terrain'); inspection.register(structures, 'structures');
 const terrainSources = [...inspection.records.values()].filter(r => r.target === 'terrain'); assert.equal(terrainSources.length, 2);
 const triangles = terrainSources.map(r => r.mesh.geometry.index.count); assert.ok(triangles.every(n => n > 0));
 structures.visible = false; const original = structures.material;
 inspection.set({mode: 'wireframe', targets: {terrain: true, structures: false}});
 assert.equal(inspection.state.overlays, 2); assert.equal(structures.material, original); assert.equal(structures.visible, false);
 for (const record of terrainSources) assert.equal(record.overlay.geometry.index, record.mesh.geometry.index);
 inspection.set({targets: {terrain: false, structures: true}}); assert.equal(inspection.state.overlays, 1); assert.equal(structures.visible, false);
 for (const record of terrainSources) assert.equal(record.mesh.material, record.original);
 inspection.dispose(); disposeGroup(terrain); disposeGroup(structures);
});

test('night shader hooks, cache keys, source textures and multi-material properties survive reveal', () => {
 const inspection = new MeshInspection(), source = mesh(), facade = facadeMaterial('#ffffff', lighting), texture = new THREE.Texture();
 facade.map = texture; facade.opacity = .8; facade.transparent = true; facade.depthWrite = false; facade.side = THREE.DoubleSide;
 facade.customProgramCacheKey = () => 'test-night-source'; const other = material(); other.visible = false;
 const originals = [facade, other]; source.material = originals; inspection.register(source, 'structures');
 inspection.set({mode: 'overlay', opacity: 50});
 assert.equal(source.material[0].map, texture); assert.equal(source.material[0].opacity, .4); assert.equal(source.material[0].side, THREE.DoubleSide);
 assert.equal(source.material[0].customProgramCacheKey(), 'test-night-source');
 const shader = {uniforms: {}, vertexShader: '#include <common>\n#include <begin_vertex>', fragmentShader: '#include <common>\n#include <color_fragment>\n#include <emissivemap_fragment>'};
 source.material[0].onBeforeCompile(shader); lighting.night.value = 1; assert.equal(shader.uniforms.uCityNight.value, 1); assert.match(shader.fragmentShader, /windowLight/);
 assert.equal(source.children[0].material[1].visible, false);
 let textureDisposed = 0; texture.addEventListener('dispose', () => textureDisposed++);
 inspection.set({mode: 'solid'}); assert.equal(source.material, originals); assert.equal(facade.opacity, .8); assert.equal(facade.depthWrite, false); assert.equal(textureDisposed, 0);
 inspection.dispose(); disposeGroup(source); texture.dispose();
});

test('new roots inherit settings, shared materials release exactly once, eviction restores ownership', () => {
 const {inspection, scene, group, source} = fixture(), original = source.material;
 inspection.set({mode: 'overlay'}); const lateGroup = new THREE.Group(), late = mesh(original); lateGroup.add(late); scene.add(lateGroup); inspection.register(lateGroup, 'structures'); inspection.register(lateGroup, 'structures');
 assert.equal(source.material, late.material); assert.equal(inspection.state.materialPairs, 1); assert.equal(late.children.length, 1);
 let skinDisposed = 0, wireDisposed = 0, geometryDisposed = 0, originalDisposed = 0;
 source.material.addEventListener('dispose', () => skinDisposed++); source.children[0].material.addEventListener('dispose', () => wireDisposed++);
 late.geometry.addEventListener('dispose', () => geometryDisposed++); original.addEventListener('dispose', () => originalDisposed++);
 lateGroup.removeFromParent(); assert.equal(late.material, original); assert.equal(late.children.length, 0); assert.equal(skinDisposed, 0); assert.equal(geometryDisposed, 0);
 group.removeFromParent(); assert.equal(source.material, original); assert.equal(skinDisposed, 1); assert.equal(wireDisposed, 1); assert.equal(originalDisposed, 0); assert.equal(inspection.state.overlays, 0);
 source.geometry.dispose(); late.geometry.dispose(); original.dispose();
});

test('triangle overlay cannot intercept picking; source mesh and face indices remain stable', () => {
 const {inspection, group, source} = fixture(); source.updateMatrixWorld(true);
 const ray = new THREE.Raycaster(new THREE.Vector3(0, 0, 30), new THREE.Vector3(0, 0, -1));
 const before = ray.intersectObject(source, true)[0]; assert.ok(before);
 for (const mode of ['overlay', 'wireframe', 'solid']) {
  inspection.set({mode}); source.updateMatrixWorld(true);
  const hits = ray.intersectObject(source, true); assert.equal(hits[0].object, source); assert.equal(hits[0].faceIndex, before.faceIndex); assert.ok(hits.every(hit => hit.object === source));
 }
 disposeGroup(group);
});

test('bridge rail instances preserve their transforms, LOD visibility and release derived buffers', async () => {
 const inspection = new MeshInspection(), scene = new THREE.Scene(); inspection.set({mode: 'overlay'});
 const layer = new BridgeLayer({scene, inspection, sampler: {height: () => 0}, prepare: data => data});
 const record = {id: 'way/1', sourceId: 'way/1', source: 'test', kind: 'footway', role: 'bridge', width: 3, covered: true, deckPath: [[0, 8, 0], [20, 8, 0]], bounds: [-2, -2, 22, 2]};
 const previous = globalThis.fetch; globalThis.fetch = async () => ({ok: true, json: async () => [record]});
 try { assert.equal(await layer.load('test'), true); } finally { globalThis.fetch = previous; }
 const group = [...layer.cache.values()][0], rails = group.userData.railMesh, overlay = rails.children[0];
 assert.ok(overlay.isInstancedMesh); assert.equal(overlay.geometry, rails.geometry); assert.equal(overlay.count, rails.count); assert.notEqual(overlay.instanceMatrix, rails.instanceMatrix);
 assert.deepEqual(overlay.instanceMatrix.array, rails.instanceMatrix.array);
 let disposed = 0; overlay.addEventListener('dispose', () => disposed++);
 layer.plan(0, 0, 3000, new THREE.Vector3(0, 10000, 0)); assert.equal(rails.visible, false);
 layer.plan(50000, 50000); assert.equal(inspection.records.size, 0); assert.equal(inspection.state.materialPairs, 0); assert.equal(disposed, 1);
 layer.dispose(); inspection.dispose();
});

test('streamed bases, detailed government replacements and fallback bakes inherit wireframe and clean up', async t => {
 const inspection = new MeshInspection(), scene = new THREE.Scene(); inspection.set({mode: 'wireframe'});
 const building = {uid: 'landsd/1:0', id: 'landsd/1', tile: '0_0', kind: 'yes', base: 2, height: 12, minimum: 0, rings: [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]], centre: [5, 5]};
 const data = {id: '0_0', buildings: [building], roads: [], parks: []};
 const manifest = {tileSize: 2000, tiles: [{id: '0_0', url: 'tile', bounds: [0, 0, 2000, 2000], centre: [1000, 1000]}]};
 const stream = new CityStreaming({manifest, terrain: terrainData, sampler: {height: () => 2}, scene, inspection, activity: {buildings: {}}});
 t.mock.method(globalThis, 'fetch', async () => ({ok: true, json: async () => structuredClone(data)}));
 stream.cache.plan(['0_0']); await stream.cache.waitFor(['0_0']);
 const base = stream.cache.entries.get('0_0').buildings.group.children[0]; assert.equal(base.children[0].material.wireframe, true);
 const geometry = new THREE.BoxGeometry(10, 12, 10).toNonIndexed(); geometry.translate(5, 8, 5);
 const source = new THREE.Mesh(geometry, material()), group = new THREE.Group(); group.add(source);
 const bounds = new THREE.Box3().setFromObject(group), detail = {group, meshes: [source], bounds, record: {...building, modelGeometry: {position: geometry.attributes.position.array, triangles: geometry.attributes.position.count / 3}}};
 assert.equal(await stream.setDetailedModel(building.uid, detail), true); assert.equal(source.children.length, 1); assert.equal(source.material.colorWrite, false); assert.equal(base.children.length, 0);
 assert.equal(await stream.setDetailedModel(building.uid, null), true); assert.equal(source.children.length, 0);
 const fallback = stream.cache.entries.get('0_0').buildings.group.children[0]; assert.equal(fallback.children.length, 1); assert.equal(fallback.material.colorWrite, false);
 disposeOfficialModel(detail); stream.cache.close(); assert.equal(inspection.records.size, 0); assert.equal(inspection.state.materialPairs, 0); inspection.dispose();
});


test('zero-opacity inspection skips facade shading and hides back faces without changing shadow or pick surfaces', () => {
 const {inspection, group, source} = fixture(), original = source.material;
 inspection.set({mode: 'overlay', opacity: 35});
 assert.equal(source.material.transparent, true); assert.equal(source.material.depthWrite, true);
 assert.equal(source.children[0].material.transparent, true, 'wire renders in the same queue after translucent skins');
 assert.ok(source.children[0].renderOrder > source.renderOrder);
 inspection.set({opacity: 0});
 assert.equal(source.material.isMeshBasicMaterial, true); assert.equal(source.material.transparent, false);
 assert.equal(source.material.colorWrite, false); assert.equal(source.material.depthWrite, true);
 assert.equal(source.material.onBeforeCompile, THREE.Material.prototype.onBeforeCompile, 'unlit depth pass runs no facade callback');
 assert.equal(source.material.wireframe, false); assert.equal(source.castShadow, true);
 assert.equal(source.children[0].material.transparent, false); assert.equal(source.children[0].material.side, original.side);
 inspection.set({opacity: 100}); assert.equal(source.material.transparent, false); assert.equal(source.material.isMeshStandardMaterial, true);
 assert.equal(source.children[0].material.transparent, false);
 inspection.set({mode: 'solid'}); assert.equal(source.material, original); disposeGroup(group);
});

test('day/night palette switches only derived wires and newly attached meshes inherit it', () => {
 const {inspection, scene, group, source} = fixture(), original = source.material, originalColour = original.color.clone();
 inspection.set({mode: 'wireframe'}); const wire = source.children[0].material, day = wire.color.clone(), depth = source.material;
 inspection.setNight(true); assert.notDeepEqual(wire.color, day); assert.equal(source.material, depth);
 inspection.setNight(true); assert.equal(source.children[0].material, wire);
 const late = mesh(); scene.add(late); inspection.register(late, 'structures'); assert.deepEqual(late.children[0].material.color, wire.color);
 inspection.setNight(false); assert.deepEqual(wire.color, day); assert.deepEqual(original.color, originalColour);
 inspection.set({mode: 'solid'}); assert.equal(source.material, original); disposeGroup(group); disposeGroup(late);
});

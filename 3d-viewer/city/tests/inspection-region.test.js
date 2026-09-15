import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import {selectInspectionRegion,regionWireMesh,inspectionShader,INSPECTION_PROFILES} from '../inspection-region.js';
import {MeshInspection} from '../mesh-inspection.js';
import {facadeMaterial} from '../world.js';

function source() {
 const geometry = new THREE.BufferGeometry(), values = [];
 for (let i = 0; i < 100; i++) values.push(i * 10, 0, 0, i * 10 + 2, 0, 0, i * 10, 2, 2);
 geometry.setAttribute('position', new THREE.Float32BufferAttribute(values, 3)); geometry.setIndex(Array.from({length: 300}, (_, i) => i));
 geometry.addGroup(0, 150, 0); geometry.addGroup(150, 150, 1);
 const mesh = new THREE.Mesh(geometry, [new THREE.MeshStandardMaterial(), new THREE.MeshStandardMaterial()]);
 const scene = new THREE.Scene(); scene.add(mesh); return {scene, mesh, record: {mesh, target: 'structures'}};
}

test('adaptive focus bounds all wire triangles without dropping faces inside the selected circle', () => {
 const {record} = source(), region = selectInspectionRegion([record], {x: 0, z: 0}, {radius: 1000, triangles: 12});
 assert.equal(region.triangles, 12); assert.ok(region.radius > 110 && region.radius < 120);
 assert.deepEqual(region.selected.get(record).map(c => c.offset), Array.from({length: 12}, (_, i) => i * 3));
 const impossible = selectInspectionRegion([record], {x: 0, z: 0}, {radius: 1000, triangles: 0}); assert.equal(impossible.radius, 0); assert.equal(impossible.triangles, 0);
 assert.ok(INSPECTION_PROFILES.mobile.triangles < INSPECTION_PROFILES.desktop.triangles);
});

test('bounded geometry keeps exact source triangle topology, material groups and transforms with owned buffers', () => {
 const {mesh, record} = source(); mesh.position.set(500, 7, -12); mesh.rotation.y = .2;
 const region = selectInspectionRegion([record], {x: 1040, z: -120}, {radius: 150, triangles: 80}), candidates = region.selected.get(record); assert.ok(candidates.length > 0);
 const before = mesh.geometry.attributes.position.array.slice(), wire = regionWireMesh(record, candidates, mesh.material), geometry = wire.geometry;
 assert.notEqual(geometry.attributes.position, mesh.geometry.attributes.position);
 assert.ok(geometry.attributes.position.count <= region.triangles * 3);
 for (let i = 0; i < geometry.index.count; i++) {
  const vertex = geometry.index.getX(i), originalVertex = geometry.userData.inspectionSourceVertices[vertex], offset = geometry.userData.inspectionSourceOffsets[Math.floor(i / 3)];
  assert.equal(originalVertex, mesh.geometry.index.getX(offset + i % 3));
  for (const name of ['getX', 'getY', 'getZ']) assert.equal(geometry.attributes.position[name](vertex), mesh.geometry.attributes.position[name](originalVertex));
 }
 for (const group of geometry.groups) for (let i = group.start; i < group.start + group.count; i += 3) assert.equal(group.materialIndex, geometry.userData.inspectionSourceOffsets[i / 3] < 150 ? 0 : 1);
 let disposed = 0; mesh.geometry.addEventListener('dispose', () => disposed++); geometry.dispose(); assert.equal(disposed, 0); assert.deepEqual(mesh.geometry.attributes.position.array, before);
});

test('instance selection counts every real triangle and retains chosen source matrices', () => {
 const mesh = new THREE.InstancedMesh(new THREE.BoxGeometry(2, 2, 2), new THREE.MeshStandardMaterial(), 10), matrix = new THREE.Matrix4();
 for (let i = 0; i < 10; i++) mesh.setMatrixAt(i, matrix.makeTranslation(i * 30, 20, 0));
 const record = {mesh}, region = selectInspectionRegion([record], {x: 0, z: 0}, {radius: 300, triangles: 24});
 assert.equal(region.triangles, 24); const selected = region.selected.get(record), wire = regionWireMesh(record, selected, mesh.material); assert.equal(wire.count, 2);
 assert.equal(wire.geometry, mesh.geometry);
 for (let i = 0; i < wire.count; i++) { const original = new THREE.Matrix4(), derived = new THREE.Matrix4(); mesh.getMatrixAt(selected[i].instance, original); wire.getMatrixAt(i, derived); assert.deepEqual(derived, original); }
 wire.dispose(); mesh.dispose(); mesh.geometry.dispose(); mesh.material.dispose();
});

test('regional shader keeps far skins unchanged, uses instance/world positions, and writes logarithmic depth before zero-opacity return', () => {
 const uniforms = {focus: {value: new THREE.Vector2()}, radius: {value: 100}, opacity: {value: 0}};
 const shader = {uniforms: {}, vertexShader: '#include <common>\n#include <project_vertex>', fragmentShader: '#include <common>\nvoid main() {\n#include <logdepthbuf_fragment>\n#include <opaque_fragment>\n}'};
 inspectionShader(shader, uniforms); assert.equal(shader.uniforms.uInspectionOpacity, uniforms.opacity);
 assert.match(shader.vertexShader, /instanceMatrix \* inspectionPosition/); assert.match(shader.vertexShader, /modelMatrix \* inspectionPosition/);
 assert.ok(shader.fragmentShader.indexOf('return;') > shader.fragmentShader.indexOf('#include <logdepthbuf_fragment>'));
 assert.match(shader.fragmentShader, /if \(distance\(vInspectionXZ, uInspectionFocus\) <= uInspectionRadius\) gl_FragColor.a \*= uInspectionOpacity/);
 const wire = {uniforms: {}, vertexShader: '#include <common>\n#include <project_vertex>', fragmentShader: '#include <common>\nvoid main() {'}; inspectionShader(wire, uniforms, {wire: true}); assert.match(wire.fragmentShader, /> uInspectionRadius\) discard/);
});

test('bounded controller preserves distant source materials and restores, disposes and refreshes on focus/LOD/stream changes', () => {
 const {mesh, scene} = source(), inspection = new MeshInspection({bounded: true, profile: 'mobile'}), originals = mesh.material;
 const distant = new THREE.Mesh(new THREE.BoxGeometry(4, 4, 4), new THREE.MeshStandardMaterial()); distant.position.x = 2000; scene.add(distant); const distantOriginal = distant.material;
 inspection.register(mesh, 'structures'); inspection.register(distant, 'structures'); inspection.plan({x: 0, z: 0}); inspection.set({mode: 'wireframe'});
 assert.equal(distant.material, distantOriginal); assert.equal(distant.children.length, 0);
 assert.equal(mesh.material[0].opacity, originals[0].opacity); assert.equal(mesh.material[0].colorWrite, true); assert.equal(mesh.material[0].depthWrite, true);
 const derived = mesh.children[0].geometry; let sourceDisposals = 0, derivedDisposals = 0; mesh.geometry.addEventListener('dispose', () => sourceDisposals++); derived.addEventListener('dispose', () => derivedDisposals++);
 inspection.plan({x: 2000, z: 0}); assert.equal(mesh.material, originals); assert.equal(derivedDisposals, 1); assert.equal(sourceDisposals, 0); assert.equal(distant.children.length, 1);
 distant.visible = false; inspection.plan({x: 2000, z: 0}); assert.equal(distant.children.length, 0); distant.visible = true; inspection.plan({x: 2000, z: 0}); assert.equal(distant.children.length, 1);
 const late = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshStandardMaterial()); late.position.x = 2005; scene.add(late); inspection.register(late, 'structures'); inspection.plan({x: 2000, z: 0}); assert.equal(late.children.length, 1);
 inspection.set({mode: 'solid'}); assert.equal(distant.material, distantOriginal); assert.equal(inspection.state.overlays, 0); assert.equal(inspection.state.materialPairs, 0); assert.equal(inspection.state.scope.triangles, 0);
 for (const record of inspection.records.values()) assert.equal(record.candidates, null); inspection.dispose();
});

test('region-decorated facade keeps the live original city-clock uniforms', () => {
 const lighting = {night: {value: 0}, activity: {value: [1, 1, 1, 1]}, retail: {value: 1}, elapsed: {value: 0}, shimmer: {value: 1}};
 const original = facadeMaterial('#ffffff', lighting), mesh = new THREE.Mesh(new THREE.BoxGeometry(5, 5, 5), original), inspection = new MeshInspection({bounded: true});
 inspection.register(mesh, 'structures'); inspection.plan({x: 0, z: 0}); inspection.set({mode: 'overlay', opacity: 35});
 const shader = {uniforms: {}, vertexShader: '#include <common>\n#include <begin_vertex>\n#include <project_vertex>', fragmentShader: '#include <common>\nvoid main() {\n#include <logdepthbuf_fragment>\n#include <color_fragment>\n#include <emissivemap_fragment>\n#include <opaque_fragment>\n}'};
 mesh.material.onBeforeCompile(shader); lighting.night.value = 1; assert.equal(shader.uniforms.uCityNight.value, 1); assert.equal(shader.uniforms.uInspectionOpacity.value, .35); assert.match(shader.fragmentShader, /windowLight/);
 inspection.set({mode: 'solid'}); assert.equal(mesh.material, original); inspection.dispose();
});

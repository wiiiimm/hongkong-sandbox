import * as THREE from '../vendor/three.module.js';
import {INSPECTION_PROFILES,selectInspectionRegion,regionWireMesh,inspectionShader,inspectionVisible} from './inspection-region.js';

const MODES = new Set(['solid', 'overlay', 'wireframe']);
const TARGETS = ['terrain', 'structures'];
const NO_PICK = () => {};
/** Triangle inspection retains real source triangles and draw groups. City uses
 * a bounded, indexed position subset around the view focus; it never expands the
 * whole territory or invents grid/edge geometry. Owners register new roots and
 * release before eviction. Planning uses the registry on the 600 ms cadence.
 */
export class MeshInspection {
 constructor({bounded = false, profile = 'desktop'} = {}) {
  this.bounded = bounded; this.profile = INSPECTION_PROFILES[profile]; this.focus = {x: 0, z: 420}; this.dirty = true;
  this.region = {radius: 0, triangles: 0}; this.regionUniforms = {focus: {value: new THREE.Vector2(0, 420)}, radius: {value: 0}, opacity: {value: .65}};
  this.mode = 'solid'; this.opacity = 65; this.night = false;
  this.targets = {terrain: true, structures: true};
  this.roots = new Map(); this.records = new Map(); this.resources = new Map();
 }
 register(root, target) {
  if (!TARGETS.includes(target)) throw new Error('Unknown inspection target');
  if (this.roots.has(root)) return;
  const meshes = [];
  root.traverse(mesh => { if (mesh.isMesh && !mesh.userData.inspectionOverlay) meshes.push(mesh); });
  const removed = () => this.unregister(root);
  this.roots.set(root, {meshes, removed}); root.addEventListener('removed', removed);
  for (const mesh of meshes) {
   if (this.records.has(mesh)) continue;
   const record = {mesh, target, original: mesh.material, overlay: null, resources: []};
   this.records.set(mesh, record); if (!this.bounded) this.apply(record); this.dirty = true;
  }
 }
 unregister(root) {
  const entry = this.roots.get(root); if (!entry) return;
  root.removeEventListener('removed', entry.removed);
  for (const mesh of entry.meshes) {
   const record = this.records.get(mesh); if (!record) continue;
   this.release(record); this.records.delete(mesh);
  }
  this.roots.delete(root); this.dirty = true;
 }
 acquire(original, target) {
  let byTarget = this.resources.get(original);
  if (!byTarget) this.resources.set(original, byTarget = new Map());
  let resource = byTarget.get(target);
  if (!resource) {
   const skin = original.clone();
   // Material.clone does not preserve shader callbacks. Keep the live city-clock
   // uniforms and source textures; only the inspection render state changes.
   skin.onBeforeCompile = this.bounded ? shader => { original.onBeforeCompile(shader); inspectionShader(shader, this.regionUniforms); } : original.onBeforeCompile;
   skin.customProgramCacheKey = () => original.customProgramCacheKey() + (this.bounded ? '-inspection-region-v1' : '');
   const depth = new THREE.MeshBasicMaterial({colorWrite: false, depthWrite: true, side: original.side, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1});
   depth.visible = original.visible; depth.shadowSide = original.shadowSide; depth.alphaTest = original.alphaTest;
   if (original.alphaTest) { depth.map = original.map; depth.alphaMap = original.alphaMap; }
   const wire = new THREE.MeshBasicMaterial({color: this.colour(target), wireframe: true, side: original.side, toneMapped: false, depthWrite: false});
   wire.visible = original.visible; wire.depthTest = true;
   if (this.bounded) { wire.onBeforeCompile = shader => inspectionShader(shader, this.regionUniforms, {wire: true}); wire.customProgramCacheKey = () => 'inspection-region-wire-v1'; }
   resource = {original, target, skin, depth, wire, references: 0}; byTarget.set(target, resource);
  }
  resource.references++; return resource;
 }
 updateMaterial(resource) {
  const {original, skin, wire} = resource, alpha = this.mode === 'wireframe' ? 0 : this.opacity / 100;
  const transparent = original.transparent || alpha < 1;
  if (skin.transparent !== transparent) { skin.transparent = transparent; skin.needsUpdate = true; }
  skin.opacity = original.opacity * (this.bounded ? 1 : alpha);
  skin.colorWrite = original.colorWrite && (this.bounded || alpha > 0);
  // Keep hidden triangles occluded. Revealing colour never turns the city into
  // a stack of blended back faces; depth-only skins avoid invisible facade work.
  skin.depthWrite = original.depthWrite;
  const wireTransparent = (this.bounded || alpha > 0) && transparent;
  if (wire.transparent !== wireTransparent) { wire.transparent = wireTransparent; wire.needsUpdate = true; }
  skin.polygonOffset = true; skin.polygonOffsetFactor = 1; skin.polygonOffsetUnits = 1;
 }
 apply(record) {
  const {mesh, target, original} = record;
  if (this.mode === 'solid' || !this.targets[target] || this.bounded && !record.candidates?.length) { this.release(record); return; }
  if (!record.overlay) {
   record.resources = (Array.isArray(original) ? original : [original]).map(material => this.acquire(material, target));
   const wire = record.resources.map(resource => resource.wire), material = Array.isArray(original) ? wire : wire[0];
   let overlay;
   if (this.bounded) overlay = regionWireMesh(record, record.candidates, material);
   else if (mesh.isInstancedMesh) {
    overlay = new THREE.InstancedMesh(mesh.geometry, material, mesh.count);
    overlay.instanceMatrix.copy(mesh.instanceMatrix); overlay.count = mesh.count;
    overlay.boundingBox = mesh.boundingBox?.clone() || null; overlay.boundingSphere = mesh.boundingSphere?.clone() || null;
   } else overlay = new THREE.Mesh(mesh.geometry, material);
   overlay.name = 'Rendered triangles · ' + mesh.name;
   overlay.userData.inspectionOverlay = true; overlay.userData.inspectionSourceGeometry = mesh.geometry; overlay.raycast = NO_PICK;
   overlay.castShadow = false; overlay.receiveShadow = false;
   overlay.frustumCulled = mesh.frustumCulled; overlay.renderOrder = mesh.renderOrder + 1;
   mesh.add(overlay); record.overlay = overlay;
  }
  for (const resource of record.resources) this.updateMaterial(resource);
  const depthOnly = !this.bounded && (this.mode === 'wireframe' || this.opacity === 0);
  const skins = record.resources.map(resource => depthOnly ? resource.depth : resource.skin);
  mesh.material = Array.isArray(original) ? skins : skins[0];
 }
 release(record) {
  if (!record.overlay) return;
  record.mesh.material = record.original;
  record.overlay.removeFromParent();
  // Geometry and source textures are borrowed. Only derived materials and the
  // overlay's own instance buffer are owned by inspection.
  if (record.overlay.isInstancedMesh) record.overlay.dispose();
  if (record.overlay.userData.inspectionOwnedGeometry) record.overlay.geometry.dispose();
  record.overlay = null;
  for (const resource of record.resources) {
   if (--resource.references) continue;
   resource.skin.dispose(); resource.depth.dispose(); resource.wire.dispose();
   const byTarget = this.resources.get(resource.original); byTarget.delete(resource.target);
   if (!byTarget.size) this.resources.delete(resource.original);
  }
  record.resources = [];
 }
 colour(target) { return this.night ? (target === 'terrain' ? '#75c7b8' : '#dabf89') : (target === 'terrain' ? '#214d46' : '#50432c'); }
 setNight(value) {
  const night = Boolean(value); if (night === this.night) return; this.night = night;
  for (const byTarget of this.resources.values()) for (const resource of byTarget.values()) resource.wire.color.set(this.colour(resource.target));
 }
 plan(focus = this.focus, {force = false} = {}) {
  if (!this.bounded) return;
  if (this.mode === 'solid') { this.focus = {x: focus.x, z: focus.z}; return; }
  for (const record of this.records.values()) { const visible = inspectionVisible(record.mesh); if (visible !== record.regionVisible) this.dirty = true; record.regionVisible = visible; }
  if (!force && !this.dirty && Math.hypot(focus.x - this.focus.x, focus.z - this.focus.z) < Math.max(25, this.region.radius * .2)) return;
  this.focus = {x: focus.x, z: focus.z};
  const region = selectInspectionRegion([...this.records.values()].filter(record => this.targets[record.target]), this.focus, this.profile);
  this.region = {radius: region.radius, triangles: region.triangles};
  this.regionUniforms.focus.value.set(this.focus.x, this.focus.z); this.regionUniforms.radius.value = region.radius;
  for (const record of this.records.values()) { this.release(record); record.candidates = region.selected.get(record); this.apply(record); }
  this.dirty = false; this.onScopeChange?.();
 }
 set({mode = this.mode, opacity = this.opacity, targets = this.targets} = {}) {
  if (!MODES.has(mode) || !Number.isFinite(opacity) || opacity < 0 || opacity > 100) throw new Error('Invalid inspection settings');
  for (const key of TARGETS) if (typeof targets[key] !== 'boolean') throw new Error('Invalid inspection target');
  const changedScope = this.mode === 'solid' || TARGETS.some(key => targets[key] !== this.targets[key]);
  this.mode = mode; this.opacity = opacity; this.targets = {...targets};
  this.regionUniforms.opacity.value = mode === 'wireframe' ? 0 : opacity / 100;
  if (this.bounded && mode !== 'solid' && changedScope) { this.plan(this.focus, {force: true}); return; }
  for (const record of this.records.values()) { this.apply(record); if (mode === 'solid') record.candidates = null; }
  if (mode === 'solid') this.region = {radius: 0, triangles: 0};
 }
 get state() {
  const counts = {terrain: 0, structures: 0}; let overlays = 0;
  for (const record of this.records.values()) { counts[record.target]++; if (record.overlay) overlays++; }
  return {mode: this.mode, night: this.night, opacity: this.opacity, targets: {...this.targets}, meshes: counts, overlays, scope: this.bounded ? {radius: Math.round(this.region.radius), triangles: this.region.triangles, budget: this.profile.triangles, maxRadius: this.profile.radius, focus: {...this.focus}} : null, materialPairs: [...this.resources.values()].reduce((sum, entries) => sum + entries.size, 0)};
 }
 dispose() { for (const root of [...this.roots.keys()]) this.unregister(root); }
}

export function bindMeshInspection(inspection, doc = document) {
 const get = id => doc.getElementById(id), modes = [...doc.querySelectorAll('input[name="mesh-mode"]')];
 const opacity = get('mesh-opacity'), terrain = get('mesh-terrain'), structures = get('mesh-structures');
 const update = () => {
  inspection.set({mode: modes.find(input => input.checked).value, opacity: Number(opacity.value), targets: {terrain: terrain.checked, structures: structures.checked}});
  const {mode, targets} = inspection.state;
  opacity.disabled = mode !== 'overlay' || !targets.terrain && !targets.structures;
  get('mesh-opacity-value').textContent = opacity.value + '%';
  get('mesh-status').textContent = mode === 'solid' ? 'Inspection off · original materials.' : !targets.terrain && !targets.structures ? 'Choose Terrain or Structures to inspect.' : mode === 'wireframe' ? 'Triangle wires only on selected layers.' : 'Triangle wires over the selected skins.';
 };
 for (const input of [...modes, terrain, structures]) input.addEventListener('change', update);
 opacity.addEventListener('input', update);
 const scope = () => { const state = inspection.state.scope; if (get('mesh-scope-status') && state) get('mesh-scope-status').textContent = inspection.mode === 'solid' ? 'Inspection focuses on the view centre, with a bounded triangle budget.' : state.radius ? `View centre · ${state.radius} m radius · ${state.triangles.toLocaleString()} / ${state.budget.toLocaleString()} triangles. Outside this circle stays solid. Zoom or move to inspect another area.` : 'No visible triangles fit here. Move the view centre onto terrain or a structure.'; };
 inspection.onScopeChange = scope; for (const input of modes) input.addEventListener('change', scope); update(); scope();
}

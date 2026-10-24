import * as THREE from '../vendor/three.module.js';

export const INSPECTION_PROFILES = {desktop: {radius: 700, triangles: 18000}, mobile: {radius: 350, triangles: 7000}};
const distanceToBox = (x, z, minX, minZ, maxX, maxZ) => Math.max(minX - x, 0, x - maxX) ** 2 + Math.max(minZ - z, 0, z - maxZ) ** 2;
export const inspectionVisible = mesh => { for (let node = mesh; node; node = node.parent) if (!node.visible) return false; return true; };
function ranges(mesh) {
 const geometry = mesh.geometry, count = geometry.index?.count ?? geometry.attributes.position.count;
 const start = geometry.drawRange.start, end = Math.min(count, start + geometry.drawRange.count);
 return (Array.isArray(mesh.material) ? geometry.groups : [{start: 0, count, materialIndex: 0}]).map(group => ({start: Math.max(start, group.start), end: Math.min(end, group.start + group.count), materialIndex: group.materialIndex}));
}
/** Scan only source roots whose spatial bounds reach the focus. Keep complete,
 * real triangles whose XZ bounds intersect the circle; the shader clips its edge.
 * The radius shrinks before any geometry is built, so no faces inside it are lost.
 */
export function selectInspectionRegion(records, focus, profile) {
 const candidates = [], limit = profile.radius ** 2, worldBox = new THREE.Box3(), point = new THREE.Vector3(), instance = new THREE.Matrix4(), matrix = new THREE.Matrix4();
 for (const record of records) {
  const mesh = record.mesh, geometry = mesh.geometry;
  if (!inspectionVisible(mesh) || !geometry.attributes.position) continue;
  mesh.updateWorldMatrix(true, false);
  if (mesh.isInstancedMesh) { if (!mesh.boundingBox) mesh.computeBoundingBox(); worldBox.copy(mesh.boundingBox).applyMatrix4(mesh.matrixWorld); }
  else { if (!geometry.boundingBox) geometry.computeBoundingBox(); worldBox.copy(geometry.boundingBox).applyMatrix4(mesh.matrixWorld); }
  if (distanceToBox(focus.x, focus.z, worldBox.min.x, worldBox.min.z, worldBox.max.x, worldBox.max.z) > limit) continue;
  const groups = ranges(mesh), position = geometry.attributes.position, index = geometry.index;
  if (mesh.isInstancedMesh) {
   if (!geometry.boundingBox) geometry.computeBoundingBox();
   const weight = groups.reduce((sum, group) => sum + (group.end - group.start) / 3, 0);
   for (let i = 0; i < mesh.count; i++) {
    mesh.getMatrixAt(i, instance); matrix.multiplyMatrices(mesh.matrixWorld, instance);
    worldBox.copy(geometry.boundingBox).applyMatrix4(matrix);
    const distance = distanceToBox(focus.x, focus.z, worldBox.min.x, worldBox.min.z, worldBox.max.x, worldBox.max.z);
    if (distance <= limit) candidates.push({record, instance: i, distance, weight});
   }
   continue;
  }
  for (const group of groups) for (let offset = group.start; offset + 2 < group.end; offset += 3) {
   let minX = Infinity, minZ = Infinity, maxX = -Infinity, maxZ = -Infinity;
   for (let j = 0; j < 3; j++) {
    point.fromBufferAttribute(position, index ? index.getX(offset + j) : offset + j).applyMatrix4(mesh.matrixWorld);
    minX = Math.min(minX, point.x); minZ = Math.min(minZ, point.z); maxX = Math.max(maxX, point.x); maxZ = Math.max(maxZ, point.z);
   }
   const distance = distanceToBox(focus.x, focus.z, minX, minZ, maxX, maxZ);
   if (distance <= limit) candidates.push({record, offset, group: group.materialIndex, distance, weight: 1});
  }
 }
 candidates.sort((a, b) => a.distance - b.distance);
 let triangles = 0, radius = profile.radius;
 for (const candidate of candidates) {
  if (triangles + candidate.weight > profile.triangles) { radius = Math.max(0, Math.sqrt(candidate.distance) - .01); break; }
  triangles += candidate.weight;
 }
 const selected = new Map(); triangles = 0;
 for (const candidate of candidates) {
  if (!radius || candidate.distance > radius * radius) continue;
  if (!selected.has(candidate.record)) selected.set(candidate.record, []);
  selected.get(candidate.record).push(candidate); triangles += candidate.weight;
 }
 return {radius, triangles, selected};
}

export function regionWireMesh(record, candidates, material) {
 const source = record.mesh;
 if (source.isInstancedMesh) {
  const overlay = new THREE.InstancedMesh(source.geometry, material, candidates.length), matrix = new THREE.Matrix4();
  for (let i = 0; i < candidates.length; i++) { source.getMatrixAt(candidates[i].instance, matrix); overlay.setMatrixAt(i, matrix); }
  overlay.computeBoundingBox(); overlay.computeBoundingSphere(); overlay.userData.inspectionInstances = candidates.map(c => c.instance); return overlay;
 }
 const sourceGeometry = source.geometry, position = sourceGeometry.attributes.position, sourceIndex = sourceGeometry.index;
 const vertices = [], indices = [], sourceVertices = [], sourceOffsets = [], remap = new Map(), geometry = new THREE.BufferGeometry();
 // Group order remains source order, even though selection was ranked by distance.
 candidates.sort((a, b) => a.group - b.group || a.offset - b.offset);
 let group = null, groupStart = 0;
 for (const candidate of candidates) {
  if (candidate.group !== group) { if (group !== null) geometry.addGroup(groupStart, indices.length - groupStart, group); group = candidate.group; groupStart = indices.length; }
  sourceOffsets.push(candidate.offset);
  for (let j = 0; j < 3; j++) {
   const original = sourceIndex ? sourceIndex.getX(candidate.offset + j) : candidate.offset + j;
   if (!remap.has(original)) { remap.set(original, remap.size); vertices.push(position.getX(original), position.getY(original), position.getZ(original)); sourceVertices.push(original); }
   indices.push(remap.get(original));
  }
 }
 if (group !== null) geometry.addGroup(groupStart, indices.length - groupStart, group);
 geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3)); geometry.setIndex(indices);
 geometry.computeBoundingBox(); geometry.computeBoundingSphere();
 geometry.userData.inspectionSourceVertices = new Uint32Array(sourceVertices); geometry.userData.inspectionSourceOffsets = new Uint32Array(sourceOffsets);
 const overlay = new THREE.Mesh(geometry, material); overlay.userData.inspectionOwnedGeometry = true; return overlay;
}

export function inspectionShader(shader, uniforms, {wire = false} = {}) {
 Object.assign(shader.uniforms, {uInspectionFocus: uniforms.focus, uInspectionRadius: uniforms.radius, uInspectionOpacity: uniforms.opacity});
 shader.vertexShader = shader.vertexShader.replace('#include <common>', '#include <common>\nvarying vec2 vInspectionXZ;').replace('#include <project_vertex>', `#include <project_vertex>
  vec4 inspectionPosition = vec4(transformed, 1.0);
  #ifdef USE_INSTANCING
   inspectionPosition = instanceMatrix * inspectionPosition;
  #endif
  vInspectionXZ = (modelMatrix * inspectionPosition).xz;`);
 shader.fragmentShader = shader.fragmentShader.replace('#include <common>', '#include <common>\nvarying vec2 vInspectionXZ; uniform vec2 uInspectionFocus; uniform float uInspectionRadius; uniform float uInspectionOpacity;');
 if (wire) shader.fragmentShader = shader.fragmentShader.replace('void main() {', 'void main() {\nif (distance(vInspectionXZ, uInspectionFocus) > uInspectionRadius) discard;');
 else {
  shader.fragmentShader = shader.fragmentShader.replace('#include <logdepthbuf_fragment>', '#include <logdepthbuf_fragment>\nif (uInspectionOpacity == 0.0 && distance(vInspectionXZ, uInspectionFocus) <= uInspectionRadius) { gl_FragColor = vec4(0.0); return; }');
  shader.fragmentShader = shader.fragmentShader.replace('#include <opaque_fragment>', '#include <opaque_fragment>\nif (distance(vInspectionXZ, uInspectionFocus) <= uInspectionRadius) gl_FragColor.a *= uInspectionOpacity;');
 }
}

/** Check four installed Beverly Hill towers against its exact original government podium triangles. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync, writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel, disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {nearest} from '../assembly-support-review/triangles.mjs';

const root = new URL('../../../', import.meta.url);
const read = path => JSON.parse(readFileSync(new URL(path, root)));
const support = 'source-scripts/city/government-import/local/government-xl-beverly-hill-podium-20260927/source/packed/';
const wanted = new Set(['landsd/255544:0','landsd/255939:0','landsd/256136:0','landsd/256138:0']);
const sources = [];
for (const url of read('3d-viewer/city/data/manifest.json').officialModelCatalogues) {
 for (const entry of read('3d-viewer/' + url).models) if (wanted.has(entry.uid))
  sources.push({entry, base: '3d-viewer/' + url.slice(0, url.lastIndexOf('/') + 1)});
}
assert.equal(sources.length, wanted.size);
const supportEntry = JSON.parse(gunzipSync(readFileSync(new URL('source-scripts/city/government-import/local/government-xl-beverly-hill-podium-20260927/support-runtime.json.gz', root)))).rows[0].candidate.entry;
const forms = new Map();
for (const tile of read('3d-viewer/city/data/manifest.json').tiles) {
  if (tile.url !== 'city/data/tiles/1_0.json') continue;
  for (const building of read('3d-viewer/' + tile.url).buildings) forms.set(building.uid, building);
}
const lighting = {night: {value: 0}, activity: {value: new THREE.Vector4(1, 1, 1, 1)}, retail: {value: 1}, elapsed: {value: 0}, shimmer: {value: 0}};
async function load(entry, base) {
  const bytes = readFileSync(new URL(base + entry.asset, root));
  assert.equal(createHash("sha256").update(bytes).digest("hex"), entry.sha256);
  const model = await loadOfficialModel({...entry, assetURL: 'https://probe.invalid/model.glb.gz'}, forms.get(entry.uid), lighting, {fetcher: async () => new Response(bytes)});
  const {position, index} = model.record.modelGeometry;
  const faces = [];
  for (let i = 0; i < index.length; i += 3) {
    const face = new THREE.Triangle(...[index[i], index[i + 1], index[i + 2]].map(j => new THREE.Vector3().fromArray(position, j * 3)));
    if (face.getArea() > 1e-12) faces.push(face);
  }
  return {model, position, index, faces, entry};
}
const podium = await load(supportEntry, support);
const results = [];
for (const {entry, base} of sources) {
const tower = await load(entry, base);
const lower = new Map();
for (let i = 0; i < tower.position.length; i += 3) {
  const point = Array.from(tower.position.slice(i, i + 3));
  if (point[1] > tower.entry.worldBounds[0][1] + .35) continue;
  lower.set(point.map(n => n.toFixed(3)).join(','), point);
}
const measures = [...lower.values()].map(point => ({point, distance: nearest(podium, new THREE.Vector3(...point))}));
const distances = measures.map(m => m.distance).sort((a, b) => a - b);
const result = {uid: tower.entry.uid, supportUid: podium.entry.uid,
  sourceSHA256: tower.entry.sha256, supportSHA256: podium.entry.sha256,
  sourceYRange: [tower.entry.worldBounds[0][1], tower.entry.worldBounds[1][1]],
  supportYRange: [podium.entry.worldBounds[0][1], podium.entry.worldBounds[1][1]],
  interfaceSamples: measures.length, within05: distances.filter(d => d <= .5).length,
  within1: distances.filter(d => d <= 1).length, within2: distances.filter(d => d <= 2).length,
  minimumDistance: distances[0], medianDistance: distances[Math.floor(distances.length / 2)],
  maximumDistance: distances.at(-1), contactPositions: measures.filter(m => m.distance <= .5).map(m => m.point),
  aiCalls: 0, modelGeometryChanges: 0};
results.push(result);
disposeOfficialModel(tower.model);
console.log(JSON.stringify({...result, contactPositions: result.contactPositions.length}));
}
disposeOfficialModel(podium.model);
writeFileSync(new URL('docs/astra-city/government-import/government-xl-remaining-20260923/beverly-hill-neighbour-support-probe-20260928.json', root), JSON.stringify({rows: results, aiCalls: 0, modelGeometryChanges: 0, publication: false}) + '\n');

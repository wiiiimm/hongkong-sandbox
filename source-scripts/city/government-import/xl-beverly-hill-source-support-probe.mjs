/** Check Beverly Hill Block A against its exact original government podium triangles. */
import {readFileSync, writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel, disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {nearest} from '../assembly-support-review/triangles.mjs';

const root = new URL('../../../', import.meta.url);
const read = path => JSON.parse(readFileSync(new URL(path, root)));
const source = 'source-scripts/city/government-import/local/government-xl-beverly-hill-block-a-terrain-20260927/candidates/';
const support = 'source-scripts/city/government-import/local/government-xl-beverly-hill-podium-20260927/source/packed/';
const sourceEntry = read(source + 'catalogue.json').models[0];
const supportEntry = JSON.parse(gunzipSync(readFileSync(new URL('source-scripts/city/government-import/local/government-xl-beverly-hill-podium-20260927/support-runtime.json.gz', root)))).rows[0].candidate.entry;
const forms = new Map();
for (const tile of read('3d-viewer/city/data/manifest.json').tiles) {
  if (tile.url !== 'city/data/tiles/1_0.json') continue;
  for (const building of read('3d-viewer/' + tile.url).buildings) forms.set(building.uid, building);
}
const lighting = {night: {value: 0}, activity: {value: new THREE.Vector4(1, 1, 1, 1)}, retail: {value: 1}, elapsed: {value: 0}, shimmer: {value: 0}};
async function load(entry, base) {
  const bytes = readFileSync(new URL(base + entry.asset, root));
  const model = await loadOfficialModel({...entry, assetURL: 'https://probe.invalid/model.glb.gz'}, forms.get(entry.uid), lighting, {fetcher: async () => new Response(bytes)});
  const {position, index} = model.record.modelGeometry;
  const faces = [];
  for (let i = 0; i < index.length; i += 3) {
    const face = new THREE.Triangle(...[index[i], index[i + 1], index[i + 2]].map(j => new THREE.Vector3().fromArray(position, j * 3)));
    if (face.getArea() > 1e-12) faces.push(face);
  }
  return {model, position, index, faces, entry};
}
const tower = await load(sourceEntry, source);
const podium = await load(supportEntry, support);
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
const out = new URL('docs/astra-city/government-import/government-xl-remaining-20260923/beverly-hill-source-support-probe-20260927.json', root);
writeFileSync(out, JSON.stringify(result) + '\n');
disposeOfficialModel(tower.model);
disposeOfficialModel(podium.model);
console.log(JSON.stringify({...result, contactPositions: result.contactPositions.length}));

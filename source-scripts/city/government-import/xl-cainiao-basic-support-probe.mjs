/** Measure the original Cainiao lower mesh against its retained basic podium. */
import { readFileSync, writeFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import { loadOfficialModel, disposeOfficialModel } from '../../../3d-viewer/city/official-model-assets.js';

const root = new URL('../../../', import.meta.url);
const read = path => JSON.parse(readFileSync(new URL(path, root)));
const base = 'source-scripts/city/government-import/local/government-xl-cainiao-smart-gateway-terrain-20260927/candidates/';
const entry = read(base + 'catalogue.json').models[0];
const manifest = read('3d-viewer/city/data/manifest.json');
const forms = new Map();
for (const tile of manifest.tiles) {
  for (const building of read('3d-viewer/' + tile.url).buildings) forms.set(building.uid, building);
}
const podium = forms.get('landsd/327178:0');
const tower = forms.get(entry.uid);
if (!podium || !tower || podium.structureType !== 'Podium' || podium.parent !== tower.parent) throw new Error('Podium identity mismatch');
const compressed = readFileSync(new URL(base + entry.asset, root));
const lighting = { night: {value: 0}, activity: {value: new THREE.Vector4(1, 1, 1, 1)}, retail: {value: 1}, elapsed: {value: 0}, shimmer: {value: 0} };
const loaded = await loadOfficialModel({...entry, assetURL: 'https://probe.invalid/model.glb.gz'}, tower, lighting, {fetcher: async () => new Response(compressed)});
const {position, index} = loaded.record.modelGeometry;
const roof = podium.base + podium.height;
const samples = new Map();
for (let i = 0; i < position.length; i += 3) {
  const point = Array.from(position.slice(i, i + 3));
  if (point[1] > roof + 0.5) continue;
  samples.set(point.map(n => n.toFixed(3)).join(','), point);
}
const report = {uid: entry.uid, supportUid: podium.uid, sourceSHA256: entry.sha256,
  sourceVertices: position.length / 3, sourceTriangles: index.length / 3,
  supportRoofM: roof, sourceBottomM: entry.worldBounds[0][1],
  lowerVertices: [...samples.values()], aiCalls: 0, modelGeometryChanges: 0};
const out = new URL('docs/astra-city/government-import/government-xl-remaining-20260923/cainiao-basic-support-probe-20260927.json', root);
writeFileSync(out, JSON.stringify(report) + '\n');
disposeOfficialModel(loaded);
console.log(JSON.stringify({lowerVertices: report.lowerVertices.length, roof, sourceBottomM: report.sourceBottomM}));

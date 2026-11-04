/** Measure unchanged current BASIC meshes on all supplied original support worlds. */
import assert from 'node:assert/strict';
import {readFileSync, writeFileSync, existsSync} from 'node:fs';
import {gunzipSync, gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {createBuildingGeometry} from '../../../3d-viewer/city/building-geometry.js';
import {verifySupportInterface} from './support-interface.mjs';
import {snapshotModuleClosure, verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root = new URL('../../../', import.meta.url), doc = process.argv[2], hashes = {};
const sha = raw => createHash('sha256').update(raw).digest('hex');
assert(doc?.startsWith('docs/astra-city/government-import/government-xl-') && !doc.includes('..'));
function read(path) {
  const raw = readFileSync(new URL(path, root)); hashes[path] = sha(raw);
  return JSON.parse(path.endsWith('.gz') ? gunzipSync(raw) : raw);
}
const input = read(doc + '/input.json.gz');
assert(!existsSync(new URL(doc + '/checks.json.gz', root)));
for (const ref of input.evidenceRefs) assert.equal(sha(readFileSync(new URL(ref.path, root))), ref.sha256);
const manifest = read('3d-viewer/city/data/manifest.json');
assert.equal(hashes['3d-viewer/city/data/manifest.json'], input.currentManifestSHA256);
const installed = new Set(manifest.officialModelCatalogues.flatMap(url => read('3d-viewer/' + url).models.map(row => row.uid)));
const closures = ['3d-viewer/city/building-geometry.js', 'source-scripts/city/government-import/support-interface.mjs'].map(path => snapshotModuleClosure(new URL(path, root), root));
for (const closure of closures) Object.assign(hashes, closure.inputHashes);
assert.deepEqual(input.supportModes.map(mode => mode.name).sort(), ['balancedF32', 'leftF32', 'literal', 'original']);
assert.equal(new Set(input.forms.map(b => b.uid)).size, input.forms.length);
const bodies = [], rows = [];
for (const b of input.forms) {
  assert(!installed.has(b.uid));
  const tile = manifest.tiles.find(tile => tile.id === b.tile); assert(tile);
  assert.deepEqual(read('3d-viewer/' + tile.url).buildings.filter(form => form.uid === b.uid), [b]);
  const geometry = createBuildingGeometry(b);
  try {
    const body = {position: Array.from(geometry.attributes.position.array), index: geometry.index ? Array.from(geometry.index.array) : Array.from({length: geometry.attributes.position.count}, (_, index) => index)};
    assert(body.position.every(Number.isFinite));
    bodies.push({uid: b.uid, building: b, ...body});
    for (const mode of input.supportModes) {
      const proof = verifySupportInterface(body, b.base + (b.minimum || 0), mode.geometry);
      rows.push({uid: b.uid, supportUid: input.supportUid, mode: mode.name, proof});
      console.log(JSON.stringify({uid: b.uid, mode: mode.name, samples: proof.samples, strict: proof.strictContacts, unresolved: proof.unresolved.length, passed: proof.passed}));
    }
  } finally { geometry.dispose(); }
}
for (const closure of closures) assert(verifyModuleClosure(closure, root));
hashes['source-scripts/city/government-import/current_basic_on_original_support_diagnostic_v1_20261104.mjs'] = sha(readFileSync(new URL('source-scripts/city/government-import/current_basic_on_original_support_diagnostic_v1_20261104.mjs', root)));
for (const [path, pinned] of Object.entries(hashes)) assert.equal(sha(readFileSync(new URL(path, root))), pinned);
writeFileSync(new URL(doc + '/checks.json.gz', root), gzipSync(JSON.stringify({rows, bodies, inputHashes: hashes, originalGeometryChanges: 0, basicGeometryChanges: 0, installationApproved: false})));

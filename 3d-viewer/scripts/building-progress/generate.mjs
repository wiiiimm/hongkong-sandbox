/** Credential-free static statistics and screening input builder. */
import {readFileSync, writeFileSync, existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {gzipSync, gunzipSync} from 'node:zlib';
import {resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {countCoverage} from './counts.mjs';
import {SCREENING_POLICY, digest, screeningFingerprint, validScreening} from './screening.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const inputs = {}, hash = b => createHash('sha256').update(b).digest('hex');
const read = p => { const b = readFileSync(resolve(root, p)); inputs[p] = hash(b); return JSON.parse(b); };
const manifest = read('city/data/manifest.json');
const snapshot = read('scripts/building-progress/review-proof.json');
const screening = read('scripts/building-progress/screening-proof.json');
const governmentPath='scripts/building-progress/government-source-proof.json.gz';
const governmentBytes=readFileSync(resolve(root,governmentPath));inputs[governmentPath]=hash(governmentBytes);
const governmentProof=JSON.parse(gunzipSync(governmentBytes));
if(governmentProof.version!==1||!Array.isArray(governmentProof.rows)||!governmentProof.rows.length||!Number.isFinite(Date.parse(governmentProof.capturedAt))||!/^[a-f0-9]{64}$/.test(governmentProof.runId))throw Error('Unsupported government source proof');
if (screening.version !== 1 || screening.policy !== SCREENING_POLICY || !Array.isArray(screening.rows)) throw Error('Unsupported screening proof');
const native = new Map(), models = [], forms = [], suppressed = [];
for (const url of manifest.officialModelCatalogues || []) {
  const catalogue = read(url);
  for (const model of catalogue.models) {
    const asset = resolve(root, dirname(url), model.asset);
    if (!existsSync(asset) || hash(readFileSync(asset)) !== model.sha256) throw Error('Deployed native asset unavailable/hash mismatch: ' + model.uid);
    if (native.has(model.uid)) throw Error('Duplicate native model: ' + model.uid);
    native.set(model.uid, {...model, rootTranslation: catalogue.rootTranslation}); models.push(model);
  }
}
// Geometry, terrain and rendering changes invalidate old acceptance. Global
// terrain invalidation is deliberately conservative until local keys are wired in.
const context = {origin: manifest.origin, crs: manifest.crs, heightPolicy: manifest.heightPolicy, heightRules: manifest.heightRules};
for (const path of ['city/data/terrain.json', ...(manifest.terrainPatches || []).map(p => p.url),
  'city/building-geometry.js', 'city/world.js', 'city/tai-o-estimates.js',
  'city/streaming.js', 'city/official-models.js', 'city/official-model-assets.js',
  'city/geo.js', 'city/native-terrain.js', 'city/lighting.js']) context[path] = hash(readFileSync(resolve(root, path)));
function scan(v) {
  if (!v || typeof v !== 'object') return;
  if (Array.isArray(v.suppressesBuildingUids)) suppressed.push(...v.suppressesBuildingUids);
  for (const value of Object.values(v)) if (typeof value === 'object') scan(value);
}
for (const source of manifest.bridgeModels || []) {
  const url = typeof source === 'string' ? source : source.url;
  if (url) { scan(read(url)); context[url] = inputs[url]; }
}
const contextHash = digest(context), seen = new Set();
const embeddedProof = new Map(snapshot.embedded.map(p => [p.uid, p]));
for (const tile of manifest.tiles) {
  const activity = manifest.activityTiles ? read(`city/data/activity/${tile.id}.json`).buildings : {};
  for (const b of read(tile.url).buildings) {
    if (seen.has(b.uid)) throw Error('Duplicate source form: ' + b.uid);
    seen.add(b.uid);
    const n = native.get(b.uid);
    forms.push({uid: b.uid, buildingCSUID:b.buildingCSUID||null, inputHash: screeningFingerprint({...b, activity: activity[b.uid] || null}, n, contextHash),
      geometry: n ? 'native' : b.modelGeometry ? 'embedded' : 'footprint'});
    if (b.modelGeometry) {
      const proof = embeddedProof.get(b.uid);
      if (proof?.runtimeDigest === hash(JSON.stringify(b.modelGeometry))) models.push({uid: b.uid, sha256: proof.sourceSHA256});
    }
  }
}
const counts = countCoverage({forms, models, reviews: snapshot.rows, suppressed, screenings: screening.rows, governmentSources:governmentProof.rows});
const manifestDigest = hash(JSON.stringify(manifest));
const dates = [snapshot.capturedAt, ...screening.rows.map(r => r.reviewedAt)].filter(d => Number.isFinite(Date.parse(d)));
const output = {version: 3, status: 'available', ...counts,
  updatedAt: dates.sort((a,b) => Date.parse(b)-Date.parse(a))[0],
  reviewSnapshot: snapshot.snapshotId, screeningPolicy: SCREENING_POLICY,
  governmentSourceRun:governmentProof.runId, governmentSourceUpdatedAt:governmentProof.capturedAt,
  manifestDigest, inputDigest: digest([inputs, context]),
  source: 'Hong Kong Lands Department and retained OpenStreetMap forms',
  countingNote: 'Distinct deployed source-form IDs, not whole buildings. Government availability requires an exact current UID/CSUID match to a prepared source. Upgrade progress counts enhanced/good-to-go forms within that subset. Source availability is not placement approval or proof an upgrade is needed.',
  reviewPolicy: 'Good-to-go and enhancement-required decisions must match current geometry, terrain, renderer and screening policy. Changed or missing decisions remain unassessed. Existing verified source-hash reviews supply enhanced status unless a current screening requests rework.'};
writeFileSync(resolve(root, 'city/data/building-progress.json'), JSON.stringify(output, null, 2) + '\n');
if (process.argv[2] === '--plan') {
  if (!process.argv[3]) throw Error('--plan requires output path');
  const hidden = new Set(suppressed), byReview = new Map(snapshot.rows.map(r => [r.uid, r]));
  const verified = new Set(models.filter(m => byReview.get(m.uid)?.review_state === 'installed-verified' && byReview.get(m.uid)?.source_sha256 === m.sha256).map(m => m.uid));
  const byScreen = new Map(screening.rows.map(r => [r.uid, r]));
  const rows = forms.filter(f => !hidden.has(f.uid)).map(f => {
    const row = byScreen.get(f.uid), valid = validScreening(row, f);
    const state = valid && row.decision === 'enhancement-required' ? 'enhancement-required'
      : verified.has(f.uid) ? 'enhanced' : valid && row.decision === 'good-to-go' ? 'good-to-go' : 'unassessed';
    return {...f, state, action: ['enhanced','good-to-go'].includes(state) ? 'skip' : state === 'enhancement-required' ? 'enhance' : 'assess'};
  });
  const plan = {version: 1, policy: SCREENING_POLICY, manifestDigest, contextHash, aiCalls: 0, rows};
  writeFileSync(resolve(process.argv[3]), gzipSync(JSON.stringify(plan)));
}
console.log(JSON.stringify(counts));

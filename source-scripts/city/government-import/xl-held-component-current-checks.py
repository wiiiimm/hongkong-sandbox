"""Fresh complete identity/contact/foundation checks for newly routed originals."""
import importlib.util
import subprocess
import uuid
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, connect, reservations
from component_type_resolution import resolve
from original_source_ownership import document, graph_reasons
from government_georef_cell_identity import geographic_cell

BATCH = 'government-xl-held-component-recovery-20261008'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file); result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result); return result


def check_one(row, metric, geometry, profile):
    final = module('component_current_foundation', 'xl-final-script-pass.py')
    policy = module('component_current_policy', 'acceptance-policy.py')
    uid = row['uid']; sha = row['sourceSHA256']
    reasons = []
    if metric.get('error') or geometry is None:
        return {'uid': uid, 'sourceKey': row['sourceKey'], 'sourceSHA256': sha, 'scriptChecksPassed': False, 'reasons': ['detailed-current-check-error'], 'metric': metric}
    source = ROOT / row['candidate']['path']; raw = source.read_bytes(); assert digest(raw) == sha
    assert digest((ROOT / '3d-viewer' / row['source']['tile']).read_bytes()) == row['source']['tileSHA256']
    tri = np.asarray(geometry['position']).reshape(-1, 3)[np.asarray(geometry['index']).reshape(-1, 3)]
    assert len(tri) == row['triangles'] and np.isfinite(tri).all()
    assert np.max(np.abs(np.array([tri.min(axis=(0, 1)), tri.max(axis=(0, 1))]) - row['native']['model']['worldBounds'])) < .002
    lo, hi = tri.min(axis=(0, 1)), tri.max(axis=(0, 1))
    forms = final.load_forms([lo[0] - 2, lo[2] - 2, hi[0] + 2, hi[2] + 2])
    context = final.identity_context(row, tri, forms); footprint = Polygon(row['source']['building']['rings'][0], row['source']['building']['rings'][1:])
    projection = final.projection(tri)
    graph = graph_reasons(document(raw), row['modelId'], row['triangles']); reasons.extend(graph)
    # The earlier hull matcher failed; remeasure complete source geometry. The
    # existing full-cell identity contract and its bounds remain unchanged.
    for key, lower, upper in [('targetCoveredBySourceProjection', .95, 1.000000001), ('sourceExcessMaximumDistanceFromTargetM', 0, 10), ('sourceExcessCoveredByUnrelatedFormsM2', 0, 1)]:
        value = context[key]
        if not np.isfinite(value) or not lower <= value <= upper: reasons.append('full-source-identity-bound:' + key)
    if not context['exactObjectAndCSUID']: reasons.append('exact-current-source-identity')
    cell = geographic_cell(row['modelId'], row['source']['building']['buildingCSUID'], row['source']['building']['structureType'])
    if not footprint.covers(cell): reasons.append('current-target-does-not-cover-whole-georef-cell')
    if not projection.covers(cell): reasons.append('original-source-does-not-cover-whole-georef-cell')
    routing = resolve(row['native']['model'], [row['source']]); assert routing == row['routing']
    metric = {**metric, 'identity': {'overlap': float(projection.intersection(footprint).area / min(projection.area, footprint.area)), 'centroidDistance': float(projection.centroid.distance(footprint.centroid))}}
    identity_accepted = not reasons
    policy_row = {'state': 'runtime-validated-awaiting-acceptance', 'sourceSHA256': sha,
                  'identityProof': {'exactObjectId': True, 'exactBuildingCSUID': True, 'uniqueViewerMatch': True, 'identityAccepted': identity_accepted}}
    reasons.extend(policy.reasons(policy_row, metric, profile))
    ground = np.asarray(geometry['drawnGroundGeometry']).reshape(-1, 3, 3)
    foundation = final.foundation_context(tri, ground, footprint)
    foundation_pass = foundation['completeTerrainTriangles'] == foundation['triangles'] and not foundation['fullyBuriedUpwardTriangles'] and foundation['fullyBuriedAreaFraction'] == 0
    if not foundation_pass: reasons.append('whole-source-foundation')
    return {'uid': uid, 'sourceKey': row['sourceKey'], 'sourceSHA256': sha, 'scriptChecksPassed': not reasons,
            'reasons': sorted(set(reasons)), 'identityAccepted': identity_accepted, 'identity': context,
            'sourceGraphVerified': not graph, 'foundation': foundation, 'strictFoundationAccepted': foundation_pass, 'metric': metric,
            'neighbourTileHashes': {tile: digest((ROOT / '3d-viewer' / tile).read_bytes()) for _, _, tile in forms},
            'historicallyPublished': row['historicallyPublished'], 'modelGeometryChanges': 0, 'installationApproved': False,
            'qualification': 'Fresh complete physical checks against unchanged current rendered terrain. Passing requires remaining runtime/browser/publication gates; no new geometry, terrain or numerical exceptions.'}


def main():
    driver = module('component_receipt_writer', 'xl-held-component-recovery.py')
    frozen = read(DOC / 'selection.json.gz'); recovery = read(DOC / 'government-recovery.json')
    assert not (DOC / 'current-checks.json').exists()
    with connect() as con: assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (recovery['jobId'],)).fetchone() == ('complete', recovery)
    available = {r['uid'] for r in recovery['rows'] if r['state'] == 'exact-source-ready'}
    rows = [r for r in frozen['rows'] if r['uid'] in available]
    assert digest((ROOT / '3d-viewer/city/data/manifest.json').read_bytes()) == frozen['manifestSHA256']
    claim = reservations.claim('codex-xl-component-current-checks-' + str(uuid.uuid4()), ['building:' + r['uid'] for r in rows], ttl=3600, batch=BATCH)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        save(DOC / 'physical-selection.json.gz', {**frozen, 'rows': rows})
        catalogue = read(HERE.parent / 'kai-tak-port/staged/catalogue.json')
        catalogue.update(area=BATCH, models=[r['candidate']['entry'] for r in rows], counts={'packedModels': len(rows)})
        save(LOCAL / 'catalogue.json', catalogue); save(LOCAL / 'catalogue-index.json', {'models': len(rows), 'catalogues': ['catalogue.json']})
        save(DOC / 'terrain-candidates.json', [])
        if rows:
            rel = lambda p: str(p.relative_to(ROOT))
            subprocess.run(['node', str(HERE / 'acceptance-metrics.mjs'), '--selection', rel(DOC / 'physical-selection.json.gz'), '--candidates', rel(LOCAL), '--terrain-candidates', rel(DOC / 'terrain-candidates.json'), '--out', rel(DOC / 'current-metrics.json'), '--geometry-out', rel(LOCAL / 'current-runtime-geometry.json.gz')], cwd=ROOT, check=True)
            metrics = read(DOC / 'current-metrics.json'); geometry = {r['uid']: r for r in read(LOCAL / 'current-runtime-geometry.json.gz')['rows']}
            for path, sha in metrics['inputHashes'].items(): assert digest((ROOT / path).read_bytes()) == sha
            by_uid = {r['uid']: r for r in metrics['rows']}; outcomes = []
            with ProcessPoolExecutor(max_workers=3) as pool:
                futures = [pool.submit(check_one, r, by_uid[r['uid']], geometry.get(r['uid']), metrics['profiles']['mobile']) for r in rows]
                for future in as_completed(futures):
                    outcome = future.result(); outcomes.append(outcome)
                    assert reservations.heartbeat(lease, ttl=3600)
                    save(DOC / 'physical-checkpoint.json.gz', {'rows': outcomes, 'expected': len(rows)})
                    print({'checked': len(outcomes), 'expected': len(rows), 'uid': outcome['uid'], 'passed': outcome['scriptChecksPassed'], 'reasons': outcome['reasons']}, flush=True)
        else: outcomes = []
        assert {r['uid'] for r in outcomes} == available
        save(DOC / 'physical-results.json.gz', {'rows': outcomes})
        refs = [driver.ref(DOC / 'physical-results.json.gz'), driver.ref(Path(__file__).resolve()), driver.ref(DOC / 'government-recovery.json')]
        if rows: refs.append(driver.ref(DOC / 'current-metrics.json'))
        result = driver.persist('fresh-xl-component-complete-physical-checks-v1', {'routingJobId': frozen['routingJobId'], 'recoveryJobId': recovery['jobId'], 'evidenceRefs': refs}, {'rows': outcomes, 'checked': len(outcomes), 'passes': sum(r['scriptChecksPassed'] for r in outcomes)}, lease)
        save(DOC / 'current-checks.json', result); save(DOC / 'neon-current-checks-sync.json', {'jobId': result['jobId'], 'resultVerified': True})
        print({'checked': len(outcomes), 'passes': result['passes'], 'jobId': result['jobId']}, flush=True)
    finally: assert reservations.release(lease)


if __name__ == '__main__': main()

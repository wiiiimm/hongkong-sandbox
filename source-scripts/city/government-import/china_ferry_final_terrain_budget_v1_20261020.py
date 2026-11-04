"""Validate the final preserved terrain, retaining the failed pre-repair budget."""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint

BASE = ROOT / 'docs/astra-city/government-import'
SRC = BASE / 'government-xl-china-ferry-candidate-terrain-v3-20261020'
SCOPE = BASE / 'government-xl-china-ferry-current-scope-v1-20261020'
BATCH = 'government-xl-china-ferry-final-terrain-budget-v1-20261020'
DOC = BASE / BATCH
assert not DOC.exists()
r = read(SRC / 'result.json')
assert r['failedGuard'] == 'terrain-runtime-budget'
with connect() as db:
    db.execute('SET TRANSACTION READ ONLY')
    assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                      (r['jobId'],)).fetchone() == ('complete', r)
pins = {}
for e in r['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']] == e['sha256']
    pins[e['path']] = e['sha256']
for p, h in pins.items():
    assert digest((ROOT / p).read_bytes()) == h, p
path = HERE / 'local' / SRC.name / 'repaired-final.json'
assert str(path.relative_to(ROOT)) in pins
patch = read(path)
original_count = len(read(HERE / 'local' / SRC.name /
                         'pre-validation-terrain.json')['nativeMesh']['index']) // 3
final_count = len(patch['nativeMesh']['index']) // 3
assert final_count == 4322 < original_count == 51831
assert final_count <= 25000, 'terrain-runtime-budget'
builder = module('china_final_budget_builder', HERE / 'resolve-pass-indexed-parent-clipping.py')
parent = read(ROOT / '3d-viewer/city/data/terrain.json')
builder.validate_patch(patch, parent)
scope = read(SCOPE / 'scope.json')['rows'][0]
bounds = builder.extent(patch['coarseCells'], parent)
assert bounds == scope['baseReplacementExtent']
positions = np.asarray(patch['nativeMesh']['position']).reshape(-1, 3)
packed = np.concatenate([positions, positions.astype(np.float32).astype(float)])
lo, hi = packed.min(0), packed.max(0)
affected = [min(bounds[0], float(lo[0])), min(bounds[1], float(lo[2])),
            max(bounds[2], float(hi[0])), max(bounds[3], float(hi[2]))]
census = read(SCOPE / 'complete-bounds.json.gz')['rows']
assert len(census) == 6771
touching = sorted(a['uid'] for a in census
                  if not closed_disjoint(a['completeFourWorldBounds'], affected))
descriptor = dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()),
                  bounds=bounds, triangles=final_count, uids=['landsd/285642:0'])
save(DOC / 'terrain-candidates.json', [descriptor])
result = dict(
    uids=descriptor['uids'], prePreservationTriangles=original_count,
    finalTriangles=final_count, unchangedTriangleBudget=25000,
    patchValidationPassed=True, budgetPassed=True,
    reason='Constructor checks its pre-preservation local triangle list; this checkpoint validates the exact final mesh count without increasing the limit.',
    fullPackedAffectedExtent=affected, touchingInstalledUids=touching,
    allCurrentActorsNominated=6771, neighbourAcceptance=False,
    sourcePhysicalAcceptance=False, installationApproved=False)
save(DOC / 'summary.json', result)
refs = [Path(__file__), SRC / 'result.json', HERE / 'resolve-pass-indexed-parent-clipping.py',
        HERE / 'heritage_saved_native_bounds_binding_v1_20261014.py',
        *[ROOT / p for p in pins]]
module('china_final_budget_freeze',
       HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
           BATCH, 'validate-actual-final-terrain-budget-and-packed-domain', refs, result)
print(result, flush=True)

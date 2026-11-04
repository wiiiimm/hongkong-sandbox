"""Check ordinary forms and complete installed native neighbours; no exclusions."""
from pathlib import Path
import subprocess
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
SRC = BASE / 'government-xl-china-ferry-final-terrain-budget-v1-20261020'
BATCH = 'government-xl-china-ferry-current-neighbours-v1-20261020'
DOC = BASE / BATCH
assert not DOC.exists()
receipt = read(SRC / 'result.json')
with connect() as db:
    db.execute('SET TRANSACTION READ ONLY')
    assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                      (receipt['jobId'],)).fetchone() == ('complete', receipt)
pins = {}
for e in receipt['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']] == e['sha256']
    pins[e['path']] = e['sha256']
for p, h in pins.items():
    assert digest((ROOT / p).read_bytes()) == h, p
candidates = read(SRC / 'terrain-candidates.json')
assert len(candidates) == 1
bounds = receipt['fullPackedAffectedExtent']
final = module('china_neighbour_forms', HERE / 'xl-final-script-pass.py')
forms = final.load_forms(bounds)
manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
installed = {e['uid'] for url in manifest['officialModelCatalogues']
             for e in read(ROOT / '3d-viewer' / url)['models']}
rows = [dict(building=b, patchIndexes=[0],
             existingNative=b['uid'] in installed or bool(b.get('modelGeometry')))
        for b, _, tile in forms]
assert set(receipt['touchingInstalledUids']) <= {r['building']['uid'] for r in rows}
form_hashes = {str((ROOT / '3d-viewer' / tile).relative_to(ROOT)):
               digest((ROOT / '3d-viewer' / tile).read_bytes())
               for b, _, tile in forms}
save(DOC / 'neighbour-inputs.json.gz', dict(
    rows=rows, inputHashes=form_hashes, patches=candidates,
    candidateIds=['landsd/285642:0'],
    requiredNativeUids=receipt['touchingInstalledUids']))
refs = [Path(__file__), SRC / 'result.json', HERE / 'xl-final-script-pass.py',
        *[ROOT / p for p in pins], *[ROOT / p for p in form_hashes]]
for name in ['check-neighbours-multi-retained.mjs',
             'check-native-neighbours-multi-retained-scoped-v3.mjs']:
    tool = HERE / name
    subprocess.run(['node', str(tool), str(DOC.relative_to(ROOT)) + '/'],
                   cwd=ROOT, check=True)
    refs.append(tool)
reports = {}
for path in DOC.glob('*checks.json'):
    report = read(path)
    reports[path.name] = report
    for p, h in report.get('inputHashes', {}).items():
        assert digest((ROOT / p).read_bytes()) == h, p
        refs.append(ROOT / p)
for p, h in pins.items():
    assert digest((ROOT / p).read_bytes()) == h, p
ordinary = read(DOC / 'neighbour-checks.json')
failures = [r for r in ordinary['rows'] if r['reasons']]
result = dict(uids=['landsd/285642:0'], forms=len(rows),
              ordinaryFlags=failures, requiredNativeUids=receipt['touchingInstalledUids'],
              reportFiles=sorted(reports), installationApproved=False,
              nextStep='Reconcile native check outcomes with ordinary flags; retain all actual regressions.')
save(DOC / 'summary.json', result)
module('china_neighbours_freeze',
       HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
           BATCH, 'complete-current-domain-ordinary-and-native-neighbours',
           list(dict.fromkeys(refs)), result)
print(result, flush=True)

"""Bind the private floor trial to complete current production grid/native parents."""
import sys
import uuid
import subprocess
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v3_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-lippo-rendered-floor-parent-lookup-v1-20261103'
TRIAL = 'government-xl-silvercord-lippo-private-source-floor-trial-v1-20261103'
LOCAL = HERE / 'local' / BATCH
UIDS = ['landsd/233997:0', 'landsd/231645:0']


def owned():
    lease = read(LOCAL / 'reservation.json'); assert reservations.owns(lease)
    _, pins = authenticate(BASE / TRIAL); refs = [Path(__file__), BASE / TRIAL / 'result.json']
    paths = [BASE / TRIAL / '231645-0' / name for name in ['private-ground.json.gz', 'return-proof.json.gz']]
    for path in paths:
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]; refs.append(path)
    out = BASE / BATCH; out.mkdir(); tool = HERE / 'original_captured_ground_parent_lookup_v1_20261103.mjs'; refs.append(tool)
    output = out / 'complete-rendered-parent-lookup.json'
    with (out / 'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), *[str(p.relative_to(ROOT)) for p in paths], str(output.relative_to(ROOT))],
                       cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=3600, check=True)
    result = read(output)
    for path, sha in result['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha; refs.append(ROOT / path)
    assert reservations.owns(lease)
    summary = dict(uids=UIDS, **{k: result[k] for k in ['uniquelyMatched', 'unmatched', 'ambiguous', 'completeRenderedFacesExamined']},
                   capturedSceneApprovalTransferred=False, physicalAcceptance=False, installationApproved=False,
                   sourceGeometryChanges=0, publication=False,
                   qualification='Exact coordinate lookup only through the current production grid/native renderer. No omitted unmatched facets, terrain replacement, fresh full-ground approval, retained-actor acceptance or installation credit.')
    save(out / 'summary.json', summary)
    module('pair_rendered_floor_parent_lookup_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'current-production-rendered-grid-and-native-floor-parent-facet-lookup', list(dict.fromkeys(refs)), summary)
    print(summary, flush=True)


if __name__ == '__main__':
    if '--owned' in sys.argv: owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('pair-rendered-floor-parent-' + str(uuid.uuid4()), ['building:' + u for u in UIDS] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok']
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])

"""Source-bound production collision diagnostic; not scene/installation approval."""
import argparse
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from elegant_basic_footing_foreign_volume_v1_20261028 import BASE, PREFIX, SCOPE, PROPOSAL


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert a.batch.startswith(PREFIX) and '/' not in a.batch
    out, local = BASE/a.batch, HERE/'local'/a.batch
    assert not out.exists()
    rp = BASE/(PREFIX+'sixteen-original-updated-terrain-plan-v1-20261028.json')
    resources = set(read(rp)['resources'])
    lp = local/'reservation.json'
    if not a.owned:
        assert not local.exists()
        claim = reservations.claim('basic-footing-runtime-collision-'+str(uuid.uuid4()), sorted(resources), batch=a.batch, ttl=1800)
        assert claim['ok']
        return execute_reserved(claim['reservation'], lp, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(lp)
    assert reservations.owns(lease) and resources <= set(lease['resources'])
    refs, pins = [Path(__file__), rp], {}

    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE/batch)[1]
            refs.append(BASE/batch/'result.json')
        path = BASE/batch/name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    forms = take(SCOPE, 'form-obligations.json.gz')
    building = take(PROPOSAL, 'input.json')['building']
    proposal = take(PROPOSAL, 'proposal.json')
    assert proposal['uid'] == building['uid'] == 'landsd/213586:0' and building in forms
    current = {}
    for form in forms:
        tile = ROOT/'3d-viewer/city/data/tiles'/(form['tile']+'.json')
        assert digest(tile.read_bytes()) == pins[SCOPE][str(tile.relative_to(ROOT))]
        assert [b for b in read(tile)['buildings'] if b['uid'] == form['uid']] == [form]
        current[str(tile.relative_to(ROOT))] = digest(tile.read_bytes())
        refs.append(tile)
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == pins[SCOPE][str(manifest.relative_to(ROOT))]
    current[str(manifest.relative_to(ROOT))] = digest(manifest.read_bytes())
    refs.append(manifest)
    save(out/'input.json', dict(building=building, foundationBase=proposal['foundationBase'], currentForms=forms, inputHashes=current))
    tool = HERE/'basic_footing_runtime_collision_v1_20261028.mjs'
    refs.append(tool)
    with (out/'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), str((out/'input.json').relative_to(ROOT)), str((out/'runtime-collision.json').relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    report = read(out/'runtime-collision.json')
    for path, sha in report['inputHashes'].items():
        assert digest((ROOT/path).read_bytes()) == sha
        refs.append(ROOT/path)
    result = {k: v for k, v in report.items() if k not in ['inputHashes', 'completeRecursiveProductionModuleClosure']}
    result.update(uids=[building['uid']], sourceGeometryChanges=0, physicalAccepted=False, publication=False)
    save(out/'summary.json', result)
    assert reservations.owns(lease)
    module('basic_footing_runtime_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'production-basic-footing-collision-volumes-and-regional-probes', list(dict.fromkeys(refs)), result)
    print(dict(probes=report['probes'], collisionReviewApproved=False), flush=True)


if __name__ == '__main__':
    main()

"""Replay unchanged production collision checks for explicitly scoped canopy proposals.

Each proposal remains private. This records the complete current region for every
existing single-canopy kernel run; joint native/source and visual checks remain.
"""
import argparse
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'scope']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--proposal', action='append', required=True)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    names = [args.batch, args.scope, *args.proposal]
    assert all(n.startswith('government-xl-') and '/' not in n for n in names)
    assert len(args.proposal) == len(set(args.proposal))
    base = ROOT / 'docs/astra-city/government-import'
    out, local = base / args.batch, HERE / 'local' / args.batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, filename):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        path = base / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    forms = take(args.scope, 'form-obligations.json.gz')
    scope = take(args.scope, 'scope.json')
    assert forms and len(forms) == len({b['uid'] for b in forms}) == scope['intersectingForms']
    resources = {('building:' if b['uid'].startswith('landsd/') else 'source-form:') + b['uid'] for b in forms}
    resources.update('building:' + uid for uid in scope['uids'])
    resources.add('terrain:city/data/terrain.json')
    for record in scope['terrainContacts']:
        resources.add('terrain:' + record['url'])
    leasefile = local / 'reservation.json'
    if not args.owned:
        assert not local.exists()
        claim = reservations.claim('current-canopy-collision-' + str(uuid.uuid4()), sorted(resources), batch=args.batch, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], leasefile, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(leasefile)
    assert reservations.owns(lease) and set(lease['resources']) == resources
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_sha = digest(manifest.read_bytes())
    assert manifest_sha == pins[args.scope][str(manifest.relative_to(ROOT))]
    refs.append(manifest)
    hashes = {str(manifest.relative_to(ROOT)): manifest_sha}
    for b in forms:
        tile = ROOT / '3d-viewer/city/data/tiles' / (b['tile'] + '.json')
        key = str(tile.relative_to(ROOT))
        assert digest(tile.read_bytes()) == pins[args.scope][key]
        assert [row for row in read(tile)['buildings'] if row['uid'] == b['uid']] == [b]
        hashes[key] = digest(tile.read_bytes())
        refs.append(tile)
    kernel = HERE / 'basic_canopy_runtime_collision_v2_20261031.mjs'
    kernel_sha = digest(kernel.read_bytes())
    refs.append(kernel)
    rows, uids = [], set()
    for batch in args.proposal:
        assert reservations.owns(lease)
        summary = take(batch, 'summary.json')
        building = take(batch, 'input.json')['building']
        proposal = take(batch, 'proposal.json')
        uid = building['uid']
        assert uid not in uids and building in forms
        uids.add(uid)
        assert uid == summary['uid'] == proposal['uid']
        assert summary['fullPostFootprintsMeetGround'] and summary['wholeRoofClear']
        assert summary['roofAndRecordedElevationsUnchanged'] and summary['installationApproved'] is False
        assert building['kind'] == 'roof' and building['structureType'] == 'Open-sided Structure'
        assert building['baseSource'] == 'terrain-estimated' and building['heightSource'] == 'estimated'
        assert building.get('baseHeightHKPD') is None and building.get('topHeightHKPD') is None
        assert summary['foundationBase'] == proposal['foundationBase'] < building['base'] - .02
        sub = out / uid.split('/')[1].replace(':', '-')
        save(sub / 'input.json', dict(building=building, foundationBase=proposal['foundationBase'], currentForms=forms, expectedFormCount=len(forms), inputHashes=hashes))
        with (sub / 'worker.log').open('w') as log:
            subprocess.run(['node', str(kernel), str((sub / 'input.json').relative_to(ROOT)), str((sub / 'collision.json').relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
        report = read(sub / 'collision.json')
        assert report['uid'] == uid and report['postCount'] == summary['completePostCount']
        assert report['onlyPostBottomsChanged'] and report['allRoofPartsExactlyRetained']
        assert report['unchangedRegionalForms'] == len(forms) - 1
        assert report['collisionReviewApproved'] is False and report['installationApproved'] is False
        for path, sha in report['inputHashes'].items():
            assert digest((ROOT / path).read_bytes()) == sha
            refs.append(ROOT / path)
        rows.append(dict(uid=uid, posts=report['postCount'], probes=report['probes'], addedTargetCollisionProbes=report['addedTargetCollisionProbes'], addedGlobalCollisionProbes=report['addedGlobalCollisionProbes']))
    assert digest(kernel.read_bytes()) == kernel_sha and reservations.owns(lease)
    for path, sha in hashes.items():
        assert digest((ROOT / path).read_bytes()) == sha
    result = dict(uids=sorted(uids), forms=len(forms), rows=rows, sourceGeometryChanges=0, sourcePoseChanges=0, productionChanges=0, physicalAcceptance=False, collisionReviewApproved=False, installationApproved=False, publication=False, qualification='Every proposal independently replays the unchanged production collision kernel over the complete current region. Roofs, XZ, post tops and all other BASIC volumes are preserved. These are individual monotonicity probes, not simultaneous multi-canopy/native collision, physical-role, visual or publication acceptance.')
    save(out / 'summary.json', result)
    module('current_canopy_scope_collision_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'complete-current-region-individual-canopy-production-collision-context', list(dict.fromkeys(refs)), result)
    print(dict(canopies=len(rows), forms=len(forms), probes=sum(r['probes'] for r in rows)), flush=True)


if __name__ == '__main__':
    main()

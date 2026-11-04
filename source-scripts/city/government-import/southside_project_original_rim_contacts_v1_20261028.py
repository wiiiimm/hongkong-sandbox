"""Canonical original footing diagnostics for all 16 project parts against podium."""
import argparse
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-southside-project-original-rim-contacts-v1-20261028'
DOC, LOCAL = BASE / BATCH, HERE / 'local' / BATCH
LEASE = LOCAL / 'reservation.json'
CAP = BASE / 'government-xl-southside-project-original-recovery-v1-20261028'
JS = HERE / 'original_neighbour_rim_contacts_v1_20261028.mjs'
PODIUM = 'landsd/315025:0'


def owned():
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists()
    _, pins = authenticate(CAP)
    path = CAP / 'selection.json.gz'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    selection = read(path)
    assert len(selection['rows']) == 17
    assert {'building:' + r['uid'] for r in selection['rows']} <= set(lease['resources'])
    refs = [Path(__file__), JS, CAP / 'result.json', path, HERE / 'exact_packed_world_geometry_20261009.py']
    triangles, sources = {}, {}
    for row in selection['rows']:
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256']
        tri = decode_original_world_triangles(asset.read_bytes())
        assert len(tri) == row['triangles'] and np.isfinite(tri).all()
        triangles[row['uid']] = tri
        sources[row['uid']] = dict(uid=row['uid'], sourceSHA256=row['sourceSHA256'],
                                   sourceKey=row['native']['cacheKey'] + '/' + row['modelId'],
                                   originalWorldSHA256=digest(tri.astype('<f8').tobytes()), faces=len(tri))
        refs.append(asset)
    support = triangles[PODIUM]
    geometry = lambda t: dict(position=t.reshape(-1).tolist(), index=list(range(t.size//3)))
    inputs = []
    for uid in sorted(set(triangles) - {PODIUM}):
        tri = triangles[uid]
        inputs.append(dict(uid=uid, mode='original', source=geometry(tri), support=geometry(support),
                           sourceMinimumY=float(tri[:, :, 1].min()),
                           sourceWorldSHA256=sources[uid]['originalWorldSHA256'],
                           supportWorldSHA256=sources[PODIUM]['originalWorldSHA256']))
    save(DOC / 'input.json.gz', dict(rows=inputs))
    proc = subprocess.run(['node', str(JS), str((DOC/'input.json.gz').relative_to(ROOT)),
                           str((DOC/'contacts.json.gz').relative_to(ROOT))], cwd=ROOT, capture_output=True, text=True)
    save(DOC / 'command.json', dict(exitCode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr))
    assert proc.returncode == 0
    report = read(DOC / 'contacts.json.gz')
    assert len(report['rows']) == 16 and {r['uid'] for r in report['rows']} == set(triangles) - {PODIUM}
    for name, sha in report['inputHashes'].items():
        assert digest((ROOT/name).read_bytes()) == sha
        refs.append(ROOT/name)
    rows = [{k: v for k, v in r.items() if k not in ['rawInterface', 'mapped']} for r in report['rows']]
    result = dict(uids=sorted(triangles), rows=rows, sourceScopes=sources, podiumSupportUid=PODIUM,
                  mode='original', terrainIncluded=False, currentSceneSupportAccepted=False,
                  physicalAccepted=False, identityAccepted=False, installationApproved=False, sourceGeometryChanges=0,
                  qualification='Unchanged canonical low-rim/interface kernel for every complete original part against every original podium face. Geometric contact diagnostics only. No original facets changed, no support/root role approved, no terrain or current BASIC flags cleared. Other project parts are not included as supports in this first podium-only pass; unresolved points require exact component/support follow-through.')
    save(DOC / 'summary.json', result)
    assert reservations.owns(lease)
    module('southside_project_original_rim_contacts_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'sixteen-original-project-part-canonical-podium-rim-queries', list(dict.fromkeys(refs)), result)
    print(rows, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    if args.owned:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    authenticate(CAP)
    rows = read(CAP / 'selection.json.gz')['rows']
    claim = reservations.claim('southside-project-original-rim-' + str(uuid.uuid4()),
                               ['building:' + r['uid'] for r in rows], batch=BATCH, ttl=3600)
    assert claim['ok']
    execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])


if __name__ == '__main__':
    main()

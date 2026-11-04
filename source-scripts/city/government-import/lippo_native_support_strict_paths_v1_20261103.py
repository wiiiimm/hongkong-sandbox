"""Route measured Lippo tower warnings to independently replayed strict roots.

Original shared edges only; no new roots, joins, support approval or geometry.
"""
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from original_face_attachment_minimax_v2_20261024 import attachment_paths
from original_endpoint_root_retry_v1_20261102 import retry_paths, passed
from pool_incident_wall_contacts_v1_20261017 import closest

BASE = ROOT / 'docs/astra-city/government-import'
INPUT = 'government-xl-lippo-current-native-podium-migration-probe-v1-20261103'
BATCH = 'government-xl-lippo-native-support-strict-paths-v1-20261103'
LOCAL = HERE / 'local' / BATCH
TOWER, PODIUM = 'landsd/239465:0', 'landsd/231645:0'


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease)
    out = BASE / BATCH
    assert not out.exists()
    receipt, pins = authenticate(BASE / INPUT)
    assert receipt['uids'] == [TOWER, PODIUM]
    refs = [Path(__file__), BASE / INPUT / 'result.json']

    def take(name):
        path = BASE / INPUT / name
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    summary = take('summary.json')
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == summary['currentManifestSHA256']
    refs.append(manifest)
    attrs = take('tower-attributes.json.gz')
    assert attrs['startEndAllInputsVerified'] and len(attrs['rows']) == 1
    # Independently frozen current renderer input binds exact original assets,
    # complete catalogue entries, current forms and recursive production closure.
    for path, sha in attrs['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
        refs.append(ROOT / path)
    rows = []
    for mode in ['original', 'literal', 'leftF32', 'balancedF32']:
        assert reservations.owns(lease)
        input_data = take(mode + '/input.json.gz')
        previous = take(mode + '/diagnostic.json.gz')
        support = take(mode + '/support.json.gz')['rows'][0]
        assert len(input_data['rows']) == 1 and support['uid'] == TOWER
        source = input_data['rows'][0]
        assert source['uid'] == TOWER
        tri = np.asarray(source['position'], dtype='<f8').reshape(-1, 3)[np.asarray(source['index']).reshape(-1, 3)]
        podium = np.asarray(input_data['podium'], dtype='<f8')
        assert len(tri) == 3597 and len(podium) == 13725
        assert digest(tri.tobytes()) == previous['sourceWorldSHA256ByUid'][TOWER]
        assert digest(podium.tobytes()) == previous['sourceWorldSHA256ByUid'][PODIUM]
        assert support['proof'] == previous['support']
        input_path = BASE / INPUT / mode / 'input.json.gz'
        root_path = out / (mode + '-strict-roots.json.gz')
        root_path.parent.mkdir(parents=True, exist_ok=True)
        tool = HERE / 'original_strict_support_roots_v1_20261024.mjs'
        subprocess.run(['node', str(tool), str(input_path), str(root_path)], cwd=ROOT, check=True, timeout=1800)
        roots = read(root_path)
        assert roots['uid'] == TOWER and roots['inputSHA256'] == digest(input_path.read_bytes())
        assert roots['strict'] == previous['support']['strictLowRim']
        lo, hi = tri.min(1), tri.max(1)
        renderable = np.linalg.norm(np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0]), axis=1) > 0

        def incident(point):
            point = np.asarray(point)
            candidates = np.flatnonzero(renderable & np.all(lo <= point+.001, axis=1) & np.all(hi >= point-.001, axis=1))
            faces = [int(i) for i in candidates if np.linalg.norm(closest(point, tri[i])-point) <= .001]
            assert faces
            return faces

        anchors = [dict(r, incidentFaces=incident(r['position'])) for r in roots['roots'] if r['strictAccepted']]
        assert len(anchors) == previous['support']['strictContacts']
        targets = [dict(witness=w, incidentFaces=incident(w['position'])) for w in previous['support']['unresolved']]
        first = attachment_paths(tri, dict(targets=targets, proof=dict(contacts=[])), [], strict_anchors=anchors)
        recovered, attempts = retry_paths(tri, first, anchors)
        assert len(first) == len(recovered) == len(targets)
        save(out / (mode + '.json.gz'), dict(mode=mode, sourceWorldSHA256=previous['sourceWorldSHA256ByUid'][TOWER],
              supportWorldSHA256=previous['sourceWorldSHA256ByUid'][PODIUM], canonicalStrictRoots=anchors,
              rawMinimaxPaths=first, endpointRetryAttempts=attempts, rows=recovered,
              newRoots=0, intercomponentJoins=0, sourceGeometryChanges=0, supportApproved=False))
        row = dict(mode=mode, strictAnchors=len(anchors), rawUnresolved=len(targets),
                   initiallyPassing=sum(passed(r) for r in first), passingWithExistingEndpointRetry=sum(passed(r) for r in recovered),
                   remaining=sum(not passed(r) for r in recovered), newRoots=0, intercomponentJoins=0)
        rows.append(row)
        print(row, flush=True)
        refs.append(tool)
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == summary['currentManifestSHA256']
    result = dict(uids=[TOWER, PODIUM], currentManifestSHA256=summary['currentManifestSHA256'], sourceSHA256ByUid=summary['sourceSHA256ByUid'],
                  rows=rows, allWarningsHaveExistingStrictRootPaths=all(r['remaining'] == 0 for r in rows),
                  rawDirectSupportFailuresPreserved=True, sourceGeometryChanges=0, sourcePoseChanges=0, newRoots=0, intercomponentJoins=0,
                  supportApproved=False, physicalAcceptance=False, installationApproved=False, publication=False,
                  qualification='Every raw strict-interface warning retains its original measurement. Existing canonical support roots are replayed independently. Shared original edges and alternate existing roots use the unchanged endpoint ceiling and 1mm incidence guard. Path evidence alone does not migrate the installed support contract or approve source roles, compound clearance, terrain or publication.')
    save(out / 'summary.json', result)
    refs.extend(HERE / n for n in ['original_face_attachment_minimax_v2_20261024.py', 'original_endpoint_root_retry_v1_20261102.py', 'pool_incident_wall_contacts_v1_20261017.py', 'support-contact.mjs'])
    module('lippo_strict_paths_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'current-original-lippo-native-support-existing-strict-root-path-diagnostic', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('lippo-existing-strict-roots-' + str(uuid.uuid4()), ['building:' + u for u in [TOWER, PODIUM]] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])

"""Retry four Langham endpoint failures against unchanged verified native roots."""
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from observed_reserved_runner_v4_20261103 import execute_reserved
from original_assembly_four_world_pair_context_v3_20261101 import represented
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_endpoint_root_retry_grouped_v1_20261103 import retry_paths
from original_endpoint_root_retry_v1_20261102 import passed

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-langham-existing-strict-endpoint-retry-v1-20261103'
LOCAL = HERE / 'local' / BATCH
RUNTIME = 'government-xl-silvercord-lippo-five-original-floor-runtime-v1-20261103'
ATTR = 'government-xl-silvercord-lippo-five-original-attributes-v2-20261103'
PRIOR = 'government-xl-silvercord-lippo-five-original-237843-0-strict-paths-v1-20261103'
STRICT = 'government-xl-silvercord-lippo-five-original-237843-0-support-v1-20261103'
UID, SUPPORT = 'landsd/237843:0', 'landsd/231645:0'


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease) and not (BASE / BATCH).exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        path = BASE / batch / name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(RUNTIME, 'selection.json.gz')
    attrs = take(ATTR, 'attributes.json.gz')
    assert attrs['startEndAllInputsVerified']
    strict = take(STRICT, 'summary.json')
    prior = take(PRIOR, 'summary.json')
    assert strict['supportedUid'] == UID and strict['supportUids'] == [SUPPORT]
    assert strict['sourceSHA256ByUid'] == prior['sourceSHA256ByUid']
    worlds = {}
    for uid in [UID, SUPPORT]:
        row = next(r for r in selection['rows'] if r['uid'] == uid)
        attr = next(r for r in attrs['rows'] if r['uid'] == uid)
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == attr['sourceSHA256'] == strict['sourceSHA256ByUid'][uid]
        refs.append(asset)
        worlds[uid] = represented(attr, decode_original_world_triangles(asset.read_bytes()))
    results = []
    for mode, tri in worlds[UID].items():
        assert reservations.owns(lease)
        old = take(PRIOR, mode + '.json.gz')
        original = next(r for r in strict['rows'] if r['mode'] == mode)
        assert old['sourceWorldSHA256'] == original['sourceWorldSHA256ByUid'][UID] == digest(tri.tobytes())
        assert old['supportWorldSHA256'] == original['sourceWorldSHA256ByUid'][SUPPORT] == digest(worlds[SUPPORT][mode].tobytes())
        roots = take(PRIOR, mode + '-strict-roots.json.gz')
        input_path = BASE / STRICT / mode / 'input.json.gz'
        take(STRICT, mode + '/input.json.gz')
        assert roots['inputSHA256'] == digest(input_path.read_bytes())
        assert roots['strict'] == original['support']['strictLowRim']
        anchors = old['canonicalStrictRoots']
        assert len(anchors) == original['support']['strictContacts'] == 70
        assert [r['witness'] for r in old['rows']] == original['support']['unresolved']
        paths, attempts = retry_paths(tri, old['rows'], anchors)
        assert len(paths) == len(old['rows']) == 8
        save(BASE / BATCH / (mode + '.json.gz'), dict(mode=mode, sourceWorldSHA256=old['sourceWorldSHA256'],
            supportWorldSHA256=old['supportWorldSHA256'], originalFailedRows=old['rows'],
            existingVerifiedRoots=anchors, rows=paths, attempts=attempts, newRoots=0, sourceGeometryChanges=0))
        results.append(dict(mode=mode, previousFailures=sum(not passed(r) for r in old['rows']),
            remainingFailures=sum(not passed(r) for r in paths), warnings=len(paths),
            sharedGraphBuilds=len({r['anchorIndex'] for r in attempts}), rootAttempts=len(attempts)))
        print(results[-1], flush=True)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    refs.extend(HERE / n for n in ['original_endpoint_root_retry_grouped_v1_20261103.py',
        'original_endpoint_root_retry_v1_20261102.py', 'original_face_attachment_minimax_v2_20261024.py'])
    summary = dict(uids=[UID, SUPPORT], sourceSHA256ByUid=strict['sourceSHA256ByUid'], rows=results,
        allFourWorldPathsPass=all(r['remainingFailures'] == 0 for r in results), newRoots=0,
        sourceGeometryChanges=0, sourcePoseChanges=0, supportApproved=False, physicalAcceptance=False,
        installationApproved=False, publication=False, qualification=__doc__ +
        ' Authenticated prior independently reproduced canonical roots and exact source/support arrays are unchanged. Existing endpoint height, strict gap and1mm source-incidence limits remain. Preserve original failed paths; no support/publication approval.')
    save(BASE / BATCH / 'summary.json', summary)
    module('langham_existing_endpoint_recovery', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'exact-original-langham-existing-strict-endpoint-retry', list(dict.fromkeys(refs)), summary)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('langham-existing-endpoints-' + str(uuid.uuid4()),
            ['building:' + u for u in [UID, SUPPORT]] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])

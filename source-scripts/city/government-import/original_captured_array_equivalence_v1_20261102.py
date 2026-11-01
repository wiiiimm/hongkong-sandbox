"""Compare complete captured arrays after adding explicit original companions.

This proves input equality only. It transfers no acceptance and says nothing
about contacts involving newly added actors, which need independent checks.
"""
import argparse
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

def equal_array(a, b, dtype):
    left, right = np.asarray(a, dtype=dtype), np.asarray(b, dtype=dtype)
    assert left.shape == right.shape and np.isfinite(left).all() and np.isfinite(right).all()
    assert left.tobytes() == right.tobytes(), 'Captured array changed; reuse is not proved'
    return dict(shape=list(left.shape), sha256=digest(left.tobytes()))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'before', 'before-attributes', 'after', 'after-attributes']:
        p.add_argument('--' + k, required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    names = [a.before, a.before_attributes, a.after, a.after_attributes]
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, *names])
    base = ROOT / 'docs/astra-city/government-import'
    out, lp = base / a.batch, HERE / 'local' / a.batch / 'reservation.json'
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    def take(batch, path):
        if batch not in pins:
            _, pins[batch] = authenticate(base / batch)
            refs.append(base / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    before = take(a.before, base / a.before / 'selection.json.gz')
    after = take(a.after, base / a.after / 'selection.json.gz')
    old, new = [{r['uid']: r for r in s['rows']} for s in [before, after]]
    assert len(old) == len(before['rows']) and len(new) == len(after['rows'])
    assert set(old) < set(new) and 0 < len(new) <= 40
    if not a.owned:
        assert not lp.parent.exists()
        c = reservations.claim('captured-original-parity-' + str(uuid.uuid4()),
            ['building:' + u for u in sorted(new)], batch=a.batch, ttl=3600)
        assert c['ok'], c
        return execute_reserved(c['reservation'], lp, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(lp)
    assert reservations.owns(lease)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == before['manifestSHA256'] == after['manifestSHA256']
    refs.append(manifest)
    geom = [{r['uid']: r for r in take(n, HERE / 'local' / n / 'runtime-geometry.json.gz')['rows']}
            for n in [a.before, a.after]]
    attr_docs = [take(n, base / n / 'attributes.json.gz') for n in [a.before_attributes, a.after_attributes]]
    assert all(d['startEndAllInputsVerified'] for d in attr_docs)
    attrs = [{r['uid']: r for r in d['rows']} for d in attr_docs]
    modules = [{k: v for k, v in d['inputHashes'].items() if k.startswith('3d-viewer/') and k.endswith('.js')}
               for d in attr_docs]
    assert modules[0] == modules[1] and '3d-viewer/city/official-model-assets.js' in modules[0]
    for name, sha in modules[0].items():
        path = ROOT / name
        assert digest(path.read_bytes()) == sha
        refs.append(path)
    rows = []
    for uid in sorted(old):
        left, right = old[uid], new[uid]
        assert left['source'] == right['source'] and left['native'] == right['native']
        assert left['candidate']['entry'] == right['candidate']['entry']
        sha = left['sourceSHA256']
        assert sha == right['sourceSHA256']
        for r in [left, right]:
            path = ROOT / r['candidate']['path']
            assert digest(path.read_bytes()) == sha
            refs.append(path)
        signatures = {}
        for key, dtype in [('position', '<f8'), ('index', '<i8'), ('drawnGroundGeometry', '<f8')]:
            signatures[key] = equal_array(geom[0][uid][key], geom[1][uid][key], dtype)
        for key in ['completeLiteralWorldPosition', 'completeExplicitLeftAssociatedFloat32WorldPosition',
                    'completeExplicitBalancedFloat32WorldPosition', 'completeOriginalIndex']:
            signatures[key] = equal_array(attrs[0][uid][key], attrs[1][uid][key],
                                         '<i8' if key == 'completeOriginalIndex' else '<f8')
        assert all(r[uid]['sourceSHA256'] == sha for r in [*geom, *attrs])
        rows.append(dict(uid=uid, sourceSHA256=sha, completeCapturedArraySignatures=signatures))
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == after['manifestSHA256']
    result = dict(uids=sorted(old), newlyCapturedUids=sorted(set(new) - set(old)), rows=rows,
        beforeRuntime=a.before, afterRuntime=a.after, identicalCompleteSourceAndGroundInputs=True,
        originalSourceBytesAndPoseMetadataIdentical=True, sourceGeometryChanges=0, sourcePoseChanges=0,
        physicalAcceptance=False, collisionApproved=False, installationApproved=False, publication=False,
        qualification=__doc__ + ' Every old position, unused vertex, index, saved ground facet and all three represented world streams match byte-for-byte. Old measurements still require their own producer bindings; new-actor collision, identity, runtime and publication checks remain separate.')
    save(out / 'summary.json', result)
    module('captured_original_array_equivalence', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'exact-complete-original-captured-array-equivalence-no-acceptance', list(dict.fromkeys(refs)), result)

if __name__ == '__main__':
    main()

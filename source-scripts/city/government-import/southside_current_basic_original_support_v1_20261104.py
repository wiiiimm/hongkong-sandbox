"""Bind actual current BASIC support diagnostics, preserving every raw terrain flag."""
import argparse
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-southside-current-basic-original-support-v1-20261104'
OUT = BASE / BATCH
LEASE = HERE / 'local' / (BATCH + '-lease') / 'reservation.json'
RUNTIME = 'government-xl-southside-source-bound-current-podium-runtime-v1-20261104'
REGRESSION = 'government-xl-southside-source-bound-basic-regressions-v2-20261104'
ATTRIBUTES = 'government-xl-southside-current-podium-attributes-v1-20261104'
SUPPORT = 'landsd/315025:0'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    assert not OUT.exists()
    _, rp = authenticate(BASE / REGRESSION)
    formpath = BASE / REGRESSION / 'terrain-only/neighbour-inputs.json.gz'
    assert digest(formpath.read_bytes()) == rp[str(formpath.relative_to(ROOT))]
    forms = [r['building'] for r in read(formpath)['rows']]
    assert len(forms) == 84
    resources = {('building:' if f['uid'].startswith('landsd/') else 'source-form:') + f['uid'] for f in forms}
    resources |= {'building:' + SUPPORT, 'terrain:city/data/terrain.json'}
    if not args.owned:
        assert not LEASE.parent.exists()
        claim = reservations.claim('southside-current-basic-original-support-' + str(uuid.uuid4()), sorted(resources), batch=BATCH, ttl=3600)
        assert claim['ok']
        return execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])
    lease = read(LEASE)
    assert reservations.owns(lease) and resources <= set(lease['resources'])
    refs = [Path(__file__)]
    pins = {}

    def take(batch, path):
        if batch not in pins:
            _, pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    inputs = take(REGRESSION, formpath)
    report = take(REGRESSION, BASE / REGRESSION / 'terrain-only/neighbour-checks.json')
    flagged = {r['uid'] for r in report['rows'] if r['reasons']}
    assert len(flagged) == 16
    for r in report['rows']:
        assert not r['reasons'] or r['reasons'] == ['increased-neighbour-ground-gap']
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    for path, sha in inputs['inputHashes'].items():
        assert digest((ROOT/path).read_bytes()) == sha
        refs.append(ROOT/path)
    selected = take(RUNTIME, BASE / RUNTIME / 'selection.json.gz')
    assert selected['manifestSHA256'] == digest(manifest.read_bytes())
    assert len(selected['rows']) == 1 and selected['rows'][0]['uid'] == SUPPORT
    row = selected['rows'][0]
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256']
    refs.append(asset)
    runtime = take(RUNTIME, HERE / 'local' / RUNTIME / 'runtime-geometry.json.gz')
    assert len(runtime['rows']) == 1 and runtime['rows'][0]['uid'] == SUPPORT
    attr_tool = HERE / 'selected_original_render_attributes_v1.py'
    # The existing attribute producer is read-only and runs inside this full lease.
    assert not (BASE / ATTRIBUTES).exists()
    OUT.mkdir()
    with (OUT / 'attributes-worker.log').open('w') as log:
        subprocess.run([sys.executable, str(attr_tool), '--batch', ATTRIBUTES, '--capture', RUNTIME], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    attrs = take(ATTRIBUTES, BASE / ATTRIBUTES / 'attributes.json.gz')
    assert attrs['startEndAllInputsVerified'] and len(attrs['rows']) == 1
    attr = attrs['rows'][0]
    assert attr['sourceSHA256'] == runtime['rows'][0]['sourceSHA256'] == row['sourceSHA256']
    index = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    literal = np.asarray(attr['completeLiteralWorldPosition']).reshape(-1, 3)
    g = runtime['rows'][0]
    assert np.array_equal(literal[index], np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)])
    original = decode_original_world_triangles(asset.read_bytes())
    assert original.shape == (11699, 3, 3)
    worlds = dict(original=original, literal=literal[index], leftF32=np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1, 3)[index], balancedF32=np.asarray(attr['completeExplicitBalancedFloat32WorldPosition']).reshape(-1, 3)[index])
    assert all(np.isfinite(t).all() for t in worlds.values())
    save(OUT / 'input.json.gz', dict(currentManifestSHA256=selected['manifestSHA256'], supportUid=SUPPORT, sourceSHA256=row['sourceSHA256'], forms=[f for f in forms if f['uid'] in flagged], supportModes=[dict(name=name, worldSHA256=digest(tri.astype('<f8').tobytes()), geometry=dict(position=tri.ravel().tolist(), index=list(range(len(tri)*3)))) for name, tri in worlds.items()], evidenceRefs=[dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())) for p in dict.fromkeys(refs)]))
    tool = HERE / 'current_basic_on_original_support_diagnostic_v1_20261104.mjs'
    with (OUT / 'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), str(OUT.relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    checks = read(OUT / 'checks.json.gz')
    assert len(checks['rows']) == 64
    summary = []
    for uid in sorted(flagged):
        modes = [r for r in checks['rows'] if r['uid'] == uid]
        assert {r['mode'] for r in modes} == set(worlds)
        summary.append(dict(uid=uid, allFourInterfacesPassed=all(r['proof']['passed'] for r in modes), modes=[dict(mode=r['mode'], passed=r['proof']['passed'], samples=r['proof']['samples'], strictContacts=r['proof']['strictContacts'], wallContacts=r['proof']['wallIntersections'], unresolved=len(r['proof']['unresolved']), minGap=r['proof']['strictLowRim']['minGap'], maxGap=r['proof']['strictLowRim']['maxGap']) for r in modes]))
    for path, sha in checks['inputHashes'].items():
        assert digest((ROOT/path).read_bytes()) == sha
        refs.append(ROOT/path)
    refs += [tool, attr_tool, HERE/'exact_packed_world_geometry_20261009.py']
    assert reservations.owns(lease)
    result = dict(uids=[SUPPORT], supportUid=SUPPORT, sourceSHA256=row['sourceSHA256'], flaggedBasicForms=16, interfacesTested=64, rows=summary, allFourInterfacePasses=sum(r['allFourInterfacesPassed'] for r in summary), rawGroundGapFlagsPreserved=True, fullScopeForms=84, wholeSourcePhysicalAccepted=False, supportDependenciesApproved=False, identityAccepted=False, installationApproved=False, sourceGeometryChanges=0, basicGeometryChanges=0, qualification='Actual current production BASIC render meshes and all complete original/literal/explicit Float32 podium worlds. Unchanged canonical [-0.1,1]m support kernel and bounded wall rule. Positive sampled contacts do not establish full-floor clearance, support semantics, lifecycle dependency/fallback, original identity or publication. All84 obligations and all16 raw terrain-gap flags remain; no actor suppressed or replaced.')
    save(OUT / 'summary.json', result)
    module('southside_current_basic_original_support_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'actual-current-basic-original-podium-four-world-interface-diagnostic', list(dict.fromkeys(refs)), result)
    print(dict(flagged=16, allFourInterfacePasses=result['allFourInterfacePasses'], unresolvedUids=[r['uid'] for r in summary if not r['allFourInterfacesPassed']]), flush=True)


if __name__ == '__main__':
    main()

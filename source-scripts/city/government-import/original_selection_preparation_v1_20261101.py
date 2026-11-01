"""Run existing diagnostics for an exact acquired or explicitly merged original batch.

Supporting originals need not belong to the fixed521 cohort. Only the existing
acquisition or explicit merge receipt schemas are admitted, with all source
approval flags false. This grants no installation credit.
"""
import argparse, subprocess, sys, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--capture', required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.capture])
    base = ROOT / 'docs/astra-city/government-import'
    out, local = base / a.batch, HERE / 'local' / a.batch
    receipt, pins = authenticate(base / a.capture)
    selected = base / a.capture / 'selection.json.gz'
    assert digest(selected.read_bytes()) == pins[str(selected.relative_to(ROOT))]
    selection = read(selected)
    uids = sorted(r['uid'] for r in selection['rows'])
    assert 0 < len(uids) == len(set(uids)) <= 40
    if receipt['stage']=='explicit-current-unique-native-original-source-recovery-no-acceptance':
        declared=set(receipt['recoveredUids'])
    else:
        assert receipt['stage']=='explicit-current-original-selection-merge'
        declared=set(receipt['sourceOrigins'])
    assert set(uids)==declared and not receipt.get('installationApproved') and not receipt.get('publication')
    for row in selection['rows']:
        assert not any(row['candidate']['entry'].get(k) for k in ['placementReviewed','publicationApproved','identityReviewApproved','sourceIdentityReviewed'])
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    start = digest(manifest.read_bytes())
    assert start == selection['manifestSHA256']
    installed = {e['uid'] for url in read(manifest)['officialModelCatalogues'] for e in read(ROOT / '3d-viewer' / url)['models']}
    assert not installed.intersection(uids)
    resources = ['building:' + u for u in uids] + ['immutable-source-proof:' + a.batch]
    leasefile = local / 'reservation.json'
    if not a.owned:
        assert not local.exists() and not out.exists()
        c = reservations.claim('acquired-original-preparation-' + str(uuid.uuid4()), resources, batch=a.batch, ttl=3600)
        assert c['ok'], c
        return execute_reserved(c['reservation'], leasefile, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(leasefile)
    assert reservations.owns(lease) and set(lease['resources']) == set(resources) and not out.exists()
    out.mkdir()
    refs = [Path(__file__), base / a.capture / 'result.json', selected, manifest]
    completed = []
    phases = [('runtime', 'selected_original_current_capture_v3.py', ['--capture', a.capture, *[v for u in uids for v in ['--uid', u]]]),
        ('identity', 'selected_original_identity_v3.py', ['--capture', a.batch + '-runtime']),
        ('attributes', 'selected_original_render_attributes_v1.py', ['--capture', a.batch + '-runtime'])]
    try:
        for name, script, args in phases:
            assert reservations.owns(lease) and digest(manifest.read_bytes()) == start
            tool = HERE / script
            sha = digest(tool.read_bytes())
            batch = a.batch + '-' + name
            assert not (base / batch).exists()
            with (out / (name + '.log')).open('w') as log:
                subprocess.run([sys.executable, str(tool), '--batch', batch, *args], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
            assert digest(tool.read_bytes()) == sha
            r, _ = authenticate(base / batch)
            completed.append(dict(batch=batch, jobId=r['jobId']))
            save(out / 'state.json', dict(running=True, completed=completed))
            refs.extend([tool, base / batch / 'result.json'])
        assert reservations.owns(lease) and digest(manifest.read_bytes()) == start
        result = dict(uids=uids, completed=completed, currentManifestSHA256=start, sourceGeometryChanges=0,
            installationApproved=False, publication=False, newlyInstalled=0, scriptExternalAICalls=0)
        save(out / 'state.json', dict(running=False, completed=completed))
        save(out / 'summary.json', result)
        module('acquired_original_preparation_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'explicit-acquired-original-runtime-identity-attributes-only', refs, result)
    except BaseException as error:
        save(out / 'state.json', dict(running=False, completed=completed, error=repr(error)))
        raise

if __name__ == '__main__': main()

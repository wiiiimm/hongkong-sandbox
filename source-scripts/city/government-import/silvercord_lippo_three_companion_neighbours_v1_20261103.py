"""Check only the three new sources, retaining their entire current neighbour scope."""
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from observed_reserved_runner_v4_20261103 import execute_reserved

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-lippo-three-companion-neighbours-v1-20261103'
LOCAL = HERE / 'local' / BATCH
UIDS = ['landsd/237843:0', 'landsd/238659:0', 'landsd/239032:0']
SCOPE = 'government-xl-silvercord-lippo-five-original-collision-scope-v1-20261103'
RUNTIME = 'government-xl-silvercord-lippo-five-original-floor-runtime-v1-20261103'
ATTR = 'government-xl-silvercord-lippo-five-original-attributes-v2-20261103'
INVENTORY = 'government-xl-after-june-current-native-bounds-reused-v1-20261103'


def main():
    _, pins = authenticate(BASE / SCOPE)
    path = BASE / SCOPE / 'summary.json'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    scope = read(path)
    assert set(UIDS) <= set(scope['uids'])
    resources = {'building:' + uid for uid in UIDS} | {'terrain:city/data/terrain.json'}
    scope_files = []
    for row in scope['rows']:
        if row['uid'] not in UIDS:
            continue
        resources.update('building:' + n['uid'] for n in row['nearbyNativeActors'])
        p = BASE / SCOPE / (row['uid'].split('/')[1] + '-forms.json.gz')
        assert digest(p.read_bytes()) == pins[str(p.relative_to(ROOT))]
        scope_files.append(p)
        resources.update(('building:' if r['building']['uid'].startswith('landsd/') else 'source-form:')
                         + r['building']['uid'] for r in read(p))
    if '--owned' not in sys.argv:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('three-exact-original-neighbours-' + str(uuid.uuid4()),
            sorted(resources), batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease) and set(lease['resources']) == resources
    out = BASE / BATCH
    assert not out.exists()
    out.mkdir()
    refs = [Path(__file__), BASE / SCOPE / 'result.json', path, *scope_files]
    subset = [v for uid in UIDS for v in ['--uid', uid]]
    shared = ['--scope', SCOPE, '--runtime', RUNTIME, '--attributes', ATTR]
    native = BATCH + '-native'
    phases = [('selected_original_overlapping_native_contacts_v4_20261103.py', native,
               shared + ['--inventory', INVENTORY] + subset),
              ('selected_original_native_fallback_contacts_v2_20261026.py', BATCH + '-fallbacks',
               shared + ['--inventory', INVENTORY] + subset),
              ('selected_original_model_only_foreign_contacts_v3_20261024.py', BATCH + '-basics',
               shared + ['--native-contacts', native] + subset)]
    completed = []
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == scope['currentManifestSHA256']
    refs.append(manifest)
    for i, (name, batch, args) in enumerate(phases):
        assert reservations.owns(lease)
        tool = HERE / name
        sha = digest(tool.read_bytes())
        save(out / 'state.json', dict(running=True, phase=batch, completed=completed))
        with (out / ('phase-' + str(i) + '.log')).open('w') as log:
            subprocess.run([sys.executable, str(tool), '--batch', batch, *args], cwd=ROOT,
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        assert reservations.owns(lease) and digest(tool.read_bytes()) == sha
        receipt, _ = authenticate(BASE / batch)
        assert set(receipt['uids']) == set(UIDS)
        completed.append(dict(batch=batch, jobId=receipt['jobId']))
        refs.extend([tool, BASE / batch / 'result.json'])
        print(completed[-1], flush=True)
    assert digest(manifest.read_bytes()) == scope['currentManifestSHA256']
    save(out / 'state.json', dict(running=False, completed=completed))
    result = dict(uids=UIDS, completed=completed, allCurrentSourceNativesAndFormsRetained=True,
        priorPodiumContactCalculationsRepeated=0, sourceGeometryChanges=0, installationApproved=False,
        physicalAcceptance=False, publication=False, qualification=__doc__ +
        ' Completed prior podium proofs remain separate and unchanged. These newly recovered sources keep every native nomination, corresponding BASIC fallback and foreign current form. No contact exception, support migration or publication approval.')
    save(out / 'summary.json', result)
    module('three_original_companion_neighbour_checks', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'complete-three-original-current-neighbour-follow-through', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        state_path = BASE / BATCH / 'state.json'
        if '--owned' in sys.argv and state_path.exists():
            state = read(state_path)
            state.update(running=False, error=repr(error))
            save(state_path, state)
        raise

"""Private original-E12 bounded burial recovery under the existing 1.2m floor."""
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-alexandra-harbour-glory-e12-clamped-private-terrain-trial-v2-20261101'
CAPTURE = 'government-xl-harbour-glory-alexandra-after-harbour-one-current-v1-20261101-runtime'
TERRAIN = 'government-xl-alexandra247461-current-e12-original-terrain-source-context-v1-20261101'
UIDS = ['landsd/247461:0', 'landsd/35148:0']

def main():
    out = BASE / BATCH
    leasepath = HERE / 'local' / BATCH / 'reservation.json'
    resources = ['building:' + u for u in UIDS] + ['terrain:city/data/terrain.json']
    if '--owned' not in sys.argv:
        assert not out.exists() and not leasepath.parent.exists()
        claim = reservations.claim('alexandra-original-e12-' + str(uuid.uuid4()), resources, batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], leasepath, [sys.executable, __file__, '--owned'])
    lease = read(leasepath)
    assert reservations.owns(lease) and set(lease['resources']) == set(resources)
    refs = [Path(__file__)]
    for name in [CAPTURE, TERRAIN]:
        authenticate(BASE / name)
        refs.append(BASE / name / 'result.json')
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    sha = digest(manifest.read_bytes())
    selection = read(BASE / CAPTURE / 'selection.json.gz')
    assert selection['manifestSHA256'] == sha and {r['uid'] for r in selection['rows']} == set(UIDS)
    refs.extend([manifest, BASE / CAPTURE / 'selection.json.gz'])
    out.mkdir()
    context = BATCH + '-buried-context'
    phases = [
        ('selected_original_buried_context_v1.py', context, ['--runtime', CAPTURE]),
        ('selected_original_clamped_buried_upward_inset_v7_20261026.py', BATCH + '-inset',
         ['--capture', CAPTURE, '--terrain-check', TERRAIN, '--context', context, '--uid', UIDS[0]])]
    completed_phases = []
    for index, (script, batch, args) in enumerate(phases):
        tool = HERE / script
        producer = digest(tool.read_bytes())
        command = [sys.executable, str(tool), '--batch', batch, *args]
        commandfile = out / ('command-' + str(index) + '.json')
        logpath = out / ('phase-' + str(index) + '.log')
        save(commandfile, dict(command=command, producerSHA256=producer))
        assert reservations.owns(lease) and digest(manifest.read_bytes()) == sha
        with logpath.open('w') as log:
            completed = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        assert reservations.owns(lease) and digest(manifest.read_bytes()) == sha and digest(tool.read_bytes()) == producer
        row = dict(batch=batch, script=script, exitCode=completed.returncode)
        refs.extend([tool, commandfile, logpath])
        if completed.returncode == 0:
            receipt, _ = authenticate(BASE / batch)
            row['jobId'] = receipt['jobId']
            refs.append(BASE / batch / 'result.json')
        completed_phases.append(row)
        save(out / 'state.json', dict(running=True, completed=completed_phases))
        if completed.returncode:
            break
    save(out / 'state.json', dict(running=False, completed=completed_phases))
    result = dict(uids=UIDS, completed=completed_phases, sourceGeometryChanges=0, sourcePoseChanges=0,
                  installationApproved=False, publication=False, publicTerrainEdits=False,
                  scriptExternalAICalls=0, historicalE11IdentityUnchanged=True,
                  qualification='Bounded current upward-buried original faces only. Existing 1.2m terrain floor and all final validators retained. No acceptance from producer exit status.')
    save(out / 'summary.json', result)
    module('alexandra_original_e12_trial_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'explicit-private-original-e12-terrain-diagnostic-no-acceptance', list(dict.fromkeys(refs)), result)

if __name__ == '__main__':
    main()

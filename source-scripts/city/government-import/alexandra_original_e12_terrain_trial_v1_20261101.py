"""Private original-E12 terrain trial; no geometry edits or acceptance."""
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-alexandra-harbour-glory-e12-private-terrain-trial-v1-20261101'
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
    tool = HERE / 'selected_original_local_inset_v14_20261029.py'
    producer = digest(tool.read_bytes())
    command = [sys.executable, str(tool), '--batch', BATCH + '-inset', '--capture', CAPTURE,
               '--terrain-check', TERRAIN, '--uid', UIDS[0], '--companion', UIDS[1]]
    save(out / 'command.json', dict(command=command, producerSHA256=producer))
    with (out / 'worker.log').open('w') as log:
        completed = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == sha and digest(tool.read_bytes()) == producer
    result = dict(uids=UIDS, exitCode=completed.returncode, sourceGeometryChanges=0, sourcePoseChanges=0,
                  installationApproved=False, publication=False, publicTerrainEdits=False,
                  scriptExternalAICalls=0, historicalE11IdentityUnchanged=True)
    if completed.returncode == 0:
        receipt, _ = authenticate(BASE / (BATCH + '-inset'))
        result['insetJobId'] = receipt['jobId']
        refs.append(BASE / (BATCH + '-inset') / 'result.json')
    refs.extend([tool, out / 'command.json', out / 'worker.log'])
    save(out / 'summary.json', result)
    module('alexandra_original_e12_trial_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'explicit-private-original-e12-terrain-diagnostic-no-acceptance', refs, result)

if __name__ == '__main__':
    main()

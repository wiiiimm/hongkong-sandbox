"""Persist completed Kwong Fung evidence without installation or rejection credit."""
from pathlib import Path
from run import ROOT, HERE, read, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base = ROOT / 'docs/astra-city/government-import'
    batch = 'government-xl-kwong-fung-scripted-terrain-checkpoint-v1-20261025'
    assert not (base / batch).exists()
    inventory = 'government-xl-after-unnamed276873-unfinished-exact-source-inventory-v1-20261025'
    tally, _ = authenticate(base / inventory)
    assert tally['fixedXLTotal'] == tally['installed'] + tally['unfinished'] == 521
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == tally['currentManifestSHA256']
    phases = []
    refs = [Path(__file__), manifest, base / inventory / 'result.json']
    for folder in sorted(base.glob('government-xl-kwong-fung*-20261025')):
        if (folder / 'result.json').exists():
            receipt, _ = authenticate(folder)
            phases.append(dict(batch=folder.name, jobId=receipt['jobId']))
            refs.append(folder / 'result.json')
    assert len(phases) >= 30
    required = ['government-xl-kwong-fung229834-private-exact-rims-v1-20261025',
                'government-xl-kwong-fung-three-original-private-form-checks-v1-20261025',
                'government-xl-kwong-fung337316-private-compound-clearance-v1-20261025',
                'government-xl-kwong-fung337318-private-compound-clearance-v1-20261025']
    assert set(required) <= {r['batch'] for r in phases}
    podium = read(base / required[0] / 'summary.json')
    assert all(r['passed'] for r in podium['rows'])
    finite = read(base / 'government-xl-kwong-fung-three-original-private-finite-continuous-v1-20261025/summary.json')
    assert all(not r['continuousAffectedFaces'] and not r['wholeSourceUncoveredFaces'] for r in finite['rows'])
    refs += [HERE / 'test_original_basal_cap_junction_context_v1_20261025.py',
             HERE / 'test_original_face_ground_finite_witness_context_v1_20261025.py']
    result = dict(uids=['landsd/229834:0', 'landsd/337316:0', 'landsd/337318:0'],
                  phases=phases, fixedXLTotal=tally['fixedXLTotal'],
                  fixedXLInstalled=tally['installed'], fixedXLUnfinished=tally['unfinished'],
                  officialDetailedActors=tally['currentNativeActors'],
                  sourceReviewApproved=False, physicalAcceptance=False,
                  requiresHumanDecision=False, requiresAIGeometryModelling=False,
                  requiresComputeAndCode=True, allScriptedChecksDone=False,
                  sourceGeometryChanges=0, sourcePoseChanges=0,
                  currentHeldReason='Private original terrain clears podium; exact tower-to-podium source roles, final neighbour/runtime qualification and inspected browser exports remain before guarded installation.',
                  remainingWork=['Bind exact complete H143/93 three-source assembly identity and original basal/wall junction interpretation, retaining all raw failures.',
                                 'Complete final current terrain/neighbour/runtime qualification and source support graph.',
                                 'Inspect fresh desktop/mobile day/night own-source exports before staged approval.',
                                 'Guarded installation, fresh live exports, full prior assets/521-source/BASIC-support readback, commit and push.'],
                  qualification='Completed private evidence only. Three unchanged originals total 22146 faces. Only Block2 belongs to the fixed XL list; Block1 and podium are companion originals. No installation, permanent rejection, optimisation, geometry modelling or approval inferred from this checkpoint. Old floating diagnostic witnesses outside source bounds remain archived; finite fallback preserves actual burial failures.')
    module('kwong_terrain_checkpoint', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch, 'kwong-fung-original-terrain-and-finite-clearance-checkpoint', refs, result)


if __name__ == '__main__':
    main()

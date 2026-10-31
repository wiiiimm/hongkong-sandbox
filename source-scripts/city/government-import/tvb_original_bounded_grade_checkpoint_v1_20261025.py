"""Save private TVB terrain progress and remaining original-role checks in Neon."""
from pathlib import Path
import shutil
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import'
    batch='government-xl-tvb-two-original-bounded-grade-checkpoint-v1-20261025'
    out=base/batch;assert not out.exists()
    tally_name='government-xl-after-kwong-fung-unfinished-exact-source-inventory-v1-20261025'
    tally,_=authenticate(base/tally_name)
    assert tally['installed']==361 and tally['unfinished']==160 and tally['fixedXLTotal']==521
    refs=[Path(__file__),base/tally_name/'result.json'];phases=[]
    for folder in sorted(base.glob('government-xl-tvb*-20261025')):
        if (folder/'result.json').exists():
            r,_=authenticate(folder);refs.append(folder/'result.json')
            phases.append(dict(batch=folder.name,jobId=r['jobId']))
    assert len(phases)>=20
    names={r['batch']for r in phases}
    for name in ['government-xl-tvb-two-original-bounded-grade-form-checks-v1-20261025',
                 'government-xl-tvb-two-original-private-runtime-v2-20261025',
                 'government-xl-tvb-two-original-private-continuous-v2-20261025']:
        assert name in names
    neighbours=read(base/'government-xl-tvb-two-original-bounded-grade-form-checks-v1-20261025/summary.json')
    assert neighbours['forms']==8 and neighbours['flagged']==[] and neighbours['ordinaryFlagged']==0
    continuous=read(base/'government-xl-tvb-two-original-private-continuous-v2-20261025/summary.json')
    assert all(not r['wholeSourceUncoveredFaces'] and not r['continuousAffectedFaces']for r in continuous['rows'])
    failed=base/'government-xl-tvb132578-private-exact-rims-v1-20261025'
    assert not(failed/'result.json').exists()
    out.mkdir();shutil.copyfile('/tmp/xl-tvb132578-private-exact-rims-v1-20261025.log',out/'prior-broad-candidate-132578-rim-failure.log')
    refs += [p for p in failed.rglob('*')if p.is_file()]
    view='government-xl-tvb-two-original-source-views-v1-20261025'
    images=[]
    for filename in ['complete-original-assembly.png','base-only-diagnostic.png']:
        path=base/view/filename;refs.append(path)
        images.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    result=dict(uids=['landsd/9778:0','landsd/132578:0'],phases=phases,
                fixedXLTotal=521,fixedXLInstalled=361,fixedXLUnfinished=160,officialDetailedActors=6924,
                sourceGeometryChanges=0,sourcePoseChanges=0,allScriptedChecksDone=False,
                physicalAcceptance=False,identityAccepted=False,visualAcceptance=False,
                requiresHumanDecision=False,requiresAIGeometryModelling=False,requiresComputeAndCode=True,
                sourceEvidenceReviewPending=True,imagesActuallyViewed=images,
                currentHeldReason='Narrow original-TIN grade fixes actual ground and passes all8 neighbours. Small116-face original still needs fresh rim/source-role interpretation; prior broad-candidate direct rim failure retained. No browser/install credit.',
                nextActions=['Fresh V2 exact coverage/foundations/rims; retain and interpret any original upper-wall boundary probes using exact source evidence, no new global per-component structural requirement.',
                             'Bind exact2-source family identity/whole cells and current source interfaces/foreign contacts without pretending either raw roof-support direction passed.',
                             'Actually inspected original desktop/mobile day/night browser qualification, then guarded installation/full previous-asset+521 readback if all obligations resolve.'],
                observations=['ROOT viewed both source diagrams. They show the mast and a low perimeter/plinth-like component; a diagram alone grants no architectural, identity or structural approval.',
                              'The unrelated OSM actor is way/186639167:0; source current parents are way/186639172. The unrelated actor is retained, not exempted/suppressed as an alias.',
                              'V10 lowering-only proposal did not fix the9m grade gap. Broad authentic TIN fixed source grade but buried a neighbour. V11 full original grade within source projection+1m/3m return resolves the neighbour check with2283 terrain faces/3 parent faces; all original building bytes remain unchanged.'])
    save(out/'summary.json',result)
    module('tvb_grade_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'private-tvb-original-grade-and-retained-neighbour-checkpoint',refs,result)


if __name__=='__main__':main()

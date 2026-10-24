"""Persist current Sung Fung evidence and the next original-podium action."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-next-repairs-sung-fung-court-79098-actionable-hold-v1-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)]
    names=['government-xl-next-repairs-sung-fung-court-79098-four-world-low-face-context-v1-20261024','government-xl-next-repairs-sung-fung-court-79098-complete-height-profile-v1-20261023','government-xl-next-repairs-sung-fung-court-79098-current-diagnostic-browser-v2-20261023','government-xl-next-repairs-sung-fung-court-79098-current-diagnostic-browser-v3-20261023','government-xl-next-repairs-sung-fung-court-79098-model-only-foreign-contacts-v1-20261024','government-xl-next-repairs-beverly-sung-fung-current-model-only-scope-v1-20261024','government-xl-next-repairs-sung-fung-court-79098-unchanged-current-prephysical-v1-20261023']
    receipts={}
    for name in names:
        r,pins=authenticate(base/name);refs.append(base/name/'result.json');receipts[name]=r['jobId']
        for rel,sha in pins.items():
            if rel.startswith(str((base/name).relative_to(ROOT))+'/'):
                path=ROOT/rel;assert digest(path.read_bytes())==sha;refs.append(path)
    result=dict(uids=['landsd/79098:0'],sourceSHA256='4f8072df1732dacc3d0f1624964358fe5d77bacba1a363dc739a15648fd5baaf',status='held-for-scripted-podium-context-and-source-specific-physical-review',heldForCompute=True,heldForHumanDecision=False,aiGeometryModellingRequired=False,permanentRejection=False,installationApproved=False,publication=False,newlyInstalled=0,sourceGeometryChanges=0,sourcePoseChanges=0,relatedCurrentBasicPodiumUid='landsd/45779:0',reasonCodes=['ordinary-whole-source-ground-clearance-fails-on-138-exposed-wall-faces','current-basic-podium-intersection-requires-before-after-and-original-family-context'],evidence=receipts,nextActions=['Compare all four original-world source crossings against existing BASIC tower/podium contacts; retain actual positive foreign contacts.','Recover authentic podium45779 source/family relationship if available; do not suppress or reshape the current podium merely to pass.','Complete bounded source-specific foundation/roof interpretation without transferring diagnostic browser status into approval.','Finish mobile and publication/live gates only after whole-source/assembly physical acceptance.'],rootVisualObservations=['Actually inspected desktop day/night from both private diagnostic angles. First angle foreground basic actor hides lower source; opposite angle exposes more low tower without apparent broad floating slab.','No visual acceptance granted: night source is dark with proceduralWindows false; neighbours remain lit.','Largest source roof areas at120.315m align closely to recorded120.1m; smaller rooftop feature reaches129.665m. Height summary supports investigation but is not independent surveyed validation.'],qualification='All11965faces considered in all4 coordinate worlds. Each world has138 exact below-threshold faces, all near-vertical and with highest original vertex above every overlapping ground face. No wholly buried or upward buried faces. Current basic podium has actual positive contacts, so these facts alone do not authorize installation.')
    save(out/'summary.json',result)
    module('sung_hold_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'sung-fung-current-actionable-podium-context-hold',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()

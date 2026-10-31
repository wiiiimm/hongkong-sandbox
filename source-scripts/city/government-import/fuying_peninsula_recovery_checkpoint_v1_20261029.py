"""Freeze exact original recovery and actionable current holds; no acceptance."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BATCH='government-xl-fuying-peninsula-recovery-checkpoint-v1-20261029'
BASE=ROOT/'docs/astra-city/government-import'

def main():
    out=BASE/BATCH
    assert not out.exists()
    refs=[Path(__file__)]; jobs={}
    names=[
        'government-xl-after-depot120104-native-bounds-v1-20261029',
        'government-xl-fuying-peninsula-after-depot-current-v1-20261029',
        'government-xl-fuying-peninsula-after-depot-cached-terrain-v1-20261029',
        'government-xl-fuying-peninsula-after-depot-terrain-sequence-v1-20261029',
        'government-xl-fuying181489-exact-terrain-budget-v1-20261029',
        'government-xl-fuying181489-convex-core-terrain-v1-20261029',
        'government-xl-fuying181489-native-parent-inset-v1-20261029',
        'government-xl-fuying181489-actual-native-parent-inset-v2-20261029',
        'government-xl-peninsula266543-office-original-lookup-v1-20261029',
        'government-xl-peninsula266543-office-cached-raw-recovery-v1-20261029',
        'government-xl-peninsula266543-office-cached-selection-v1-20261029',
        'government-xl-peninsula-pair-original-selection-v1-20261029',
        'government-xl-peninsula-pair-current-v1-20261029',
        'government-xl-peninsula-pair-finite-contacts-v1-20261029',
        'government-xl-peninsula-pair-four-world-support-v1-20261029',
        'government-xl-peninsula270876-four-world-low-faces-v1-20261029',
        'government-xl-peninsula270876-complete-ground-cap-paths-v1-20261029',
        'government-xl-peninsula-office-rim-attachment-v1-20261029',
        'government-xl-peninsula-office-finite-self-attachment-v2-20261029',
        'government-xl-peninsula-pair-current-foreign-contacts-v1-20261029',
        'government-xl-peninsula266543-office-source-views-v1-20261029',
    ]
    for name in names:
        receipt,pins=authenticate(BASE/name); jobs[name]=receipt['jobId'];refs.append(BASE/name/'result.json')
        for filename in ['summary.json','ROOT-READBACK.json']:
            path=BASE/name/filename
            if path.exists():
                assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
                refs.append(path)
    pair=read(BASE/names[18]/'summary.json')
    assert all(r['witnesses']==r['finiteAttachmentPaths']==164 and r['disconnected']==0 and r['pathsWithinEndpointHeight']==136 for r in pair['rows'])
    caps=read(BASE/names[16]/'summary.json');assert caps['allFourCompleteGroundClearCapPaths']
    parentpath=ROOT/'3d-viewer/city/data/government-native-fu-wong-original-v1-20261023.json';parent=read(parentpath);refs.append(parentpath)
    assert parent.get('nativeMesh') and not parent.get('patches')
    retained=sorted(parent['meta']['targetUids'])
    result=dict(uids=['landsd/181489:0','landsd/270876:0','landsd/266543:0'],status='held-for-further-source-bound-compute-and-interpretation',
        heldForHumanDecision=False,heldForCompute=True,aiGeometryModellingRequired=False,permanentRejection=False,
        installationApproved=False,publication=False,newlyInstalled=0,sourceGeometryChanges=0,sourcePoseChanges=0,
        fixedXL=dict(total=521,installed=404,exactCurrentSourceTerminal=3,outstanding=114),currentDetailedActors=7019,
        evidence=jobs,rows=[dict(uid='landsd/181489:0',reason='Current ground has105 buried/36 upward-buried facets. Correct parent is existing native Fu Wong, not root. Native-child proposal39,484faces fails25k budget; preserving actual captured parent instead of synthetic grid return fails ordinary parent-edge join. Native meshes also cannot directly contain nested overrides under current validator.',
            retainedParent=dict(path=str(parentpath.relative_to(ROOT)),sha256=digest(parentpath.read_bytes()),targetUids=retained),
            nextAction='Plan explicit original-parent replacement/composition preserving every retained target, original boundary and actual drawn parent facets. Do not append an overlapping root patch, install an invalid nested native child, relax budgets, or repeat unchanged failed constructors.'),
        dict(uid='landsd/270876:0',reason='All189 negative source facets have complete original clear-cap paths in all4 representations, with zero negative non-wall faces. This is topology evidence, not wall-role or identity approval. Raw current2D Tower/native Podium classification mismatch retained.',
            nextAction='Review exact hotel body/tower roles and lower facade context, then qualify current foreign contacts, exact source and placement before any browser/publication step.'),
        dict(uid='landsd/266543:0',reason='Exact indexed70,838byte original recovered locally with pinned4c40dd79 SHA and2872faces. All164 strict-support warnings now have positive finite self-join paths to hotel in all4worlds;136 pass endpoint height,28 fail by0.00000095367431640625 to0.21595001220703125m. No detached components remain under exact self-contact accounting; raw strict failures preserved.',
            nextAction='Inspect complete28 remaining path-height witnesses and authored lower facade/closure roles. Do not promote contact connectivity to structural support or waive endpoint height globally. Any installation needs exact coordinated activation/fallback and both originals verified.')],
        scriptExternalAICalls=0,aiGeometryModelling=False,qualification='Evidence checkpoint only. Original bytes/pose/terrain/catalogues unchanged. All521 source keys including both NULL-UID keys remain in scope. Neither diagnostic failures nor pending physical interpretation establish permanent non-installability.')
    save(out/'summary.json',result)
    module('fuying_peninsula_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-cache-recovery-current-contact-and-native-parent-actionable-holds',refs,result)
    print(dict(status=result['status'],jobs=len(jobs),newlyInstalled=0))

if __name__=='__main__':main()

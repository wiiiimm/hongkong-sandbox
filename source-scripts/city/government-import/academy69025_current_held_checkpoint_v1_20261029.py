"""Save exact Academy blockers and completed work for continued scripted recovery."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-academy69025-current-held-checkpoint-v1-20261029'
def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];inputs={}
    records={
      'identity':('government-xl-academy69025-after-fortune-current-v2-20261029-identity','69025:0/identity.json'),
      'terrain':('government-xl-academy69025-complete-tin-current-v1-20261029-69025-0-inset','summary.json'),
      'foundations':('government-xl-academy69025-complete-tin-current-v1-20261029-69025-0-foundations','summary.json'),
      'scope':('government-xl-academy69025-complete-tin-current-v1-20261029-69025-0-scope','scope.json'),
      'rims':('government-xl-academy69025-tin-raw-rims-v1-20261029','summary.json'),
      'lowFaces':('government-xl-academy69025-tin-low-faces-v1-20261029','summary.json'),
      'nativeContacts':('government-xl-academy69025-current-native-contacts-v1-20261029','summary.json'),
      'nativeRoles':('government-xl-academy69025-current-native-roles-v1-20261029','summary.json'),
      'nativeLineage':('government-xl-academy69025-current-native-lineage-v1-20261029','summary.json'),
      'floorDomain':('government-xl-academy69025-floor-domain-diagnostic-v1-20261029','summary.json'),
      'identityViews':('government-xl-academy69025-current-identity-views-v1-20261029','summary.json'),
      'nativeViews':('government-xl-academy69025-current-native-contact-views-v1-20261029','summary.json')}
    data={}
    for key,(batch,name)in records.items():
        receipt,pins=authenticate(BASE/batch);p=BASE/batch/name
        assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([BASE/batch/'result.json',p]);data[key]=read(p)
        inputs[key]=dict(batch=batch,jobId=receipt['jobId'],path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    assert not data['identity']['passed']and not data['foundations']['establishedFoundationPolicyPassed']
    assert data['floorDomain']['missingSetEmpty']is False and data['floorDomain']['sourceFaces']==[2471,2472,2473,2474,2485,2486]
    images=[BASE/records['identityViews'][0]/n for n in ['whole-source-plan.png','whole-source-perspectives.png']]+[BASE/records['nativeViews'][0]/'337830:0-native-contact-context.png'];refs.extend(images)
    result=dict(uids=['landsd/69025:0'],sourceSHA256='75d1193ec409e8522705df1f262f647e12beda5c4e309f9905ca8ba7e5e88414',humanStatus='held for further scripted processing and source-evidence review',humanDecisionRequired=False,aiGeometryRequired=False,permanentRejection=False,installationApproved=False,publication=False,inputs=inputs,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,imagesActuallyViewed=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],heldReasons=[dict(reason='Source extent needs bounded original-feature interpretation',rawReasons=data['identity']['reasons'],observed='Original mesh includes exterior spiral stair and curved plaza feature beyond the target footprint; exact metadata routing passes and no unrelated BASIC overlap is reported. This observation grants no identity or placement acceptance.'),dict(reason='Original source junction needs review',nativeUid='landsd/337830:0',finitePairsPerWorld=148,positiveSurfacePairsPerWorld=144,transversePairsPerWorld=142,observed='All represented transverse pairs trace to transverse pairs present in unchanged originals. No source/native move or Boolean edit is authorised; source relationship, fallback and collision checks remain.'),dict(reason='Terrain correction incomplete',terrainFaces=data['terrain']['terrainTriangles'],fourWorldBuriedUpwardFaces=3,allFourWorldAffectedLowFaces=221,upwardNomination=[2471,2472,2473,2474,2485,2486],missingDomainAreaM2=data['floorDomain']['missingAreaM2'],observed='Bounded six-facet floor return fails strict domain coverage. Both world and local-origin representations preserve the gap; do not waive coverage or rerun unchanged.'),dict(reason='Retained scene terrain and neighbours require explicit composition',terrainContacts=data['scope']['terrainContacts'],touchingNativeUids=data['scope']['touchingNativeUids'],observed='Generic sequence defers neighbour work when an existing terrain is nominated. Explicit existing-terrain retention plus both native regressions remain mandatory.')],nextActions=['Repair or prove a genuinely covered derived terrain domain with all original guard checks intact.','Recheck final original foundations/rims and retained neighbours after terrain changes.','Bind a narrow original-feature identity/junction interpretation to exact current source bytes; retain all raw failures.','Run full private desktop/mobile/fallback/collision gates before guarded installation.'])
    save(out/'held-reasons.json',result)
    module('academy_held_checkpoint_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-current-academy-original-held-reasons-and-scripted-recovery-checkpoint',refs,result)
if __name__=='__main__':main()

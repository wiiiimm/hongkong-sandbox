"""Approve only an exact private source/canopy visibility experiment."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-unnamed265269-private-canopy-review-v2-20261029';UID='landsd/265269:0';BASIC='landsd/265270:0';SOURCE='0adf753f5832d3598fd1d99c3700b704e33de74aa97c4d4f868ba68c6cb445da'
def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,p):
        if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    feature='government-xl-unnamed265269-canopy-primary-feature-packet-v2-20261029';f=take(feature,BASE/feature/'summary.json');assert (f['sourceUid'],f['basicUid'],f['sourceSHA256'])==(UID,BASIC,SOURCE)
    b=f['currentForms'][BASIC];official=f['officialRecords'][BASIC];assert b['baseHeightHKPD']is None and b['topHeightHKPD']is None and b['heightSource']=='estimated'and official['BaseHeight']is None and official['TopHeight']is None and official['BuildingBlockType']=='Open-sided Structure'and official['Status']=='Active'
    coverage='government-xl-unnamed265269-canopy-roof-post-coverage-v1-20261029';c=take(coverage,BASE/coverage/'summary.json');assert c['sourceSHA256']==SOURCE and len(c['rows'])==4
    interface='government-xl-unnamed265269-canopy-interface-views-v1-20261029';take(interface,BASE/interface/'summary.json')
    images=[BASE/feature/'original-roof-current-official-canopy.png',BASE/interface/'full-height.png',BASE/interface/'original-height.png']
    for image in images:
        batch=feature if image.parent.name==feature else interface
        assert digest(image.read_bytes())==pins[batch][str(image.relative_to(ROOT))];refs.append(image)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest)
    rebind='government-xl-unnamed265269-exact-current-grade-rebind-v1-20261029';same=take(rebind,BASE/rebind/'summary.json');assert same['sourceSHA256']==SOURCE and same['sourceWorldArraysExactlyUnchanged']and same['completeDrawnGroundArraysExactlyUnchanged']and same['currentManifestSHA256']==digest(manifest.read_bytes())
    scope='government-xl-unnamed265269-after-academy-current-v1-20261029-model-scope';rows=take(scope,BASE/scope/'265269:0-forms.json.gz');current={r['building']['uid']:r['building']for r in rows};assert current[BASIC]==b and current[UID]==f['currentForms'][UID]
    for row in rows:
        if row['building']['uid']not in [UID,BASIC]:continue
        path=ROOT/'3d-viewer'/row['tile'];assert digest(path.read_bytes())==row['tileSHA256'];assert next(q for q in read(path)['buildings']if q['uid']==row['building']['uid'])==row['building'];refs.append(path)
    result=dict(uids=[UID],sourceUid=UID,basicUid=BASIC,sourceSHA256=SOURCE,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),exactBasicForm=b,officialCanopyRecord=official,imagesActuallyViewed=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],coverageRowsVerbatim=c['rows'],nativeRoofComponentsVerbatim=f['originalRoofComponents'],reviewer='ROOT',privateCanopyExperimentApproved=True,coveragePercentageNotAnApprovalRule=True,sourceIdentityApproved=False,physicalAcceptance=False,collisionReviewApproved=False,visualAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,basicGeometryChanges=0,aiGeometryModelling=False,evidenceInterpretationUsedAI=True,proposedSuppression=dict(ownerUid=UID,sourceSHA256=SOURCE,suppressesBuildingUids=[BASIC],onlyWhileExactOwnerActive=True),requiredNextChecks=['Actual desktop/mobile day/night source appearance and canopy visibility.','Actual failure/retry, Base-only and eviction restore the unchanged BASIC canopy.','Resolve all original identity/extent, canonical grade and current-neighbour/collision evidence before installation.'],basis=['The actual original has the repeated higher roof bays and complete authored columns at this registered canopy footprint; the estimated BASIC is a lower overlapping illustration. Fresh active official canopy record has no surveyed base/top. Exact original roof components, fresh official outline and current outline are preserved independently.','This is a bounded feature-correspondence judgement for a private visibility test, following the existing Sha Tin conditional-replacement approach. Raw roof shortfall and illustrative post-cap shortfall remain verbatim and are not declared geometrically covered or structurally supported. No source roof/post is raised, rescaled, clipped or remodelled.','Only this exact BASIC canopy may be hidden in a temporary catalogue while this exact original is active. Full unchanged fallback restoration remains mandatory. This decision does not approve the whole model identity/placement, collision, physical support, publication or as-built/cadastral accuracy.'])
    save(out/'ROOT-PRIVATE-CANOPY-REVIEW.json',result)
    module('private_canopy_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-exact-source-canopy-correspondence-private-experiment-only',refs,result)
if __name__=='__main__':main()

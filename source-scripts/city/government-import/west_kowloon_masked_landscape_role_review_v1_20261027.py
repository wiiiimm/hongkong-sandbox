"""Bound the reviewed35 original auxiliary landscape bases; no model acceptance."""
from pathlib import Path
from fractions import Fraction
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-west-kowloon-north-masked-landscape-role-review-v1-20261027';out=base/batch;assert not out.exists()
    name='government-xl-west-kowloon-north-landscape-base-context-v1-20261027';_,pins=authenticate(base/name);path=base/name/'summary.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];context=read(path)
    assert context['uids']==['landsd/182397:0'] and context['sourceSHA256']=='f16aa7f57a9b89962a6e1f3183e4dea922c7dbcb173515e608deae1ddc4b48b1'
    rows=context['warningRows'];ids=sorted(r['sourceFace']for r in rows);assert len(ids)==len(set(ids))==35
    assert context['allWarningFacetsStrictlyOutsideCoreFootprint'] and context['allWarningFacetsCompletelyMaskedByOriginalTerrain']
    assert all(any(g>0 for g in r['strictCoreFootprintSeparatingAxisGapsM']) and r['entireFacetStrictlyBelowEveryOverlappingOriginalTerrainFacet'] and Fraction(r['exactMaximumSourceMinusOriginalTerrainM'])<0 for r in rows)
    assert len(context['exactSharedEdgeComponentContext'])==1
    component=context['exactSharedEdgeComponentContext'][0];assert sorted(component['warningFacesInComponent'])==ids
    native=component['representative'];assert native['wholeSharedEdgeComponentFaces']==526 and set(ids)<=set(native['componentFaceIds'])
    assert native['componentBounds'][1][1]<10
    assert len(context['rootActuallyViewedPhotos'])==len(context['rootActuallyViewedOriginalTINExports'])==3
    refs=[Path(__file__),base/name/'result.json',path]
    for r in context['rootActuallyViewedPhotos']+context['rootActuallyViewedOriginalTINExports']:
        p=ROOT/r['path'];assert digest(p.read_bytes())==r['sha256'];refs.append(p)
    result=dict(uids=context['uids'],sourceSHA256=context['sourceSHA256'],sourceWorldSHA256=context['sourceWorldSHA256'],originalTerrainSHA256=context['originalTerrainSHA256'],reviewedSourceFaces=ids,sourceRoleAccepted=True,acceptedRole='original auxiliary landscape-base surfaces masked by authentic government terrain',sourceSpecificRoleOnly=True,wholeLandscapeComponentFaces=native['componentFaceIds'],interpretation='All35 warnings lie outside the tower footprint, within the separate low526-face shared-edge forecourt component. Complete finite-column checks prove all35 remain below every overlapping original-TIN face. The whole-source plan and official entrance/landscape photographs identify this as the flagpole/landscape forecourt, rather than the tower core. Retain the unedited auxiliary bases beneath the matching original ground; do not excavate terrain merely to expose them. No specific basement, room or survey height is inferred from photographs.',requiredBeforeAnyInstallation=dict(exactSameSourceSHAAndReviewedFaceIds=True,currentFourWorldMaskedAuxiliaryRevalidation=True,currentFourWorldCoreFoundationChecks=True,allOtherSourceFacesRetainOrdinaryFoundationPolicy=True,sourceIdentityAcceptance=True,allCurrentBasicAndRetainedNativeChecks=True,actualDesktopMobileAndFailureRetry=True,guardedPublicationAndIndependentReadback=True),sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,terrainGeometryChanges=0,rawFoundationWarningsChanged=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Bounded source-role acceptance for these exact35 original auxiliary landscape-base facets only. Does not alter general foundation policy or approve the whole model, terrain candidate, contacts, support, current renderer, visibility or publication. It cannot transfer to changed source bytes, changed face IDs or a different current four-world terrain result.')
    save(out/'ROOT-SOURCE-ROLE-REVIEW.json',result);save(out/'summary.json',result)
    module('masked_landscape_role_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-original-masked-auxiliary-landscape-base-role-review',refs,result)
    print(dict(reviewedFaces=len(ids),sourceSpecificRoleAccepted=True,physicalAcceptance=False),flush=True)

if __name__=='__main__':main()

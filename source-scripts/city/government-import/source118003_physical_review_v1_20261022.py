"""Bind exact source118003 official-structure identity to complete physical evidence.

Independent terrain-supported originals only. This changes no automatic guard or
source geometry. Only the named related record already proved by the dedicated official-structure
identity receipt is interpreted. No generic identity or physical gate changes.
"""
import argparse
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
PERMITTED={'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage','fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent'}


def validate_decision_binding(raw,decision):
    assert decision['reviewer']=='ROOT' and decision['sourceIdentityInterpretationApproved'] is True
    assert decision['uid']=='landsd/118003:0'
    assert decision['sourceSHA256']=='f3d9ed0d2750849db16427133f0c09c441a01d8a5ef1f3c9c8e26dbf6f1a96e0'
    for key in ['uid','sourceSHA256','sourceFormSHA256','worldTrianglesSHA256']:
        assert raw[key]==decision[key]
    assert not raw['passed'] and set(raw['reasons'])==set(decision['expectedRawReasons'])
    assert set(raw['reasons'])=={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage','full-source-unrelated-overlap'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--decision',required=True);a=p.parse_args()
    assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;assert not doc.exists()
    decisionpath=ROOT/a.decision;decision=read(decisionpath);uid=decision['uid'];sha=decision['sourceSHA256'];count=decision['completeSourceFaces'];names=decision['evidenceBatches']
    refs=[Path(__file__),decisionpath];cache={}
    for key,name in names.items():
        assert name.startswith('government-xl-')and '/'not in name
        cache[key]=authenticate(base/name)[1];refs.append(base/name/'result.json')
    def take(key,filename):
        path=base/names[key]/filename;assert digest(path.read_bytes())==cache[key][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    raw=take('identity',uid.split('/')[1]+'/identity.json');validate_decision_binding(raw,decision)
    assert raw['originalOwnership']['sourceGraphVerified'] and raw['originalOwnership']['originalRootName']==decision['modelId']
    assert raw['exactCurrentComponentRoute']['qualified'] and raw['exactCurrentComponentRoute']['uid']==uid
    assert raw['exactWholeCellCoverage']['covered'] and raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==count
    context=take('identity',uid.split('/')[1]+'/context.json')['identity']
    named=take('namedIdentity','identity.json')
    assert named['identityAccepted'] and named['sourceSpecificIdentityRecomputed'] and named['rawIdentityVerbatim']==raw
    assert named['uid']==uid and named['sourceSHA256']==sha and named['relatedUID']=='landsd/118128:0' and named['officialStructureID']==1645937
    assert named['currentFormSuppression'] is False and named['currentCollisionExemption'] is False and named['currentTerrainExemption'] is False
    assert context['unrelatedIntersectingForms']==1
    assert {r['uid'] for r in context['intersectingForms'] if not r['sameParent']}=={'landsd/118128:0'}
    assert named['allCurrentFormsRetained']==take('scope','form-obligations.json.gz')
    plots=take('plots','summary.json');assert plots['sourceSHA256']==sha and plots['completeSourceFaces']==count and plots['originalWorldSHA256']==raw['worldTrianglesSHA256']
    expected={str((base/names['plots']/f).relative_to(ROOT))for f in ['whole-source-plan.png','whole-source-perspectives.png']}
    assert len(decision['imagesActuallyViewed'])==2 and {r['path']for r in decision['imagesActuallyViewed']}==expected
    for image in decision['imagesActuallyViewed']:
        path=ROOT/image['path'];assert digest(path.read_bytes())==image['sha256']==cache['plots'][image['path']];refs.append(path)
    boundary=take('boundary','summary.json');assert boundary['sourceSHA256']==sha and boundary['originalWorldSHA256']==raw['worldTrianglesSHA256']
    assert boundary['identityApproved']is False and boundary['installationApproved']is False
    foundations=take('foundations','summary.json')['rows'];assert {r['mode']for r in foundations}=={'original','literal','explicitLeftF32','explicitBalancedF32'}
    assert all(r['uid']==uid and r['triangles']==r['completeTerrainTriangles']==count and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in foundations)
    scope=take('scope','scope.json');assert scope['currentNativeActors']==decision['currentNativeActors'] and not scope['touchingNativeUids'] and scope['positiveAreaTerrainOverlaps']==0
    neighbours=take('neighbours','summary.json');assert neighbours['forms']==scope['intersectingForms']==decision['neighbourForms'] and not neighbours['basicFlags'] and not neighbours['requiredNativeUids'] and not neighbours['nativeRows'] and not neighbours['nativeResolved']
    rims=take('rims','summary.json')['rows']
    assert {r['mode'] for r in rims}=={'original','literal','explicitLeftF32','explicitBalancedF32'} and len(rims)==4
    assert all(r['passed'] and r['completeSourceFaces']==count and r['minimumSampleGapM']>=-.5 and r['minimumRimGapM']<=.1 and r['maximumRimGapM']<=1 for r in rims)
    metrics=take('runtime','metrics.json');metric=next(r for r in metrics['rows']if r['uid']==uid)
    proof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True)
    policy=module('selected_review_policy',HERE/'acceptance-policy.py')
    assert not policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=sha,identityProof=proof),metric,metrics['profiles']['mobile'])
    assert metric['missingTerrain']==0 and metric['maxSamplerDelta']<=.004
    selected=take('runtime','selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selected['rows']}=={uid:sha}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    interpreted=deepcopy(raw);interpreted.update(passed=True,reasons=[],proof=proof,rawIdentityVerbatim=deepcopy(raw),sourceIdentityReviewUsedAI=True,physicalAccepted=False,installationApproved=False,sourceSpecificIdentityDecision=decision)
    result=dict(uids=[uid],sourceSHA256ByUid={uid:sha},sourceSpecificPhysicalInterpretationAccepted=True,sourceIdentityAssemblyQualified=True,sourceSpecificBoundaryInterpretationAccepted=True,identityProof=proof,currentManifestSHA256=selected['manifestSHA256'],imagesActuallyViewed=decision['imagesActuallyViewed'],reviewer='ROOT',identityOnlyReviewUsedAI=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,completeFourWorldFoundations=True,completeCurrentNeighbourChecks=neighbours['forms'],rawIdentityReasonsRetained=raw['reasons'],sourceSpecificIdentityInterpretation=decision['interpretation'],installationApproved=False,publication=False,qualification='Exact-source interpretation only; automatic coverage/extent tests remain unchanged and raw failures retained. Strict current contact/runtime, all four complete foundations and all current neighbours pass. Browser, picking/collision, failure/retry and guarded publication remain required.')
    save(doc/'ROOT-PHYSICAL-REVIEW.json',result);save(doc/'reviewed-identity.json',interpreted);save(doc/'expected-raw-identity.json',raw)
    refs.extend([HERE/'acceptance-policy.py',HERE/'selected_original_identity_v2.py'])
    module('selected_physical_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-selected-original-boundary-physical-review',refs,result)


if __name__=='__main__':main()

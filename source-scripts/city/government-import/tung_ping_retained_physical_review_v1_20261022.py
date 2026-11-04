"""Bind existing exact named TungPing/BlockF record identity to full current physical checks.

Case-specific adapter only: no generic unrelated-form exception. Named provider,
complete source and exact-interface proofs must be freshly recomputed and pinned.
All ordinary physical, four-world and native-neighbour guards remain unchanged.
"""
import argparse
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
PERMITTED={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}


def validate_decision_binding(raw,decision):
    assert decision['reviewer']=='ROOT' and decision['sourceIdentityInterpretationApproved']is True
    for key in ['uid','sourceSHA256','sourceFormSHA256','worldTrianglesSHA256']:
        assert raw[key]==decision[key], 'Exact reviewed source/form/world changed'
    assert raw['passed']is False and set(raw['reasons'])==set(decision['expectedRawReasons'])
    assert raw['uid']=='landsd/97301:0' and raw['sourceSHA256']=='1401822634163c71c14b23c87791896c3e78d13d7362b112fc693eb19c94458d'
    assert set(raw['reasons'])==PERMITTED, 'Only exact named TungPing/BlockF identity is supported'


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
    for key in ['uid','sourceSHA256','sourceFormSHA256','worldTrianglesSHA256']:assert named[key]==raw[key]
    assert named['passed'] and not named['reasons'] and named['sourceSpecificIdentityRecomputed'] and named['currentNativeSourceVersionsReadBack']
    assert named['historicalManifestApprovalTransferred'] is False
    assert named['currentManifestSHA256']==raw['exactRouteManifestSHA256']
    assert named['relatedUID']=='landsd/97300:0'and named['relatedSourceSHA256']=='ab0ddef30aa0ea08b5bc7f86db9eb10c90924d753fcff909a0500ad123a21dea'
    assert count==11443 and named['currentFormSuppression'] is False
    assert named['currentCollisionExemption'] is False and named['currentTerrainExemption'] is False
    assert set(named['onlyNamedRelatedReasonsReplaced'])==set(raw['reasons'])==PERMITTED
    assert {r['uid']for r in named['sourceRecords']}=={uid,named['relatedUID']}
    assert {r['buildingCSUID']for r in named['sourceRecords']}=={'3427311446T20050430','3426211455T20050430'}
    forms=take('scope','form-obligations.json.gz')
    assert named['allCurrentFormsRetained']==forms
    streams=take('namedIdentity','complete-original-streams.json.gz')
    assert streams[uid]['compressedSHA256']==sha and streams[named['relatedUID']]['compressedSHA256']==named['relatedSourceSHA256']
    plots=take('plots','summary.json');assert plots['sourceSHA256']==sha and plots['completeSourceFaces']==count and plots['originalWorldSHA256']==raw['worldTrianglesSHA256']
    expected={str((base/names['plots']/f).relative_to(ROOT))for f in ['whole-source-plan.png','whole-source-perspectives.png']}
    assert len(decision['imagesActuallyViewed'])==2 and {r['path']for r in decision['imagesActuallyViewed']}==expected
    for image in decision['imagesActuallyViewed']:
        path=ROOT/image['path'];assert digest(path.read_bytes())==image['sha256']==cache['plots'][image['path']];refs.append(path)
    boundary=take('boundary','summary.json');assert boundary['sourceSHA256']==sha and boundary['originalWorldSHA256']==raw['worldTrianglesSHA256']
    assert boundary['identityApproved']is False and boundary['installationApproved']is False
    foundations=take('foundations','summary.json')['rows'];assert {r['mode']for r in foundations}=={'original','literal','explicitLeftF32','explicitBalancedF32'}
    assert all(r['uid']==uid and r['triangles']==r['completeTerrainTriangles']==count and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in foundations)
    scope=take('scope','scope.json');assert scope['currentNativeActors']==decision['currentNativeActors']
    patch=take('patch','summary.json');assert patch['status']=='private-terrain-validator-passed'
    replacement=patch['candidate']['replaces'];oldpath=ROOT/'3d-viewer'/replacement['url']
    assert digest(oldpath.read_bytes())==replacement['sha256'];refs.append(oldpath)
    assert set(read(oldpath)['meta']['targetUids'])==set(replacement['retainedUids'])
    contacts=[x for x in scope['terrainContacts'] if x['coarseOverlapAreaM2']>0 or any(p['overlapAreaM2']>0 for p in x['packedContacts'])]
    assert len(contacts)==scope['positiveAreaTerrainOverlaps']==1 and contacts[0]['url']==replacement['url']
    candidatepath=ROOT/patch['candidate']['path'];assert digest(candidatepath.read_bytes())==patch['candidate']['sha256'];refs.append(candidatepath)
    assert set(read(candidatepath)['meta']['targetUids'])==set(replacement['retainedUids'])|{uid}
    neighbours=take('neighbours','summary.json')
    assert neighbours['forms']==scope['intersectingForms']==decision['neighbourForms'] and not neighbours['basicFlags']
    ordinary=take('neighbours','neighbour-checks.json')
    flagged=[r for r in ordinary['rows'] if r['reasons']]
    assert len(ordinary['rows'])==neighbours['forms'] and not any(r['reasons'] for r in ordinary['rows'] if not r['existingNative'])
    native=take('nativeNeighbours','summary.json')
    required=set(scope['touchingNativeUids'])|set(replacement['retainedUids'])
    assert required and required==set(native['requiredNativeUids'])==set(native['nativeResolved'])
    assert native['forms']==neighbours['forms'] and not native['basicFlags']
    assert {r['uid'] for r in native['nativeRows']}==required
    assert all(r['passed'] and r['triangles']>0 and r['terrain']['newlyWhollyBuried']==r['terrain']['newlyUpwardWhollyBuried']==0 for r in native['nativeRows'])
    assert {r['uid'] for r in flagged}<=required
    assert all(r['existingNative'] and r['reasons']==['existing-native-neighbour-requires-full-mesh-check'] for r in flagged)
    rims=take('strictRims','summary.json')
    assert rims['sourceSHA256']==sha and {r['mode'] for r in rims['rows']}=={'original','literal','leftF32','balancedF32'}
    assert all(r['passed'] and r['completeSourceFaces']==count for r in rims['rows'])
    metrics=take('runtime','metrics.json');metric=next(r for r in metrics['rows']if r['uid']==uid)
    proof=deepcopy(named['proof']);assert all(proof[k]for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted'])
    policy=module('selected_review_policy',HERE/'acceptance-policy.py')
    assert not policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=sha,identityProof=proof),metric,metrics['profiles']['mobile'])
    assert metric['missingTerrain']==0 and metric['maxSamplerDelta']<=.004
    selected=take('runtime','selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selected['rows']}=={uid:sha}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256']==named['currentManifestSHA256'];refs.append(manifest)
    interpreted=deepcopy(raw);interpreted.update(passed=True,reasons=[],proof=proof,rawIdentityVerbatim=deepcopy(raw),sourceIdentityReviewUsedAI=True,physicalAccepted=False,installationApproved=False,sourceSpecificIdentityDecision=decision)
    result=dict(uids=[uid],sourceSHA256ByUid={uid:sha},sourceSpecificPhysicalInterpretationAccepted=True,sourceIdentityAssemblyQualified=True,sourceSpecificBoundaryInterpretationAccepted=True,identityProof=proof,currentManifestSHA256=selected['manifestSHA256'],imagesActuallyViewed=decision['imagesActuallyViewed'],reviewer='ROOT',identityOnlyReviewUsedAI=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,completeFourWorldFoundations=True,completeCurrentNeighbourChecks=neighbours['forms'],exactTerrainReplacement=replacement,retainedNativeRegression=native,completeStrictFourWorldRims=rims,rawIdentityReasonsRetained=raw['reasons'],sourceSpecificIdentityInterpretation=decision['interpretation'],installationApproved=False,publication=False,qualification='Exact named TungPing/BlockF identity bound to current original sources; raw approximate identity failures retained. Strict current contact/runtime, all four complete foundations and all current neighbours pass. Browser, picking/collision, failure/retry and guarded publication remain required.')
    save(doc/'ROOT-PHYSICAL-REVIEW.json',result);save(doc/'reviewed-identity.json',interpreted);save(doc/'expected-raw-identity.json',raw)
    refs.extend([HERE/'acceptance-policy.py',HERE/'selected_original_identity_v2.py',HERE/'selected_original_retained_physical_review_v1.py',HERE/'tung_ping_related_record_identity_v3_20261022.py'])
    module('selected_physical_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-tung-ping-block-f-retained-physical-review',refs,result)


if __name__=='__main__':main()

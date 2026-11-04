"""Bound exact exposed University Hall wall/ground interpretation to current inputs."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-next-repairs-university-hall-93417-';batch=prefix+'physical-review-v1-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,f):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        path=base/n/f;assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    runtime=prefix+'runtime-v1-20261023';selection=take(runtime,'selection.json.gz');assert len(selection['rows'])==1;row=selection['rows'][0];uid=row['uid'];assert uid=='landsd/93417:0';sha=row['sourceSHA256'];assert sha=='debfebe52c8a04231cd20bdbfeaa9057f28af6e9df054769f9c57118f4d5aa60'
    metric_data=take(runtime,'metrics.json');metric=metric_data['rows'][0]
    for p,h in metric_data['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    identity=take(prefix+'identity-v1-20261023','93417:0/identity.json');assert identity['passed'] and not identity['reasons'] and identity['sourceSHA256']==sha and identity['exactRouteManifestSHA256']==selection['manifestSHA256']
    assert all(identity['proof'][k] for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted'])
    policy=module('university_actual_policy',HERE/'acceptance-policy.py');reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=sha,identityProof=identity['proof']),metric,metric_data['profiles']['mobile']);assert reasons==['terrain-intersects-source-over-0.5m'];assert metric['maxLowGap']<1 and metric['minLowGap']<.1 and metric['missingTerrain']==0 and metric['maxSamplerDelta']<.004
    pre=prefix+'current-prephysical-v1-20261024';foundation=take(pre+'-foundations','summary.json')['rows'];assert len(foundation)==4 and all(r['triangles']==r['completeTerrainTriangles']==14777 and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in foundation)
    low=take(prefix+'four-world-low-faces-v1-20261024','summary.json');ids=[7568,7569,7634,7635,8019,8020,8095,8096,14474,14475,14476,14477,14478,14479];assert low['sourceSHA256']==sha and len(low['rows'])==4
    assert all(r['exactAffectedFaces']==ids and r['allAffectedWallLike'] and r['allAffectedHaveExposedHighestVertex']for r in low['rows'])
    caps=take(prefix+'four-world-cap-equivalence-v1-20261024','summary.json');assert caps['sourceSHA256']==sha and caps['allFourExactArrayEquivalent'] and caps['allFourAffectedHaveClearCapPaths'];assert caps['literalClearCapProof']['affectedOriginalWallFaces']==ids and not caps['literalClearCapProof']['rawExposureFailures']
    grade=take(prefix+'four-world-wall-grade-v1-20261024','summary.json');assert grade['sourceSHA256']==sha and len(grade['rows'])==4 and all(r['namedFaces']==ids and r['positiveFiniteInterfaces']==15 for r in grade['rows'])
    comparison=take(prefix+'source-current-wall-comparison-v1-20261024','summary.json');assert comparison['comparedFaces']==14 and comparison['originalTerrainBelowLimitFaces']==2 and comparison['currentTerrainBelowLimitFaces']==14
    scope_name=prefix+'current-model-scope-v1-20261024';scope=take(scope_name,'summary.json');assert len(scope['rows'])==1 and scope['rows'][0]['currentNativeActorsChecked']==6863 and not scope['rows'][0]['nearbyNativeActors']
    forms=take(scope_name,'93417:0-forms.json.gz');assert len(forms)==2
    foreign=take(prefix+'current-foreign-contacts-v1-20261024','summary.json');assert foreign['foreignPairs']==1 and foreign['rows'][0]['foreignUid']=='landsd/121501:0' and all(m['positiveContactPairs']==0 and m['projectedOverlapAreaM2']==0 for r in foreign['rows']for m in r['modes'])
    view_name=prefix+'wall-source-views-v3-20261024';views=take(view_name,'summary.json');assert views['allFourteenAffectedFacesShown'] and views['sourceSHA256']==sha;images=[]
    for r in views['regions']:
        path=ROOT/r['image'];assert digest(path.read_bytes())==r['imageSHA256']==pins[view_name][str(path.relative_to(ROOT))];refs.append(path);images.append(dict(path=str(path.relative_to(ROOT)),sha256=r['imageSHA256']))
    assert len(images)==2
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==scope['currentManifestSHA256'];refs.append(manifest)
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==sha;refs.append(asset)
    result=dict(uids=[uid],sourceSHA256ByUid={uid:sha},reviewer='Codex ROOT',sourceSpecificPhysicalInterpretationAccepted=True,identityAccepted=True,completeNeighbourInterpretationAccepted=True,qualifiedFourWorldSourceClearance=True,rawFourWorldSourceClearancePassed=False,rawPolicyReasons=[dict(uid=uid,reasons=reasons)],rawCanonicalFailuresPreserved=True,qualifiedExposedOriginalWallFaces=ids,identityProof=identity['proof'],identityProofByUid={uid:identity['proof']},completeCurrentNeighbourChecks=2,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),retainedCurrentBasicSupportUids=[],retainedBasicSupportDependencies=[],leaseResources=sorted('building:'+r['building']['uid']for r in forms),terrainEdits=False,sourceGeometryChanges=0,sourcePoseChanges=0,imagesActuallyViewed=images,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,installationApproved=False,publication=False,visualAcceptance=False,basis=[
        'ROOT inspected both corrected two-angle close-up exports covering every flagged source face. The14facets are exposed lower vertical walls around original facade piers/plinths in two local regions. Actual current coarse ground cuts their lower portions; upper parts remain visible and connected to the original hall. No upward walking/roof face exceeds ordinary clearance and no complete face is buried.',
        'All14777faces have complete ground coverage and zero whollyburied/upwardburied faces in all4representations. Exact finite checks identify only these14wall faces; each highest original vertex clears every overlapping finite ground face.15finite upper-ground zero-gap intervals traverse these14walls in each representation. Exact shared-edge paths reach ordinary-clear original caps.',
        'All4complete ordered source coordinate arrays and complete current ground are byte-identical; therefore the literal mathematical paths apply to exactly the same inputs. No approximate coordinate equivalence or change of source scale/translation is used.',
        'The canonical raw clearance limit remains0.5m and the recorded minimumsamplegap remains-0.965588m. Only2of14wall penetrations reproduce on original governmentTIN;12are due to this coarser currentviewerterrain. This review accepts the specific visible wall/grade relationship under existing source-specific exposed-wall interpretation; it does not claim all14are provider-authored embedments. Broad governmentterrain replacement is neither inferred necessary nor approved.',
        'Runtime policy otherwise passes current contact range, terrain coverage, sampler agreement, exact source identity and mobile budget. Complete currentnativebounds are disjoint and sole foreignbasic121501 haszero exactpositivecontacts/projectedoverlap in all4worlds. No other actor, support dependency or terrain is changed.',
        'This bounded physical interpretation resolves only the exact listed wall/ground warnings. Staged/live desktop/mobile sourceappearance, picking/collision, failurefallback/retry, catalogue/lease/publication checks remain mandatory. No structural engineering, globalwatertightness, generic wall exception or AIgeometrygeneration is asserted.'
    ])
    save(out/'ROOT-PHYSICAL-REVIEW.json',result);refs.append(HERE/'acceptance-policy.py');module('university_physical_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'source-specific-current-exposed-original-wall-ground-interpretation',refs,result)

if __name__=='__main__':main()

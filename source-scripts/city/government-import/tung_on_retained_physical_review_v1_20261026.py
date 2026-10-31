"""Bind the exact Tung On ten-face grade interpretation; preserve all raw failures."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

UID='landsd/53852:0'
SHA='29033ca5151d00c74c2c0a229873543ca7ba5df76433109f6c81657c11b03237'
NEGATIVE=[16,21,22,23,25,163,6052,6991,11392,11393]
PREFIX='government-xl-after-tuen-mun-tung-on-'

def validate_grade_context(low,caps,bottom):
    assert low['sourceSHA256']==caps['sourceSHA256']==bottom['sourceSHA256']==SHA
    assert low['uids']==caps['uids']==bottom['uids']==[UID]
    assert caps['allFourCompleteGroundClearCapPaths']is False
    assert len(low['rows'])==len(caps['rows'])==len(bottom['rows'])==4
    assert {r['mode']for r in low['rows']}=={r['mode']for r in caps['rows']}=={r['mode']for r in bottom['rows']}=={'original','literal','left','balanced'}
    for row in low['rows']:
        assert row['exactAffectedFaces']==NEGATIVE
        c=next(r for r in caps['rows']if r['mode']==row['mode'])['completeGroundClearancePartition']
        assert c['negativeSourceFaces']==NEGATIVE and c['negativeNonWallFaces']==[22]
        assert c['allAffectedHavePaths']is False
        assert [r['sourceFace']for r in c['paths']]==[i for i in NEGATIVE if i!=22]
        assert all(r['hasExactSharedEdgeClearCapPath']for r in c['paths'])
        b=next(r for r in bottom['rows']if r['mode']==row['mode']);assert b['completeSourceFaces']==11629 and len(b['faces'])==1
        f=b['faces'][0];assert f['sourceFace']==22 and f['downward']and f['exactlyHorizontal']
        assert f['areaM2']==0.8013098239898682 and f['wholeSharedEdgeComponentFaces']==4121
        assert [r['incidentSourceFaces']for r in f['exactEdgeIncidence']]==[[21,22],[22,23],[22,162]]
        assert {r['sourceFace']for r in f['adjacentFaces']}=={21,23,162}
        assert all(p[1]==44.152000427246094 for p in f['vertices'])
        # Literal source arithmetic has a measured 7e-15m component-minimum difference.
        # It is retained as context, not converted to a new clearance allowance.
        if row['mode']=='original':assert f['allVerticesAtComponentMinimum']


def main():
    base=ROOT/'docs/astra-city/government-import';batch=PREFIX+'physical-review-v1-20261026';out=base/batch
    assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,file):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        p=base/n/file;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    runtime=PREFIX+'retained-runtime-v2-20261026';selection=take(runtime,'selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selection['rows']}=={UID:SHA}
    asset=ROOT/selection['rows'][0]['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset)
    metric_data=take(runtime,'metrics.json');metric=next(r for r in metric_data['rows']if r['uid']==UID)
    for name,sha in metric_data['inputHashes'].items():assert digest((ROOT/name).read_bytes())==sha;refs.append(ROOT/name)
    identity=take('government-xl-after-tuen-mun-next-two-identity-v1-20261026','53852:0/identity.json')
    assert identity['passed']and not identity['reasons']and identity['sourceSHA256']==SHA
    assert identity['exactRouteManifestSHA256']==selection['manifestSHA256']
    proof=identity['proof'];assert all(proof[k]for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted'])
    policy=module('tung_on_actual_policy',HERE/'acceptance-policy.py')
    reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SHA,identityProof=proof),metric,metric_data['profiles']['mobile'])
    assert reasons==['terrain-intersects-source-over-0.5m']and metric['missingTerrain']==0 and metric['maxSamplerDelta']<=.004 and metric['maxLowGap']<1
    foundations=take(PREFIX+'retained-foundations-v2-20261026','summary.json')['rows']
    assert len(foundations)==4 and {r['mode']for r in foundations}=={'original','literal','explicitLeftF32','explicitBalancedF32'}
    assert all(r['uid']==UID and r['triangles']==r['completeTerrainTriangles']==11629 and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in foundations)
    low=take(PREFIX+'retained-low-faces-v2-20261026','summary.json');caps=take(PREFIX+'complete-cap-paths-v1-20261026','summary.json');bottom=take(PREFIX+'bottom-face-context-v1-20261026','summary.json');validate_grade_context(low,caps,bottom)
    scope=take(PREFIX+'retained-scope-v2-20261026','scope.json');binding=take(PREFIX+'replacement-binding-v2-20261026','summary.json')
    assert scope['currentNativeActors']==6982 and scope['intersectingForms']==40
    replacement=binding['candidate']['replaces'];oldpath=ROOT/'3d-viewer'/replacement['url'];candidate=ROOT/binding['candidate']['path']
    assert digest(oldpath.read_bytes())==replacement['sha256']and digest(candidate.read_bytes())==binding['candidate']['sha256'];refs.extend([oldpath,candidate])
    assert set(read(oldpath)['meta']['targetUids'])==set(replacement['retainedUids'])and set(read(candidate)['meta']['targetUids'])==set(replacement['retainedUids'])|{UID}
    native=take(PREFIX+'retained-neighbours-v2-20261026','summary.json');retained=set(replacement['retainedUids'])
    assert native['forms']==40 and not native['basicFlags']and retained==set(native['requiredNativeUids'])==set(native['nativeResolved'])
    assert all(r['passed']and r['terrain']['newlyWhollyBuried']==r['terrain']['newlyUpwardWhollyBuried']==0 for r in native['nativeRows'])
    contacts=take(PREFIX+'original-native-contacts-v1-20261026','summary.json');assert len(contacts['rows'])==1
    pair=contacts['rows'][0];assert pair['uid']==UID and pair['nativeUid']=='landsd/126434:0'and pair['sourceSHA256']==SHA and len(pair['modes'])==4
    assert all(m['finiteContactPairs']==0 for m in pair['modes'])
    foreign=take(PREFIX+'foreign-basic-contacts-v1-20261026','summary.json');assert foreign['foreignPairs']==0 and not foreign['rows']
    views=take(PREFIX+'grade-views-v2-20261026','summary.json');assert views['allExactNegativeFacesShown']and views['completeExactNegativeFaces']==NEGATIVE and views['sourceSHA256']==SHA
    images=[]
    for r in views['regions']:
        p=ROOT/r['image'];assert digest(p.read_bytes())==r['imageSHA256']==pins[PREFIX+'grade-views-v2-20261026'][r['image']];refs.append(p);images.append(dict(path=r['image'],sha256=r['imageSHA256']))
    assert len(images)==10
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==binding['currentManifestSHA256'];refs.append(manifest)
    result=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},reviewer='ROOT',sourceSpecificPhysicalInterpretationAccepted=True,identityAccepted=True,identityProof=proof,identityProofByUid={UID:proof},completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeCurrentNeighbourChecks=40,retainedNativeRegression=native,exactTerrainReplacement=replacement,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),rawPolicyReasons=reasons,rawFourWorldSourceClearancePassed=False,rawAllFaceCapPathsPassed=False,rawCanonicalFailuresPreserved=True,qualifiedExposedOriginalWallFaces=[i for i in NEGATIVE if i!=22],qualifiedAuthoredBottomClosureFaces=[22],imagesActuallyViewed=images,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,retainedBasicSupportDependencies=[],physicalReviewScope='Only this exact original source and the pinned actual terrain; no generic wall/nonwall exemption.',visualAcceptance=False,installationApproved=False,publication=False,basis=[
      'ROOT inspected all ten actual source/ground two-angle exports. Nine flagged facets are lower original walls crossing the sloping terrain, continuing to exposed original faces through exact complete-ground cap paths in all four coordinate representations. No upward source face remains in the complete negative partition.',
      'Face22 is the original downward triangular closure at the foot of the source vertical projection: 0.8013098239898682m2 at44.152000427246094m, all three edges paired with21/23/162. It lies at the original component minimum. The literal7e-15m component-minimum arithmetic difference is retained verbatim; no precision threshold is raised. The surrounding wall rises above terrain. This accepts its specific partial bottom/grade relationship, not a generic horizontal-face exception or inferred engineering foundation.',
      'All11629 original faces retain complete ground coverage and zero wholly buried/upward-buried facets in every coordinate representation. The raw policy reason, ten partial negatives, minimumsamplegap and all-face cap FALSE remain unchanged. The reviewed decision resolves only those exact lower-wall/bottom warnings; no model movement, geometry edits, support invention or source simplification.',
      'Exact identity passes. All40 current forms/eight retained native models pass complete terrain regressions. Full four-world finite source/native contacts are zero and no external BASIC pair remains in the complete source-only scope. Mobile policy otherwise passes. Existing global retained-support obligations remain mandatory.',
      'Actual desktop/mobile source and retained visual qualification, guarded publication, live checks and full-old-asset/full521ledger readback remain separate mandatory steps. No installation or deployment credit is granted here.' ])
    save(out/'ROOT-PHYSICAL-REVIEW.json',result);refs.append(HERE/'acceptance-policy.py')
    module('tung_on_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-original-tung-on-ten-face-wall-bottom-grade-review',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()

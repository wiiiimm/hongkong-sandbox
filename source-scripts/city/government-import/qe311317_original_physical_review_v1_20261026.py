"""Accept only the pinned QE lower-envelope/junction relationship; keep all raw failures."""
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
UID='landsd/311317:0'
PEER='landsd/161194:0'
SHA='6feeea5687b060e9b39d17be3d6336c0668e92c23a15955602ec7256be4268a1'
PEER_SHA='6d4056023e4751d923a3d5a434364c0b3b3d51f74b26b135935154a0f2430a5e'
PREFIX='government-xl-after-tung-on-qe311317-'
NEGATIVE=[43,44,45,46,47,49,50,75,76,77,78,79,283,284,285,679,680,681,682,683,684,1566,2579,2580,2581,2582,2911,2968,2980,3188,3189,3393,4740,4741,4742,4834,4835,4836,4957,4958,5101,5102,5104,5105]
SLOPES=[679,680,681,682,683,684,2579,2580,2581,2582,2968,3188,3189]
BASIC_JUNCTION=[5103,5104,5105,9111,9112,9113,9119,9308,9309,9310]


def validate_grade(low,caps,components):
    assert low['sourceSHA256']==caps['sourceSHA256']==components['sourceSHA256']==SHA
    assert low['uids']==caps['uids']==components['uids']==[UID]
    assert caps['allFourCompleteGroundClearCapPaths']is False
    worlds={'original','literal','left','balanced'}
    assert len(low['rows'])==len(caps['rows'])==len(components['rows'])==4
    assert {r['mode']for r in low['rows']}=={r['mode']for r in caps['rows']}=={r['mode']for r in components['rows']}==worlds
    for r in low['rows']:
        assert r['exactAffectedFaces']==NEGATIVE and r['completeSourceFaces']==11584
        c=next(x for x in caps['rows']if x['mode']==r['mode'])['completeGroundClearancePartition']
        assert c['negativeSourceFaces']==NEGATIVE and c['negativeNonWallFaces']==SLOPES and c['allAffectedHavePaths']is False
        assert [x['sourceFace']for x in c['paths']]==[i for i in NEGATIVE if i not in SLOPES]
        assert all(x['hasExactSharedEdgeClearCapPath']for x in c['paths'])
        context=next(x for x in components['rows']if x['mode']==r['mode']);assert context['completeSourceFaces']==11584
        assert [x['sourceFace']for x in context['faces']]==SLOPES
        for f in context['faces']:
            assert f['normal'][1]>0 and not f['downward']and not f['exactlyHorizontal']and f['areaM2']>0
            assert f['wholeSharedEdgeComponentFaces']==9185 and f['sourceFace']in f['componentFaceIds']
            assert len(f['exactEdgeIncidence'])==3 and all(f['sourceFace']in e['incidentSourceFaces']for e in f['exactEdgeIncidence'])
            assert f['componentBounds'][0][1]<=min(v[1]for v in f['vertices'])<max(v[1]for v in f['vertices'])<f['componentBounds'][1][1]


def validate_lineage(lineage,crossings):
    assert lineage['sourceSHA256ByUid']==crossings['sourceSHA256ByUid']=={UID:SHA,PEER:PEER_SHA}
    assert lineage['allRepresentedCrossingsHaveOriginalFacetPairContacts']is True
    assert crossings['allFourWorldTransverseSegmentsStrictlySubgrade']is False
    expected={'original':1,'literal':32,'leftF32':1,'balancedF32':1}
    assert len(lineage['rows'])==len(crossings['rows'])==4 and {r['mode']for r in lineage['rows']}=={r['mode']for r in crossings['rows']}==set(expected)
    for r in lineage['rows']:
        mode=r['mode'];assert r['transverseSegments']==expected[mode]and r['allRepresentedCrossingsHaveOriginalFacetPairContacts']
        g=next(x for x in crossings['rows']if x['mode']==mode);assert g['transverseSegments']==expected[mode]
        if mode=='literal':
            assert r['originalRoleCounts']=={'surface-point-contact':23,'source-edge-surface-contact':8,'transverse-surface-crossing':1}
            assert g['allTransverseSegmentsStrictlySubgrade']is False
        else:
            assert r['originalRoleCounts']=={'transverse-surface-crossing':1}and g['allTransverseSegmentsStrictlySubgrade']is True
        assert all(x['originalPairContact']is not None for x in r['rows'])
    d=lineage['completeCorrespondingVertexDeltas']
    assert d[UID]['literal']['exactMaximumAbsoluteCoordinateDeltaM']==['0','1/140737488355328','0']
    assert d[PEER]['literal']['exactMaximumAbsoluteCoordinateDeltaM']==['0','1/562949953421312','0']
    assert all(d[UID][m]['completeIndexedVerticesCompared']==34752 and d[PEER][m]['completeIndexedVerticesCompared']==1557 for m in ['literal','leftF32','balancedF32'])


def main():
    base=ROOT/'docs/astra-city/government-import';batch=PREFIX+'physical-review-v1-20261026';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(name,file):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        p=base/name/file;assert digest(p.read_bytes())==pins[name][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    def local(name,file):return take(name,HERE/'local'/name/file)
    runtime=PREFIX+'retained-runtime-v1-20261026';selection=take(runtime,'selection.json.gz');row,=selection['rows'];assert row['uid']==UID and row['sourceSHA256']==SHA
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset)
    identity=take(PREFIX+'source-identity-review-v1-20261026','summary.json');assert identity['identityAccepted']and identity['sourceSpecificIdentityReviewAccepted']and identity['sourceSHA256ByUid']=={UID:SHA}
    proof=identity['identityProof'];assert all(proof[k]for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted'])
    metrics=take(runtime,'metrics.json');metric,=metrics['rows'];assert metric['uid']==UID and metric['sourceSHA256']==SHA and metric['sourcePreserved']
    for path,sha in metrics['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    policy=module('qe_original_actual_policy',HERE/'acceptance-policy.py');reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SHA,identityProof=proof),metric,metrics['profiles']['mobile'])
    assert reasons==['terrain-intersects-source-over-0.5m']and metric['missingTerrain']==0 and metric['maxSamplerDelta']==0 and metric['maxLowGap']<0
    foundation=take(PREFIX+'retained-foundations-v1-20261026','summary.json');assert foundation['establishedFoundationPolicyPassed']and len(foundation['rows'])==4
    assert all(r['uid']==UID and r['triangles']==r['completeTerrainTriangles']==11584 and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in foundation['rows'])
    low=take(PREFIX+'retained-low-faces-v1-20261026','summary.json');caps=take(PREFIX+'retained-cap-paths-v1-20261026','summary.json');components=take(PREFIX+'sloped-face-components-v1-20261026','summary.json');validate_grade(low,caps,components)
    lineage=take(PREFIX+'pair161194-crossing-lineage-v1-20261026','summary.json');crossings=take(PREFIX+'pair161194-four-world-crossing-ground-v1-20261026','summary.json');validate_lineage(lineage,crossings)
    foreign_name=PREFIX+'foreign-basic-contacts-v1-20261026';foreign=take(foreign_name,'summary.json');assert foreign['foreignPairs']==4 and len(foreign['rows'])==4
    old_runtime=PREFIX+'patch-runtime-v2-20261026';old_g=next(x for x in local(old_runtime,'runtime-geometry.json.gz')['rows']if x['uid']==UID);current_g=next(x for x in local(runtime,'runtime-geometry.json.gz')['rows']if x['uid']==UID)
    assert old_g['sourceSHA256']==current_g['sourceSHA256']==SHA and np.array_equal(old_g['position'],current_g['position'])and np.array_equal(old_g['index'],current_g['index'])
    original_pair=take(PREFIX+'pair161194-four-world-roles-v1-20261026','original.json.gz');pair_faces={c['sourceFaceA']for c in original_pair}
    for pair in foreign['rows']:
        assert pair['uid']==UID and len(pair['modes'])==5
        for m in pair['modes']:
            if pair['foreignUid']==PEER and m['mode']!='before-basic':
                assert m['positiveContactPairs']==m['allFiniteContactPairs']==15
                data=take(foreign_name,'311317:0--161194:0--'+m['mode']+'.json.gz');assert data['allPairsExamined']and data['sourceFacesOmitted']==0
                assert len(data['contacts'])==15 and all(c['dimension']==1 for c in data['contacts'])
                assert sorted({c['sourceFaceA']for c in data['contacts']})==BASIC_JUNCTION and set(BASIC_JUNCTION)<=pair_faces
            else:assert m['positiveContactPairs']==m['allFiniteContactPairs']==0
    modelscope=take(PREFIX+'model-scope-v1-20261026','summary.json');ms,=modelscope['rows'];assert ms['uid']==UID and ms['sourceSHA256']==SHA and ms['currentNativeActorsChecked']==6983 and not ms['nearbyNativeActors']
    scope=take(PREFIX+'retained-scope-v1-20261026','scope.json');binding=take(PREFIX+'retained-replacement-binding-v1-20261026','summary.json');native=take(PREFIX+'retained-neighbours-v1-20261026','summary.json')
    retained={'landsd/266063:0','landsd/238669:0','landsd/238671:0','landsd/238856:0'}
    assert scope['currentNativeActors']==6983 and scope['intersectingForms']==native['forms']==73 and not native['basicFlags']
    assert set(native['requiredNativeUids'])==set(native['nativeResolved'])==retained and all(r['passed']for r in native['nativeRows'])
    replacement=binding['candidate']['replaces'];oldpath=ROOT/'3d-viewer'/replacement['url'];candidate=ROOT/binding['candidate']['path'];assert digest(oldpath.read_bytes())==replacement['sha256']and digest(candidate.read_bytes())==binding['candidate']['sha256'];refs.extend([oldpath,candidate])
    assert set(replacement['retainedUids'])==set(read(oldpath)['meta']['targetUids'])=={'landsd/266063:0'}and set(read(candidate)['meta']['targetUids'])=={UID,'landsd/266063:0'}
    views=take(PREFIX+'low-group-views-v2-20261026','summary.json');assert views['sourceSHA256']==SHA and views['completeAffectedFaces']==NEGATIVE and len(views['groups'])==3
    assert sorted(i for group in views['groups']for i in group['sourceFaces'])==NEGATIVE and set(SLOPES)<=set(views['groups'][0]['sourceFaces'])
    observation=take(PREFIX+'private-observation-v1-20261026','ROOT-PRIVATE-EXPORT-OBSERVATION.json');assert observation['reviewer']=='ROOT'and observation['completePrivateExportObservation']and len(observation['sourceExportsActuallySeenWithinSheets'])==20
    browser=PREFIX+'private-browser-v1-20261026';br,_=authenticate(base/browser);refs.append(base/browser/'result.json');assert br['allBrowserDiagnosticsPassed']and not br['downloadFailureTestsSkipped']and set(br['retainedNativeUids'])==retained
    mp=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(mp.read_bytes());assert msha==selection['manifestSHA256']==identity['currentManifestSHA256']==binding['currentManifestSHA256']==br['currentManifestSHA256'];refs.append(mp)
    images=views['exports']
    for r in images:
        path=ROOT/r['path'];assert digest(path.read_bytes())==r['sha256'];refs.append(path)
    result=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},reviewer='ROOT',sourceSpecificPhysicalInterpretationAccepted=True,identityAccepted=True,identityProof=proof,identityProofByUid={UID:proof},completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeCurrentNeighbourChecks=73,retainedNativeRegression=native,exactTerrainReplacement=replacement,currentManifest=dict(path=str(mp.relative_to(ROOT)),sha256=msha),rawPolicyReasons=reasons,rawFourWorldSourceClearancePassed=False,rawAllFaceCapPathsPassed=False,rawAllFourWorldCrossingsSubgrade=False,rawCanonicalFailuresPreserved=True,qualifiedExposedOriginalWallFaces=[i for i in NEGATIVE if i not in SLOPES],qualifiedOriginalSlopingLowerEnvelopeFaces=SLOPES,qualifiedBasicJunction=dict(uid=PEER,sourceFaces=BASIC_JUNCTION,lineContactsPerWorld=15,areaContacts=0),literalJunctionInterpretation='31 additional literal crossings correspond exactly to23 original point contacts and8 original edge/surface contacts; original true crossing strictly subgrade. All raw crossings preserved, no numerical tolerance waiver.',imagesActuallyViewed=images,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,retainedBasicSupportDependencies=[],physicalReviewScope='Only QE311317 exact source, exact13 sloping lower-envelope facets, exact31 wall paths, pinned ground and peer junction; no generic upward-facet or collision exemption.',visualAcceptance=False,installationApproved=False,publication=False,basis=[
      'ROOT inspected every flagged facet in three complete exact-connected low-face groups, each shown from both sides, plus the original peer junction. Thirty-one lower wall facets continue through exact original cap paths to clear original surface in all four worlds.',
      'The thirteen upward sloping facets are deliberately retained as the original authored lower-envelope/grade relationship. They are NOT reclassified as downward closures, horizontal floors, engineering foundations or walkways. All lie within the same9185-face original building component and local lower-detail group; none is a detached fabricated support. Partial grade intersection is accepted for these exact original lower surfaces after complete-ground and whole-building visual review. It is not accepted for another source or an arbitrary buried roof.',
      'Every original facet has drawn ground coverage; all11584 faces retain zero wholly buried or upward-wholly-buried triangles in all four worlds. Main source silhouette/roof/facade remains complete in actual desktop/mobile day/night views. All73 surrounding forms/four retained detailed models pass fresh regressions. No surface was moved, removed, joined, simplified or generated to clear a warning.',
      'The sole BASIC junction is161194:15 line-only contacts in each source world; every contacted source facet also meets the independently recovered original peer. All three other foreign actors have zero finite contacts. This accepts an authored boundary junction, not a structural support edge; peerBASIC remains and no actor is suppressed. Exact original peer contains five shared coplanar contact areas and a single true crossing proved strictly subgrade.',
      'Literal-runtime additional crossings map only to the same original point/edge facet-pair junctions, with exact coordinate-evaluation deltas recorded by the complete correspondence proof. All32 literal crossings and the raw non-subgrade result remain. This source-specific junction interpretation uses original authored relationships and actual scene observation, not infinite-plane depth, a new clearance tolerance or an assumption that all runtime crossings are below ground.',
      'Physical review is separate from guarded stage/publication, live checks, full old asset/catalogue/521-key ledger readback and final installation credit. Existing global retained-BASIC/source/native/placement/lease/rollback guards remain mandatory.' ])
    save(out/'ROOT-PHYSICAL-REVIEW.json',result);refs.append(HERE/'acceptance-policy.py');module('qe_original_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-qe311317-authored-lower-envelope-and-junction-physical-review',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()

"""ROOT's bounded exact-source review after complete contacts and private exports."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-fuying181489-'
BATCH=PREFIX+'source-physical-visual-review-v1-20261029'
SHA='bffdf5653f4dd01917b4028e0cd2f0559fcdb3ce960a4d7cabd5a0392b9ae163'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];cache={};jobs={}
    def take(batch,p):
        if batch not in cache:
            receipt,cache[batch]=authenticate(BASE/batch);jobs[batch]=receipt['jobId'];refs.append(BASE/batch/'result.json')
        assert ref(p)['sha256']==cache[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    def summary(suffix):
        b=PREFIX+suffix+'-20261029';return take(b,BASE/b/'summary.json')
    association=summary('exact-source-association-review-v1');assert association['exactSourceAssociationAccepted']
    profile=summary('complete-excess-facets-v1');assert profile['everyOriginalFaceExaminedAtEveryBand']and profile['wholeOriginalFaces']==14692 and profile['sourceSHA256']==SHA
    foundations=summary('six-foundation-sequence-v1');assert foundations['allSixFourWorldFoundationsComplete']and foundations['allEstablishedFoundationPoliciesPassed']
    neighbours=summary('five-member-neighbours-v1');assert neighbours['forms']==40 and neighbours['allNeighbourRegressionsResolved']and len(neighbours['allNativeRows'])==9
    ground=summary('five-member-boundary-contract-v2');assert ground['allTerrainValidatorsPassed']and ground['allFiveEffectiveMembersVerified']
    scopebatch=PREFIX+'five-member-full-scope-v1-20261029';scope=take(scopebatch,BASE/scopebatch/'scope.json');assert scope['unreviewedPositiveAreaTerrainOverlaps']==0
    contact=summary('source-contact-sequence-v1');assert contact['completeSourceContactSequence']
    natives=take(PREFIX+'source-contact-sequence-v1-20261029-natives',BASE/(PREFIX+'source-contact-sequence-v1-20261029-natives')/'summary.json')
    assert len(natives['rows'])==6
    for row in natives['rows']:
        assert row['sourceSHA256']==SHA
        assert all(m['sourceFaces']==14692 and m['areaContactPairs']==0 for m in row['modes'])
        assert all(m['positiveSurfaceContactPairs']==0 for m in row['modes'])or row['nativeUid']=='landsd/50662:0'
    basicbatch='government-xl-fuying233291-basic-contact-views-v1-20261029';basic=take(basicbatch,BASE/basicbatch/'summary.json')
    assert len(basic['contactContext'])==8 and {c['sourceFace']for c in basic['contactContext']}=={14034}and {c['foreignFace']for c in basic['contactContext']}==set(range(108,116))
    assert all(c['dimension']==1 and c['absoluteNormalY']==[1.,0.]for c in basic['contactContext'])
    nativebatch='government-xl-fuying50662-native-contact-views-v1-20261029';native=take(nativebatch,BASE/nativebatch/'summary.json')
    assert native['rows'][0]['roles']=={'coplanar-edge-contact':3,'source-edge-surface-contact':4,'surface-point-contact':126}
    viewed=[];browser=PREFIX+'five-member-private-browser-v1-20261029';reports=[]
    for width in [1280,390]:
        path=BASE/browser/str(width)/'staged-browser.json';r=take(browser,path);reports.append(ref(path));assert r['passed']and not r['errors']
        views=[v for v in r['views']if 'time'in v];assert len(views)==2
        assert all(v['sourceSHA256']==SHA and v['originalTriangles']==14692 and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']=='landsd/181489:0'for v in views)
        retained=r['retainedNativeOwnViews'];assert len(retained)==18
        for v in views+retained:
            p=BASE/browser/str(width)/v['file']
            assert ref(p)['sha256']==cache[browser][str(p.relative_to(ROOT))];refs.append(p);viewed.append(ref(p))
    assert len(viewed)==40
    diagrams=[]
    for b in [basicbatch,nativebatch]:
        for p in (BASE/b).glob('*.png'):
            assert ref(p)['sha256']==cache[b][str(p.relative_to(ROOT))];refs.append(p);diagrams.append(ref(p))
    assert len(diagrams)==2
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)==association['currentManifest'];refs.append(manifest)
    proof=BASE/(PREFIX+'five-member-boundary-contract-v2-20261029')/'whole-parent-contract.json';take(PREFIX+'five-member-boundary-contract-v2-20261029',proof)
    result=dict(uids=['landsd/181489:0'],sourceSHA256ByUid={'landsd/181489:0':SHA},currentManifest=ref(manifest),sourceAssociationReview=ref(BASE/(PREFIX+'exact-source-association-review-v1-20261029')/'summary.json'),rawIdentityReasons=association['rawIdentityReasons'],identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,physicalAcceptance=True,visualAcceptance=True,qualifiedForGuardedStaging=True,installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,imagesActuallyViewed=viewed,contactDiagramsActuallyViewed=diagrams,browserReports=reports,evidence=jobs,wholeParentContract=ref(proof),retainedBasicSupportDependencies=[],sourceRoleInterpretation='Exact government root/GeoRef Tower01/current UID-CSUID whole1m cell binds this unchanged source. Full facet clipping, source views and complete contacts establish that the long source projection is authored low canopy detail; it is retained, not trimmed to the approximate building footprint. The >2m clipped source bound is12.611m HKPD while the actual tower reaches132.662m. These distances are contextual measurements, not replacement admission thresholds. No other tower is assigned to this UID; no architectural completeness/ownership claim.',contactInterpretation='All6native pairs and3foreign BASIC pairs were tested as finite surfaces in4worlds. Fu Wong50662 has3coplanar-edge/4source-edge/126point original contacts at adjacent low authored canopies, with no positive area and no source/support edits. The only foreign BASIC intersection is one existing approximate0.22m square illustrative post at233291 through horizontal original canopy face14034. ROOT accepts that existing schematic post/thin-canopy junction for this faithful original port; it is not evidence of a misidentified tower, surveyed column ownership or structural certification. Keep the entire BASIC actor and both native originals; no suppression or new dependency is claimed. Surface tests alone do not establish solid-volume containment.',groundInterpretation='All6four-world foundations and40forms/9complete native regressions pass under existing policy.39derived terrain connector facets preserve prior positions/indices and finite1cm seam/2mmincident-face limits. All5members replace the old whole extent exactly once; every other terrain asset/metadata and all prior model entries must remain unchanged. This review is for this exact source/ground/current scene only; live installation and independent installed readback remain mandatory.')
    save(out/'ROOT-SOURCE-PHYSICAL-VISUAL-REVIEW.json',result)
    terrain=dict(status='approved-for-five-member-terrain-staging',currentManifest=ref(manifest),wholeParentContract=ref(proof),supersededURL=ground['oldParent']['path'].removeprefix('3d-viewer/'),supersededSHA256=ground['oldParent']['sha256'],sourceGeometryChanges=0,sourcePoseChanges=0,derivedTerrainConnectorFacetsAdded=39,allPriorTerrainPositionsAndIndicesPreserved=True,allSixFourWorldFoundationsPassed=True,all40FormsAnd9NativeRegressionsPassed=True,retainedNativeRows=neighbours['allNativeRows'],all40PrivateExportsActuallyViewed=True,replacementSources={m['candidate']['path']:m['candidate']['sha256']for m in ground['members']},modelInstallationApproved=False,evidenceFiles=[ref(p)for p in dict.fromkeys(refs)if p.suffix not in ['.png']])
    save(out/'ROOT-TERRAIN-GROUP-REVIEW.json',terrain)
    module('fuying_source_physical_visual_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-source-physical-visual-and-whole-parent-terrain-review',refs,result)
if __name__=='__main__':main()

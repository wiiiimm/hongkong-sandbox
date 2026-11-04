"""Bound exact unchanged HKUST Staff original, ground and current BASIC interfaces."""
import sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';UID='landsd/309822:0';SHA='56fe512572733202ce049360e08fe0effc15919bec6e296ac667e06f867c957f'
BATCH='government-xl-hkust-staff309822-physical-review-v1-20261102'
CTX='government-xl-hkust-staff-tower-current-context-v2-20261102';GROUND='government-xl-hkust-staff-tower-float-ground-proof-v1-20261102'
PREVIEW='government-xl-hkust-staff-tower-three-footings-preview-v1-20261102';POST='government-xl-hkust-staff-tower-retained-context-v2-20261102'
SCOPE=CTX+'-terrain-scope';IDENTITY='government-xl-hkust-staff309822-component-identity-review-v2-20261102'

def main():
    out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json';refs=[Path(__file__)];pins={}
    def take(batch,name='summary.json',local=False):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        p=(HERE/'local'/batch if local else BASE/batch)/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    forms=take(SCOPE,'form-obligations.json.gz');scope=take(SCOPE,'scope.json');assert len(forms)==11 and scope['uids']==[UID] and not scope['touchingNativeUids'] and scope['positiveAreaTerrainOverlaps']==0
    resources={'building:'+b['uid']for b in forms}|{'terrain:city/data/terrain.json'}
    for r in scope['terrainContacts']:
        p=ROOT/'3d-viewer'/r['url'];assert digest(p.read_bytes())==pins[SCOPE][str(p.relative_to(ROOT))];refs.append(p);resources.add('terrain:'+r['url']);resources.update('building:'+u for u in read(p)['meta']['targetUids'])
    if '--owned'not in sys.argv:
        assert not out.exists()and not lp.parent.exists();c=reservations.claim('hkust-staff-physical-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==resources
    selection=take(CTX+'-runtime','selection.json.gz');assert len(selection['rows'])==1 and selection['rows'][0]['sourceSHA256']==SHA and selection['rows'][0]['uid']==UID
    binding=take(CTX+'-numeric-binding');assert binding['allActualLiteralSourceAndDrawnGroundInputsIdentical']and binding['allFourWorldSourceAttributesIdentical']and binding['priorNumericRelationsStillApplyToExactCurrentInputs']
    earth=take('government-xl-hkust-staff-three-float-physical-v1-20261102-foundations-309822');assert earth['establishedFoundationPolicyPassed']and len(earth['rows'])==4
    assert all(r['uid']==UID and r['triangles']==r['completeTerrainTriangles']==12943 and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in earth['rows'])
    coverage=take(GROUND+'-coverage');assert coverage['sourceSHA256']==SHA and coverage['completeProjectionCoverageProved']and coverage['remainingExactlyUncoveredFaces']==[]
    roots=take(GROUND+'-roots');assert len(roots['rows'])==4 and all(r['strictRoots']==75 and r['targets']==r['finitePaths']==152 and r['aboveEndpointCeiling']==r['nonrenderingOnlyWitnesses']==0 for r in roots['rows'])
    low=take(GROUND+'-lowfaces');caps=take(GROUND+'-cap-paths');assert caps['allFourCompleteGroundClearCapPaths']and low['sourceSHA256']==caps['sourceSHA256']==SHA
    for row in low['rows']:
        cap=next(r for r in caps['rows']if r['mode']==row['mode'])['completeGroundClearancePartition'];assert row['completeSourceFaces']==cap['completeSourceFaces']==12943
        assert row['allAffectedWallLike']and len(row['exactAffectedFaces'])==34 and row['exactAffectedFaces']==cap['negativeSourceFaces']and cap['negativeNonWallFaces']==cap['nonrenderingSourceFaces']==[] and cap['allAffectedHavePaths']
    identity=take(IDENTITY);assert identity['identityAccepted']and identity['sourceSHA256ByUid']=={UID:SHA};proof=identity['rows'][0]['identityProof'];assert all(proof.values())
    named_identity=take(IDENTITY,'309822:0-identity-review.json')
    terrain=take('government-xl-hkust-staff-tower-only-terrain-v2-20261102');assert terrain['status']=='private-terrain-validator-passed'and terrain['terrainGeometryExactlyUnchanged']and terrain['uids']==[UID]
    boundary=take('government-xl-hkust-staff-tower-retained-boundaries-v1-20261102');assert boundary['sourceSHA256']==SHA and len(boundary['rows'])==10
    for r in boundary['rows']:
        assert r['areaContactPairs']==0
        if r['mode']=='before-basic':continue
        assert r['finiteContactPairs']==(32 if r['foreignUid']=='landsd/29031:0' else 217)
    foreign=take('government-xl-hkust-staff-tower-current-foreign-v1-20261102');assert foreign['foreignPairs']==5
    assert all(m['positiveContactPairs']==0 for r in foreign['rows']if r['foreignUid']in ['landsd/26966:0','landsd/26967:0','landsd/27083:0']for m in r['modes']if m['mode']!='before-basic')
    neighbour=take('government-xl-hkust-staff-tower-only-neighbours-v1-20261102');assert neighbour['forms']==11 and neighbour['requiredNativeUids']==neighbour['nativeRows']==[]
    expected=['landsd/26966:0','landsd/26967:0','landsd/27083:0'];assert sorted(r['uid']for r in neighbour['basicFlags'])==expected and all(r['reasons']==['increased-neighbour-ground-gap']for r in neighbour['basicFlags'])
    fragment=[]
    for u in expected:
        n=POST+'-post-'+u.split('/')[1].split(':')[0];p=take(n,'proposal.json');q=take(n);b=take(n,'input.json')['building'];render=take(n,'render-proof.json')
        assert b in forms and p['uid']==q['uid']==u and q['fullPostFootprintsMeetGround']and q['wholeRoofClear']and q['roofAndRecordedElevationsUnchanged']
        assert all(render[k]for k in ['roofPartsExactlyUnchanged','allXZExactlyUnchanged','onlyIllustrativePostBottomVerticesChanged'])and render['governmentGeometryChanges']==0
        tile=ROOT/'3d-viewer/city/data/tiles'/(b['tile']+'.json');assert next(x for x in read(tile)['buildings']if x['uid']==u)==b;refs.append(tile)
        fragment.append(dict(uid=u,tile=str(tile.relative_to(ROOT/'3d-viewer')),tileSHA256=digest(tile.read_bytes()),before=b,foundationBase=p['foundationBase'],evidence=dict(path=str((BASE/n/'summary.json').relative_to(ROOT)),sha256=digest((BASE/n/'summary.json').read_bytes())),proposal=dict(path=str((BASE/n/'proposal.json').relative_to(ROOT)),sha256=digest((BASE/n/'proposal.json').read_bytes()))))
    joint=take(POST+'-joint-posts');assert joint['simultaneousBasicFoundationProbesPassed']and sorted(joint['uids'])==expected and joint['forms']==11
    edge=take('government-xl-hkust-staff-tower-shared-edge-v2-20261102');assert edge['allExistingBoundaryComparisonsPassed']and edge['candidateBinding']==terrain['candidate']
    cat=take(PREVIEW,'catalogue.json',True);assert len(cat['models'])==1;entry=cat['models'][0];assert entry['sha256']==SHA and not entry.get('supportDependencies')and not entry.get('retainedBasicSupportDependencies')and not entry.get('suppressesBuildingUids')and entry['proceduralWindows']is False
    obs=BASE/'government-xl-hkust-staff-tower-actual-observations-v1-20261102.json';seen=read(obs);refs.append(obs);observed={r['path']:r['sha256']for r in seen['imagesActuallyViewed']};assert len(observed)==4
    images=[];reports=[]
    for width in [1280,390]:
        name=str(width)+'/staged-browser.json';report=take(PREVIEW,name);assert report['passed']and not report['errors'];views=[v for v in report['views']if 'time'in v];assert len(views)==2
        assert sorted(report['productionSourceBoundExperiment']['uids'])==expected and report['productionSourceBoundExperiment']['productionGeometryHTTPVerified']
        for v in views:
            assert v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==UID and v['sourceSHA256']==SHA
            p=BASE/PREVIEW/str(width)/v['file'];im=dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()));assert observed[im['path']]==im['sha256'];refs.append(p);images.append(im)
        p=BASE/PREVIEW/name;reports.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
    bo=BASE/'government-xl-hkust-staff-tower-boundary-observations-v1-20261102.json';seen_boundary=read(bo);refs.append(bo);assert seen_boundary['imagesActuallyViewed']==boundary['images']
    for im in boundary['images']:p=ROOT/im['path'];assert digest(p.read_bytes())==im['sha256'];refs.append(p)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==selection['manifestSHA256']==identity['currentManifestSHA256']==boundary['currentManifestSHA256'];refs.append(manifest)
    result=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},requiredOriginalAssembly={UID:SHA},supportByUid={},retainedBasicSupportDependencies=[],retainedCurrentBasicSupportUids=[],identityAccepted=True,identityProof=proof,identityProofByUid={UID:proof},sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeCurrentNeighbourChecks=11,leaseResources=sorted(resources),currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=mh),currentManifestSHA256=mh,rawCanonicalFailuresPreserved=True,rawFoundationRows=earth['rows'],rawRoots=roots['rows'],rawNegativeWallContext=low['rows'],rawForeignContacts=foreign['rows'],rawBoundaryContext=boundary['rows'],rawNeighbourFlags=neighbour['basicFlags'],acceptedForeignBoundaryPairs=[dict(uid=UID,foreignUid=u)for u in ['landsd/29031:0','landsd/232155:0']],unresolvedExternalBasicContacts=[],basicFlagsResolvedByExactIllustrativePostProofs=expected,sourceGeometryChanges=0,sourcePoseChanges=0,terrainEdits=True,proposedTerrainChange=True,publicTerrainWritesPerformed=False,imagesActuallyViewed=images,browserReports=reports,visualAcceptance=True,installationApproved=False,publication=False,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,interpretation=[
        'Accept this exact original standalone tower at fixed1x/source HKPD placement. All12943faces have exact actual-ground coverage in all streams. Every34negative wall has a complete original-edge cap path, no negative nonwall exists, all152rawrim witnesses reach75independently replayed strict actual-ground anchors per stream. These are original wall/ground interfaces, not a reason to import the unresolved optional podium source. No geometry/pose change or manufactured support.',
        'Retain all current BASIC forms. The named same-parent podium sits under the complete tower with217line intersections at55.431–58.8m and no area contacts; broad projection overlap is expected for this nested relation, not a narrow clearance sliver. The end structure has32line contacts at59.5–64m and0area contacts along the terminal frontage. Its full projection strip is0.997047m, explicitly not a centimetre bound. Exact separate government small-original13authored contacts per stream and inspected complete/zoomed source/current diagrams establish an authored end interface represented more coarsely by BASIC. Accept only these exact source-to-proxy interfaces; no generic collision exception, ownership inference, source companion approval, removal or remodelling.',
        'Three estimated canopy neighbours retain every roof/XZ/recorded elevation; only existing illustrative post bottoms reach the actual repaired terrain. Whole-post/roof proofs and19950jointBASICprobes pass. All three have zero target source surface contacts before adjustment; two have no XZoverlap and the third lies wholly below the overlapping source faces, so downward-only posts cannot introduce a tower crossing. All other eight forms and touching native actors retain their actual current regression evidence.',
        'Both actual desktop/mobile loading/picking/collision/failure/retry tests and all4day/night exports passed and were inspected. Overview cameras do not resolve every shelter footing; exact geometry proofs are separate. Native night darkness remains, no allfacade/FPS claim. Final qualified publisher dryrun, actual installed checks and independent full521/oldasset/global-support readback remain mandatory.'])
    save(out/'ROOT-PHYSICAL-REVIEW.json',result);save(out/'ROOT-SOURCE-REVIEW.json',result);save(out/'basic-plan-fragment.json',dict(illustrativeFoundations=fragment))
    assert reservations.owns(lease)and digest(manifest.read_bytes())==mh
    module('hkust_staff_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-exact-original-hkust-staff-ground-and-current-basic-interface-review',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()

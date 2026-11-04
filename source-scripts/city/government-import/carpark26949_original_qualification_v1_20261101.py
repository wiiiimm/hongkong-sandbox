"""Exact original carpark source/scene qualification; no publication or install credit."""
import argparse,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-academic309823-after-kai-tak-'
BATCH=P+'carpark-original-qualification-v1-20261101';UID='landsd/26949:0';OTHER='landsd/309823:0'
SHA='e4cf4099b7a1179c0c1a6ea27a7dc9036bde9ad08ba2ee900a6ac0fe3542fde8'
TERRAIN='c77dc11810a546afe58b403cef43c62e83c882208ff73087bee74054227766e1'

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json';planpath=BASE/(P+'carpark-current-runtime-plan-v1-20261101.json')
    resources=sorted(set(read(planpath)['resources'])|{'server:127.0.0.1:4177'})
    assert not out.exists()
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('carpark-original-qualification-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok']
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    refs=[Path(__file__),planpath];pins={};allpins={}
    def take(batch,name,external=None):
        if batch not in pins:
            _,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
            for p,h in pins[batch].items():assert p not in allpins or allpins[p]==h;allpins[p]=h
        path=external or BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    rt=P+'carpark-after-floor-runtime-v1-20261101';selection=take(rt,'selection.json.gz');source=selection['rows'][0]
    assert len(selection['rows'])==1 and source['uid']==UID and source['sourceSHA256']==SHA and source['triangles']==680
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset)
    identity=take(P+'carpark-shared-structure-identity-v1-20261101','identity.json');assert identity['passed']and identity['identityAccepted']and identity['sourceSHA256']==SHA and identity['officialSharedStructureID']==1732120
    lower=take(P+'carpark-lower-source-review-v1-20261101','summary.json');assert lower['sourceRoleAccepted']and lower['lowerSourceRoleOnly']and lower['sourceSHA256']==SHA
    assert len(lower['rows'])==4 and all(r['groundContactResolved']and r['allWallsHaveOriginalClearCapPaths']and r['allRawNegativeSamplesAccounted']for r in lower['rows'])
    foundations=take(P+'carpark-after-floor-foundation-v1-20261101','summary.json');assert foundations['establishedFoundationPolicyPassed']and len(foundations['rows'])==4
    scope=take(P+'carpark-after-floor-scope-v1-20261101','scope.json');forms=take(P+'carpark-after-floor-scope-v1-20261101','form-obligations.json.gz');assert scope['intersectingForms']==len(forms)==3 and scope['currentNativeActors']==7066 and not scope['touchingNativeUids']and not scope['terrainContacts']and scope['positiveAreaTerrainOverlaps']==0
    checks=take(P+'carpark-after-floor-form-checks-v1-20261101','summary.json');assert checks['forms']==3 and checks['flagged']==[]
    patch=take(P+'carpark-upward-floor-return-v1-20261101','summary.json');assert patch['status']=='private-terrain-validator-passed'and patch['sourceSHA256ByUid']=={UID:SHA}and patch['candidate']['sha256']==TERRAIN and patch['terrainTriangles']==2856
    patchpath=ROOT/patch['candidate']['path'];assert digest(patchpath.read_bytes())==TERRAIN;refs.append(patchpath)
    modelscope=take(P+'carpark-current-model-scope-v1-20261101','summary.json');assert modelscope['uids']==[UID]and modelscope['rows'][0]['currentNativeActorsChecked']==7066 and not modelscope['rows'][0]['nearbyNativeActors']
    foreign_batch=P+'carpark-current-foreign-contacts-v1-20261101';foreign=take(foreign_batch,'summary.json');assert foreign['foreignPairs']==1 and len(foreign['rows'])==1 and foreign['rows'][0]['foreignUid']==OTHER
    modes=foreign['rows'][0]['modes'];assert {r['mode']for r in modes}=={'before-basic','original','literal','leftF32','balancedF32'}
    assert next(r for r in modes if r['mode']=='before-basic')['allFiniteContactPairs']==0
    contact_bounds=[]
    for mode in ['original','literal','leftF32','balancedF32']:
        measured=next(r for r in modes if r['mode']==mode);assert measured['positiveContactPairs']==measured['allFiniteContactPairs']==16
        raw=take(foreign_batch,'26949:0--309823:0--'+mode+'.json.gz');assert raw['allPairsExamined']and raw['sourceFacesOmitted']==0
        assert len(raw['contacts'])==16 and all(r['dimension']==1 for r in raw['contacts'])
        points=np.asarray([p for r in raw['contacts']for p in r['bounds']],dtype=float)
        contact_bounds.append(dict(mode=mode,bounds=[points.min(0).tolist(),points.max(0).tolist()],rawFiniteContacts=16))
    original_pairs=take(P+'carpark-academic-original-pair-v1-20261101','summary.json');assert original_pairs['completeUnorderedPairs']==1 and len(original_pairs['rows'])==4
    assert original_pairs['sourceSHA256ByUid'][UID]==SHA and original_pairs['sourceSHA256ByUid'][OTHER]==identity['relatedSourceSHA256']
    assert all(r['uid']==UID and r['peerUid']==OTHER and r['completeSourceFaces']==680 and r['completePeerFaces']==26599 and r['contactDimensions']=={'1':28}for r in original_pairs['rows'])
    preview=P+'carpark-private-terrain-preview-v1-20261101';preview_summary=take(preview,'summary.json');assert preview_summary['previewOnly']and preview_summary['sourceSHA256ByUid']=={UID:SHA}and preview_summary['privateTerrainSHA256']==TERRAIN and preview_summary['fullAffectedBaseForms']==3
    images=[];reports=[]
    for width in [1280,390]:
        report=take(preview,str(width)+'/staged-browser.json');assert report['passed']and not report['errors'];views=[r for r in report['views']if 'time'in r];assert len(views)==2 and {r['time']for r in views}=={'15:00','22:00'}
        if width==390:assert any(r.get('phase')=='failed-download'and r['fallbackRetained']for r in report['views'])
        for view in views:
            assert view['uid']==view['pick']==view['collision']==UID and view['active']and view['fullyFramed']and view['sourceSHA256']==SHA and view['originalTriangles']==680 and view['selectionClosed']
            assert view['ground']==view['groundSampler']and not view['overflow']
            path=BASE/preview/str(width)/view['file'];assert digest(path.read_bytes())==pins[preview][str(path.relative_to(ROOT))];refs.append(path);images.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),actuallyViewed=True))
        reports.append(dict(width=width,passed=True,sourceViews=2,failedDownloadFallbackAndRetry=width==390))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==identity['currentManifestSHA256'];refs.append(manifest)
    for p,h in allpins.items():assert digest((ROOT/p).read_bytes())==h,p
    assert reservations.owns(lease)
    result=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),terrain=patch['candidate'],leaseResources=resources,supportByUid={},identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,completeFourWorldFoundations=True,qualifiedForLiveVerification=True,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,modelAndEffort='Unknown from tool-visible metadata; not inferred',reviewer='Codex ROOT',imagesActuallyInspected=images,browserReports=reports,currentSharedStructureContacts=contact_bounds,rawCurrentForeignContactsRetained=True,originalPairContactsRetained=True,currentFormSuppression=False,genericPolicyChanges=False,physicalAcceptance=True,installationApproved=False,publication=False,observations=['Only this exact carpark original and source-derived private terrain are qualified. Fresh government records explicitly join its sole overlapping Academic source through BuildingStructureID1732120/NT98/91. Stable CSUID/GeoRef/type/heights preserve the pinned source identity while changed live OBJECTIDs remain recorded, not silently substituted.','The16current base-actor line contacts occupy the shared-structure end junction, roughly2.47mby0.29m horizontally and HKPD118..119.630m. They are retained verbatim. Complete original-pair proofs independently measure28line contacts in every represented stream. Neither a zero-contact gate nor a generic interpenetration waiver is introduced. Distinct Academic source/basic identity and all source fields stay intact; it receives no import or source-role approval here.','All four actual desktop/mobile day/night exported canvases were inspected individually. The long original carpark, upper slab/roof housings, openings and stair/return forms are visible and framed beside the retained Academic basic mass; its short end connection is legible and its body remains visible. Night carpark surfaces retain procedural windows off while existing neighbours keep their lighting. No missing part is invented, source moved, neighbour suppressed or terrain failure hidden.','All680sourcefaces, complete4world foundations and all2370canonical samples are bound to the exact current ground. The remaining11partial below-grade walls are separately accepted by the inspected, original-cap/actual-grade/strict-low-rim source-role review; raw−1.9598msampledepth is retained. No upward/nonwall negative faces remain. Full3base-form regression passes, all7066installedactors were scoped, and no retained detailed actor or native terrain patch is touched.','This is source/scene qualification only. The complete canonical publisher dry run, exact qualified-stage desktop/mobile lifecycle, fenced transaction/snapshot/global retained-support checks, actual installed HTTP/collision/fallback verification and Neon readback remain mandatory before installation credit. No optimisation or generated asset tier is authorised.'])
    save(out/'ROOT-SOURCE-REVIEW.json',result);save(out/'summary.json',result)
    module('carpark_original_qualification',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-carpark-source-physical-neighbour-and-browser-qualification',refs,result)

if __name__=='__main__':main()

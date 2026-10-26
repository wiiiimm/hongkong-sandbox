"""Assemble authenticated source/physical/visual decisions; does not install assets."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
PREFIX='government-xl-after-pok-oi-tuen-mun-'
DATE='-20261026'
BATCH=PREFIX+'closed-source-review-v1'+DATE

def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(name,file):
        n=PREFIX+name+DATE
        if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
        p=BASE/n/file;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    physical=take('closed-physical-source-review-v3','ROOT-PHYSICAL-REVIEW.json');identity=take('closed-compound-identity-review-v1','ROOT-COMPOUND-IDENTITY-REVIEW.json');sheets=take('retained-browser-contact-sheets-v1','summary.json');native=take('retained-replacement-neighbours-v1','summary.json')
    manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest)
    assert physical['currentManifest']==ref(manifest)and identity['currentManifestSHA256']==ref(manifest)['sha256']
    assert physical['sourceSHA256ByUid']==identity['sourceSHA256ByUid']and len(identity['sourceSHA256ByUid'])==12
    for key in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance']:assert physical[key]
    assert identity['identityAccepted']and all(all(v[k]for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted'])for v in identity['identityProofByUid'].values())
    assert native['forms']==247 and set(native['requiredNativeUids'])==set(native['nativeResolved'])==set(physical['retainedNativeUids'])
    images=[];retained=[]
    for image in sheets['images']:
        p=ROOT/image['path'];assert digest(p.read_bytes())==image['sha256'];refs.append(p)
        record={k:image[k]for k in ['uid','width','time','path','sha256']}
        (images if image['kind']=='source' else retained).append(record)
    assert len(images)==48 and len(retained)==12
    assert {(r['uid'],r['width'],r['time'])for r in images}=={(u,w,t)for u in identity['sourceSHA256ByUid']for w in [390,1280]for t in ['15:00','22:00']}
    assert physical['contactSheetsActuallyInspected']==sheets['sheets']
    reports=[]
    for width in [1280,390]:
        report=take('retained-terrain-private-browser-v5',str(width)+'/staged-browser.json');assert report['passed']and not report['errors'];reports.append(ref(BASE/(PREFIX+'retained-terrain-private-browser-v5'+DATE)/str(width)/'staged-browser.json'))
    result={**physical,'identityProofByUid':identity['identityProofByUid'],'completeCurrentNeighbourChecks':247,'retainedNativeRegression':native,'imagesActuallyViewed':images,'retainedImagesActuallyViewed':retained,'browserReports':reports,'physicalReview':ref(BASE/(PREFIX+'closed-physical-source-review-v3'+DATE)/'ROOT-PHYSICAL-REVIEW.json'),'imageInspectionMethod':'Actual exported pixels inspected via16 immutable uncropped1x contact sheets, not48 individually opened source files. Complete earlier ROOT physical review binds the observations.','installationApproved':False,'publication':False}
    save(out/'ROOT-SOURCE-REVIEW.json',result)
    module('tuen_mun_closed_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'closed-original-source-physical-visual-review-binding',refs,result)

if __name__=='__main__':main()

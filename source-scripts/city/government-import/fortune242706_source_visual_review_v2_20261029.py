"""Bind ROOT's four inspected Fortune exports to the exact passing physical review."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from fortune242706_final_physical_review_v1_20261029 import UID,SOURCE,BATCH as PHYSICAL
BATCH='government-xl-fortune242706-source-visual-review-v2-20261029'
BROWSER='government-xl-fortune242706-final-private-preview-v3-20261029'

def main():
    base=ROOT/'docs/astra-city/government-import';out=base/BATCH
    assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,p):
        if batch not in pins:
            pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p)
        return read(p)
    physical=take(PHYSICAL,base/PHYSICAL/'ROOT-PHYSICAL-REVIEW.json')
    assert all(physical[k] for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','completeFourWorldFoundations','noClearanceExceptionUsed'])
    assert physical['sourceSHA256ByUid']=={UID:SOURCE} and physical['completeCurrentNeighbourChecks']==28
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    assert physical['currentManifest']==dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes()));refs.append(manifest)
    images=[];reports=[]
    for width in [1280,390]:
        path=base/BROWSER/str(width)/'staged-browser.json';report=take(BROWSER,path)
        assert report['passed']and not report['errors'];reports.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
        views=[v for v in report['views']if 'time'in v];assert len(views)==2
        for v in views:
            assert v['uid']==UID and v['sourceSHA256']==SOURCE
            assert v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==UID
        assert report['jointViews']and all(len(j['models'])==1 and all(m['uid']==UID and m['sourceSHA256']==SOURCE and m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])for j in report['jointViews'])
        for time in [1500,2200]:
            image=base/BROWSER/str(width)/f'staged-landsd-242706-0-{width}-{time}-canvas.png'
            assert digest(image.read_bytes())==pins[BROWSER][str(image.relative_to(ROOT))];refs.append(image)
            images.append(dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes())))
    result=dict(uids=[UID],sourceSHA256ByUid={UID:SOURCE},requiredOriginalAssembly=[UID],identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,currentManifest=physical['currentManifest'],imagesActuallyViewed=images,browserReports=reports,visualAcceptance=True,installationApproved=False,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,reviewer='Codex ROOT',qualification='ROOT inspected all four actual V3 desktop/mobile day/night exports. Complete mall roof, facade, attached pedestrian bridges and current neighbourhood are visible; the higher phone camera avoids the prior tower occlusion. Night original remains unlit, with no fabricated procedural windows. Exact source, ordinary four-world foundations/rims and all 28 retained neighbours pass. Guarded publication and live verification remain mandatory.')
    save(out/'ROOT-SOURCE-REVIEW.json',result)
    module('fortune_visual_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-fortune-original-source-physical-visual-review',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()

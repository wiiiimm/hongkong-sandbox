"""Combine completed desktop/mobile evidence and ROOT's actual image review."""
from pathlib import Path
import shutil
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-times-square-browser-review-v2-20261019'
DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
    assert not DOC.exists()
    folders=[BASE/('government-xl-times-square-assembly-browser-'+s+'-20261019')for s in ['mobile-v2','desktop-v1']]
    pins,refs={},[Path(__file__)]
    with connect()as c:
        c.execute('SET TRANSACTION READ ONLY')
        for d in folders:
            receipt=read(d/'result.json')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
            refs.append(d/'result.json')
            for e in receipt['evidenceRefs']:
                assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
    merged=dict(mode='staged',views=[],retainedNativeOwnViews=[],jointViews=[],errors=[],passed=True)
    catalogue=None;images=[]
    for d,width in zip(folders,[390,1280]):
        assert read(d/'command.json')['exitCode']==0
        cat=read(HERE/'local'/d.name/'catalogue.json')
        if catalogue is None:catalogue=cat
        else:assert cat==catalogue
        sources={e['uid']:e for e in cat['models']};assert len(sources)==3
        assert all(e['proceduralWindows']is False for e in sources.values())
        report=read(d/'staged-browser.json');assert report['passed'] and not report['errors']
        views=[v for v in report['views']if 'time'in v]
        assert len(views)==6 and {(v['uid'],v['time'],v['width'])for v in views}=={(u,t,width)for u in sources for t in ['15:00','22:00']}
        for v in views:
            assert v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']
            assert v['pick']==v['collision']==v['uid'] and v['sourceSHA256']==sources[v['uid']]['sha256']
            assert v['originalTriangles']==sources[v['uid']]['triangles'] and v['fallbackFaces']==0
        retained=report.get('retainedNativeOwnViews',[]);assert len(retained)==0
        assert {(v['uid'],v['time'],v['width'])for v in retained}=={(u,t,width)for u in []for t in ['15:00','22:00']}
        assert all(v['active']and v['visible']and v['fullyFramed']and v['fallbackFaces']==0 for v in retained)
        assert len(report['jointViews'])==3 and {j['selectedUid']for j in report['jointViews']}==set(sources)
        for joint in report['jointViews']:
            assert joint['width']==width and len(joint['models'])==3 and {m['uid']for m in joint['models']}==set(sources)
            for m in joint['models']:
                assert m['active']and m['visible']and m['fallbackFaces']==0
                assert m['sourceSHA256']==sources[m['uid']]['sha256']and m['originalTriangles']==sources[m['uid']]['triangles']
        if width==390:assert any(v.get('phase')=='failed-download'and v['fallbackRetained']for v in report['views'])
        for v in views+retained:
            p=d/v['file'];target=DOC/v['file'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
            assert digest(target.read_bytes())==digest(p.read_bytes());images.append(ref(target))
        for key in ['views','retainedNativeOwnViews','jointViews']:merged[key].extend(report.get(key,[]))
    save(DOC/'staged-browser.json',merged)
    save(DOC/'ROOT-IMAGE-REVIEW.json',dict(reviewer='Codex ROOT',visualAcceptance=True,
        stagedBrowser=ref(DOC/'staged-browser.json'),currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),
        imagesActuallyViewed=images,sourceCatalogue=ref(HERE/'local'/folders[1].name/'catalogue.json'),
        observations=['Original Times Square towers and podium are solid and aligned at their unchanged source positions in the reverse-angle assembly views.','Day/night captures preserve the new originals without procedural window skins; existing neighbouring skins are unchanged.','No installed native neighbours intersect the changed terrain area. Normal surrounding-building occlusion partly obscures the podium in assembly views; separate original-source closeups document its seams and outer platform.','Numeric picking, collision, source face count, source hash, fallback removal and mobile failed-download/retry checks pass in the unchanged test assertions.'],
        aiGeometryModelling=False,installationApproved=False))
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
    module('pacifica_browser_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'completed-split-desktop-mobile-original-viewer-review',list(dict.fromkeys(refs)),dict(uids=list(sources),views=12,retainedViews=0,visualAcceptance=True,installationApproved=False))
if __name__=='__main__':main()

"""Combine completed desktop/mobile evidence and ROOT's actual image review."""
from pathlib import Path
import shutil
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-kai-tak-cruise-browser-review-v1-20261019'
DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
    assert not DOC.exists()
    folders=[BASE/'government-xl-kai-tak-cruise-assembly-browser-390-v4-20261019',BASE/'government-xl-kai-tak-cruise-assembly-browser-1280-v1-20261019']
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
        sources={e['uid']:e for e in cat['models']};assert len(sources)==14
        assert all(e['proceduralWindows']is False for e in sources.values())
        report=read(d/'staged-browser.json');assert report['passed'] and not report['errors']
        views=[v for v in report['views']if 'time'in v]
        assert len(views)==28 and {(v['uid'],v['time'],v['width'])for v in views}=={(u,t,width)for u in sources for t in ['15:00','22:00']}
        for v in views:
            assert v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']
            assert v['pick']==v['collision']==v['uid'] and v['sourceSHA256']==sources[v['uid']]['sha256']
            assert v['originalTriangles']==sources[v['uid']]['triangles'] and v['fallbackFaces']==0
        retained=report.get('retainedNativeOwnViews',[]);assert len(retained)==2
        assert {(v['uid'],v['time'],v['width'])for v in retained}=={(u,t,width)for u in ['landsd/299814:0']for t in ['15:00','22:00']}
        assert all(v['active']and v['visible']and v['fullyFramed']and v['fallbackFaces']==0 for v in retained)
        assert len(report['jointViews'])==14 and {j['selectedUid']for j in report['jointViews']}==set(sources)
        for joint in report['jointViews']:
            assert joint['width']==width and len(joint['models'])==1 and {m['uid']for m in joint['models']}=={'landsd/263423:0'}
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
        observations=['ROOT inspected all 30 desktop exports and all 30 mobile exports using contact sheets, plus the full desktop terminal PNG. Original roof components are solid and visible without procedural window skin; night views retain dark source silhouettes.', 'Whole-terminal mobile view is distant and side-on to remain inside the existing mobile detail range; close component views and desktop whole view provide complementary evidence. This does not certify a simultaneous 14-model wide mobile presentation.', 'The apparent dense roof blocks are separate neighbours: the current 218-form footprint audit locates 198 non-terminal forms with zero terminal footprint overlap. They are retained, not suppressed.', 'Retained substation own views remain available. Existing substation window appearance and shoreline faceting are unchanged and are not reapproved as new source work.', 'Runtime assertions cover source hashes, face counts, picking, collision, fallback removal and failed-download/retry; joint assertions cover terminal presence during each component view, not all 14 sources simultaneously.'],
        aiGeometryModelling=False,installationApproved=False))
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
    module('pacifica_browser_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'completed-split-desktop-mobile-original-viewer-review',list(dict.fromkeys(refs)),dict(uids=list(sources),views=56,retainedViews=4,visualAcceptance=True,installationApproved=False))
if __name__=='__main__':main()

"""Combine completed desktop/mobile evidence and ROOT's actual image review."""
from pathlib import Path
import shutil
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-ifc-mall-browser-review-v1-20261019'
DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
    assert not DOC.exists()
    folders=[BASE/('government-xl-ifc-mall-assembly-browser-'+s+'-20261019')for s in ['mobile-v3','desktop-v3']]
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
        sources={e['uid']:e for e in cat['models']};assert len(sources)==1
        assert all(e['proceduralWindows']is False for e in sources.values())
        report=read(d/'staged-browser.json');assert report['passed'] and not report['errors']
        views=[v for v in report['views']if 'time'in v]
        assert len(views)==2 and {(v['uid'],v['time'],v['width'])for v in views}=={(u,t,width)for u in sources for t in ['15:00','22:00']}
        for v in views:
            assert v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']
            assert v['pick']==v['collision']==v['uid'] and v['sourceSHA256']==sources[v['uid']]['sha256']
            assert v['originalTriangles']==sources[v['uid']]['triangles'] and v['fallbackFaces']==0
        retained=report.get('retainedNativeOwnViews',[]);assert len(retained)==4
        assert {(v['uid'],v['time'],v['width'])for v in retained}=={(u,t,width)for u in ['landsd/161250:0','landsd/232441:0']for t in ['15:00','22:00']}
        assert all(v['active']and v['visible']and v['fullyFramed']and v['fallbackFaces']==0 for v in retained)
        expected={'landsd/161250:0':('08619d248f38cd2b2f48a6cafe8119e00c9e22d9ac58e9e7d1441b35e051a27c',4271),'landsd/232441:0':('fe5dcc43172a4c131c90a1e5f21f33564479912c4016e88e8784175a062d99f4',2167)}
        assert all((v['sourceSHA256'],v['originalTriangles'])==expected[v['uid']]for v in retained)
        assert len(report['jointViews'])==1 and {j['selectedUid']for j in report['jointViews']}==set(sources)
        for joint in report['jointViews']:
            assert joint['width']==width and len(joint['models'])==1 and {m['uid']for m in joint['models']}==set(sources)
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
        observations=['ROOT inspected all12 exported v3 images: mall day/night at390/1280 plus both retained originals day/night at390/1280. The mall arched roof, end blocks and side extensions are visible in context; original pose is unchanged.', 'Revised retained views expose the One IFC podium base and bridges; the tower naturally occludes part of its own podium, but the unrelated foreground obstruction in v2 is removed. Tower and podium keep their existing materials. No claim is made that these views fix historical tower support diagnostics.', 'The new mall has procedural windows disabled. Night imagery is appropriately dark; nearby buildings continue their existing lighting and loading transitions. Numeric picking/collision, source bytes/triangles, fallback and mobile failed-download/retry checks pass.'],
        aiGeometryModelling=False,installationApproved=False))
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
    module('pacifica_browser_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'completed-split-desktop-mobile-original-viewer-review',list(dict.fromkeys(refs)),dict(uids=list(sources),views=4,retainedViews=8,visualAcceptance=True,installationApproved=False))
if __name__=='__main__':main()

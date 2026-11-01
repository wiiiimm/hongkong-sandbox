"""Bind actual ROOT sheet inspection to every installed HKUST live export."""
import argparse,os
from pathlib import Path
from PIL import Image,ImageDraw
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--observation',required=True);a=ap.parse_args()
    base=ROOT/'docs/astra-city/government-import';config=(ROOT/os.environ['ORIGINAL_INSTALL_CONFIG']).resolve();assert config.is_relative_to(base);cfg=read(config);sources=cfg['sources'];assert len(sources)==3 and not cfg.get('supportByUid')
    folder=base/(cfg['prefix']+'-retained-original-installed-v1-'+cfg['date']);receipt,pins=authenticate(folder);assert receipt['publication']and receipt['sourceSHA256ByUid']==sources and receipt['newlyInstalled']==1
    observation=(ROOT/a.observation).resolve();assert observation.is_relative_to(base);seen=read(observation);assert seen['reviewer']=='Codex ROOT'and seen['allDeclaredExportsActuallyInspected']and seen['limitations']
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json');current={m['uid']:m for url in manifest['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']}
    images=[];retained=[]
    for width in [1280,390]:
        reportpath=folder/f'viewport-{width}/live-browser.json';assert digest(reportpath.read_bytes())==pins[str(reportpath.relative_to(ROOT))];report=read(reportpath);assert report['passed']and not report['errors']
        views=[v for v in report['views']if 'time'in v];assert len(views)==2*len(sources)
        for v in views:
            assert v['uid']in sources and v['sourceSHA256']==sources[v['uid']]and v['pick']==v['collision']==v['uid']and v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and not v['overflow']
            assert all(v['meshVisibility'])and not any(v['wireframeFlags'])
            p=reportpath.parent/v['file'];r=dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),uid=v['uid'],width=width,time=v['time']);assert pins[r['path']]==r['sha256'];images.append(r)
        assert report['jointViews']and all({m['uid']:m['sourceSHA256']for m in j['models']}==sources and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])for j in report['jointViews'])
        own=report['retainedNativeOwnViews'];assert len(own)==2 and {(v['uid'],v['time'])for v in own}=={('landsd/26949:0',t)for t in ['15:00','22:00']}
        for v in own:
            expected=current[v['uid']];assert v['active']and v['visible']and v['fullyFramed']and not v['fallbackFaces']and v['sourceSHA256']==expected['sha256']and v['originalTriangles']==expected['triangles'];assert all(v['meshVisibility'])and not any(v['wireframeFlags'])
            p=reportpath.parent/v['file'];r=dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),uid=v['uid'],width=width,time=v['time']);assert pins[r['path']]==r['sha256'];retained.append(r)
    atomic=read(folder/'atomic-lifecycle/report.json');assert atomic['passed']and not atomic['pageErrors']and len(atomic['cases'])==4
    assert {c['failedUid']for c in atomic['cases']if c['width']==390}==set(sources)
    assert all(c['baseOnlyRestoredCompleteGroup']and c['completeGroupEvicted']and not c['audit']['violations']for c in atomic['cases'])
    extra=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in sorted((folder/'atomic-lifecycle').glob('*.png'))];assert len(extra)==11
    for r in extra:assert pins[r['path']]==r['sha256']
    def pairs(rows):return {(r['path'],r['sha256'])for r in rows}
    assert len(images)==12 and len(retained)==4 and pairs(images)==pairs(seen['imagesActuallyViewed'])and pairs(retained)==pairs(seen['retainedImagesActuallyViewed'])and pairs(extra)==pairs(seen['atomicImagesActuallyViewed'])
    observed=[]
    for sheet in seen['inspectionSheetsActuallyViewed']:
        path=(ROOT/sheet['path']).resolve();assert path.is_relative_to(base)and digest(path.read_bytes())==sheet['sha256']and sheet['actuallyViewed']is True
        positions=sheet['placements'];assert 1<=len(positions)<=4
        originals=[Image.open(ROOT/r['path']).convert('RGB')for r in positions];w=max(im.width for im in originals);h=max(im.height for im in originals)+30;canvas=Image.new('RGB',(2*w,2*h),'white');draw=ImageDraw.Draw(canvas)
        for i,(r,im)in enumerate(zip(positions,originals)):
            assert digest((ROOT/r['path']).read_bytes())==r['sha256'];assert r['sourcePixelsResized']is False and r['widthPixels']==im.width and r['heightPixels']==im.height
            x=(i%2)*w;y=(i//2)*h;assert (r['x'],r['y'])==(x,y+30);draw.text((x+3,y+3),Path(r['path']).name,fill='black');canvas.paste(im,(x,y+30));observed.append(r)
        actual=Image.open(path).convert('RGB');assert actual.size==canvas.size and actual.tobytes()==canvas.tobytes()
    assert len(observed)==27 and pairs(observed)==pairs(images+retained+extra)
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    target=folder/'ROOT-LIVE-EXPORT-INSPECTION.json';assert not target.exists()
    save(target,dict(reviewer='ROOT',visualAcceptance=True,producer=ref(Path(__file__)),imagesActuallyViewed=images,retainedImagesActuallyViewed=retained,atomicImagesActuallyViewed=extra,inspectionSheetsActuallyViewed=seen['inspectionSheetsActuallyViewed'],inspectionMethod='All27 declared installed exports actually inspected through seven exact full-copy sheets; source pixels were not resized. No claim of individually opening27 source PNGs.',observations=seen['limitations'],boundObservation=ref(observation),aiGeometryModelling=False))
    print(dict(sourceImages=12,retainedImages=4,atomicImages=11,installedJobId=receipt['jobId']))
if __name__=='__main__':main()

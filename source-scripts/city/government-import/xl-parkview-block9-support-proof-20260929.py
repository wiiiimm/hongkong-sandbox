"""Revalidate unchanged Block 9 contact with the currently installed podium."""
from pathlib import Path
from shapely.geometry import MultiPoint, Polygon
from run import ROOT, HERE, read, save, digest

BASE=ROOT/'docs/astra-city/government-import/government-xl-remaining-20260923'
UID='landsd/255439:0'
SUPPORT='landsd/254491:0'

def run():
    old=BASE/'parkview-terrain-diagnostic-20260925'
    probe_path=old/'support-probe-refined.json'
    assert digest(probe_path.read_bytes())==read(old/'support-proof.json')['probeSHA256']
    probe=next(r for r in read(probe_path)['rows'] if r['uid']==UID)
    selected=read(BASE/'parkview-block9-terrain-diagnostic-20260929/selection.json.gz')['rows'][0]
    entry=selected['candidate']['entry']
    assert entry['sha256']==probe['sourceSHA256']==digest(Path(selected['candidate']['path']).read_bytes())
    installed=[]
    for url in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues']:
        for model in read(ROOT/'3d-viewer'/url)['models']:
            if model['uid']==SUPPORT:installed.append((url,model))
    assert len(installed)==1
    url,support=installed[0]
    asset=(ROOT/'3d-viewer'/url).parent/support['asset']
    assert probe['supportSHA256']==support['sha256']==digest(asset.read_bytes())
    form=selected['source']['building']
    polygon=Polygon(form['rings'][0],form['rings'][1:])
    hull=MultiPoint([(x,z) for x,_,z in probe['contactPositions']]).convex_hull
    coverage=hull.intersection(polygon).area/polygon.area
    assert probe['within05']>=100 and coverage>=.85
    save(BASE/'parkview-block9-support-proof-20260929.json',{
        'uid':UID,'supportUid':SUPPORT,'sourceSHA256':entry['sha256'],'supportSHA256':support['sha256'],
        'supportCatalogue':url,'supportAsset':str(asset.relative_to(ROOT)),
        'contactHullTargetCoverage':coverage,'within05':probe['within05'],
        'probeSHA256':digest(probe_path.read_bytes()),'passed':True,
        'aiCalls':0,'modelGeometryChanges':0,'publication':False})
    print({'uid':UID,'support':SUPPORT,'contactSamples':probe['within05'],'coverage':coverage},flush=True)

if __name__=='__main__':run()

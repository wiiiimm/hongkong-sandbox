"""Measure complete terrain-envelope retention closure before designing a replacement."""
from pathlib import Path
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';name='government-xl-island-industrial-pair-current-v1-20261023-scope'
    batch='government-xl-island-industrial-retention-closure-v1-20261023';out=base/batch;assert not out.exists()
    _,pins=authenticate(base/name);sp=base/name/'scope.json';assert digest(sp.read_bytes())==pins[str(sp.relative_to(ROOT))]
    mp=ROOT/'3d-viewer/city/data/manifest.json';assert digest(mp.read_bytes())==pins[str(mp.relative_to(ROOT))]
    refs=[Path(__file__),base/name/'result.json',sp,mp];parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);refs.append(parentpath)
    builder=module('retention_closure_bounds',HERE/'validated_parent_roundoff_template_v2.py')
    nodes=[]
    def faces(n):return len(n.get('nativeMesh',{}).get('index',[]))//3+sum(faces(p)for p in n.get('patches',[]))
    for entry in read(mp)['terrainPatches']:
        path=ROOT/'3d-viewer'/entry['url'];node=read(path);refs.append(path)
        nodes.append(dict(url=entry['url'],sha256=digest(path.read_bytes()),bounds=builder.extent(node['coarseCells'],parent),coarseCells=node['coarseCells'],nativeFaces=faces(node),targets=node['meta'].get('targetUids',[])))
    bounds=read(sp)['regionalParentExtent'];history=[];selected=set()
    for step in range(len(nodes)+1):
        domain=shapely.box(*bounds)
        current=[r for r in nodes if domain.intersection(shapely.box(*r['bounds'])).area>0]
        urls={r['url']for r in current};assert selected<=urls
        history.append(dict(step=step,bounds=bounds,patches=len(current),nativeFaces=sum(r['nativeFaces']for r in current),urls=sorted(urls)))
        if urls==selected:break
        selected=urls;bounds=[min([bounds[0]]+[r['bounds'][0]for r in current]),min([bounds[1]]+[r['bounds'][1]for r in current]),max([bounds[2]]+[r['bounds'][2]for r in current]),max([bounds[3]]+[r['bounds'][3]for r in current])]
    else:raise AssertionError('Finite catalogue closure did not converge')
    result=dict(uids=read(sp)['uids'],closure=history,requiredRetainedPatches=[r for r in nodes if r['url']in selected],sourceGeometryChanges=0,installationApproved=False,qualification='Whole existing coarse-envelope closure nomination only. No mesh edits, retention approval, template construction or publication; complete rendered packed contacts still require independent checks.')
    save(out/'summary.json',result);refs.append(HERE/'validated_parent_roundoff_template_v2.py')
    module('retention_closure_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'complete-existing-terrain-envelope-closure-diagnostic',refs,result)
    print([{k:v for k,v in row.items()if k!='urls'}for row in history],flush=True)


if __name__=='__main__':main()

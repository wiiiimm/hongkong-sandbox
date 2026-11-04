"""Read-only finite-domain coverage and clamp diagnostics for the two authentic TINs."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-next-repairs-two-original-terrain-domain-diagnostics-v1-20261023';out=base/batch;assert not out.exists()
    refs=[Path(__file__)];pins={}
    def take(name,path):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    decoder=module('domain_source_terrain',HERE/'xl-second-pass.py');builder=module('domain_clipper',HERE/'resolve-pass-indexed-parent-clipping.py');results=[]
    for label,uid in [('hanford-plaza-276187','landsd/276187:0'),('west-kowloon-bus-255415','landsd/255415:0')]:
        prefix='government-xl-next-repairs-'+label;subset=prefix+'-terrain-subset-v1-20261023';trial=prefix+'-original-terrain-trial-v1-20261023'
        checked=take(subset,base/subset/'summary.json')['rows'][0];assert checked['uid']==uid
        scope=take(trial,base/trial/'scope.json');bounds=scope['bounds'];parts=[]
        for filename in checked['sourceTerrainPaths']:
            path=ROOT/filename;gltf=take(subset,path)
            for b in gltf.get('buffers',[]):
                p=path.parent/b['uri'];assert digest(p.read_bytes())==pins[subset][str(p.relative_to(ROOT))];refs.append(p)
            parts.append(decoder.terrain_triangles(path))
        terrain=np.concatenate(parts);lo,hi=terrain[:,:,[0,2]].min(1),terrain[:,:,[0,2]].max(1);selected=terrain[(hi[:,0]>=bounds[0])&(lo[:,0]<=bounds[2])&(hi[:,1]>=bounds[1])&(lo[:,1]<=bounds[3])]
        clipped=[];witness=[]
        for i,t in enumerate(selected):
            poly=builder.exact.rect(list(t),bounds)
            for j in range(1,len(poly)-1):
                face=np.array([poly[0],poly[j],poly[j+1]])
                if shapely.MultiPoint(face[:,[0,2]]).convex_hull.area>0:
                    clipped.append(face);witness.append(i)
        assert clipped;clipped=np.array(clipped)
        polygons=shapely.polygons(clipped[:,:,[0,2]]);domain=shapely.box(*bounds);union=shapely.union_all(polygons)
        result=dict(uid=uid,sourceSHA256=checked['sourceSHA256'],bounds=bounds,originalSelectedTriangles=len(selected),originalSelectedMinY=float(selected[:,:,1].min()),finiteClippedTriangles=len(clipped),finiteClippedMinY=float(clipped[:,:,1].min()),clippedVerticesBelowClamp=int(np.count_nonzero(clipped[:,:,1]<1.2)),uncoveredDomainAreaM2=float(domain.difference(union).area),outsideDomainAreaM2=float(union.difference(domain).area),qualification='Finite clipping diagnostic only. No inferred approval, source corruption, clamp or coverage waiver.',installationApproved=False)
        save(out/(uid.split('/')[1]+'-clipped-facets.json.gz'),dict(originalFaceIds=witness,triangles=clipped.tolist()));results.append(result)
    result=dict(uids=[r['uid']for r in results],rows=results,sourceGeometryChanges=0,installationApproved=False,publication=False)
    save(out/'summary.json',result);refs.extend([HERE/'xl-second-pass.py',HERE/'resolve-pass-indexed-parent-clipping.py',HERE.parent/'assembly-support-review/exact_tin.py'])
    module('domain_clamp_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'finite-authentic-terrain-domain-clamp-diagnostic',refs,result)
    print(results,flush=True)


if __name__=='__main__':main()

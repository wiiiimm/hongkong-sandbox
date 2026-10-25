"""Identify the extra drawn terrain layer at one real residual burial witness."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from ronsdale_local_inset_v2_20261022 import plane


def main():
    base=ROOT/'docs/astra-city/government-import'
    prefix='government-xl-podium323546-after-beverly-d-'
    batch=prefix+'group-terrain-owner-v1-20261026';out=base/batch
    assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:
            _,pins[batch]=authenticate(base/batch);refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    runtime=prefix+'inset-runtime-v2-20261026';patch=prefix+'clamped-original-inset-v7-20261026'
    g=take(runtime,HERE/'local'/runtime/'runtime-geometry.json.gz')['rows'][0]
    candidate=take(patch,HERE/'local'/patch/'candidate-terrain.json')
    old=take(runtime,base/runtime/'selection.json.gz')['rows'][0]
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath)
    assert digest(manifestpath.read_bytes())==take(runtime,base/runtime/'selection.json.gz')['manifestSHA256']
    refs.append(manifestpath)
    source=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    face=source[558];point=face.mean(0);xz=shapely.Point(point[0],point[2])
    ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
    def heights(triangles):
        polygons=shapely.polygons(triangles[:,:,[0,2]])
        ids=shapely.STRtree(polygons).query(xz,predicate='intersects');rows=[]
        for i in ids:
            if polygons[i].area<=1e-10:continue
            coefficients=plane(triangles[i]);height=float(point[[0,2]]@coefficients[:2]+coefficients[2])
            rows.append(dict(face=int(i),heightM=height,vertices=triangles[i].tolist()))
        assert rows;return rows
    current=heights(ground)
    proposed=heights(np.asarray(candidate['nativeMesh']['position']).reshape(-1,3)[np.asarray(candidate['nativeMesh']['index']).reshape(-1,3)])
    url='city/data/government-native-central-piers-original-v1-20261021.json'
    assert url in {r['url']for r in manifest['terrainPatches']}
    path=ROOT/'3d-viewer'/url;node=read(path);refs.append(path)
    geo=node['meta']['georef'];c=int(np.floor((point[0]+834500-geo['bE'])/geo['aE']))
    r=int(np.floor((816500-point[2]-geo['bN'])/geo['aN']))
    assert 0<=c<node['w']-1 and 0<=r<node['h']-1
    assert not any(a<=c<b and d<=r<e for a,d,b,e in [n['coarseCells']for n in node['patches']])
    def vertex(x,y):
        i=y*node['w']+x;h=node['renderedElev'][i]
        assert np.isfinite(h)
        return np.asarray([geo['bE']+x*geo['aE']-834500,h,816500-(geo['bN']+y*geo['aN'])],dtype='float32').astype(float)
    a,b,c1,d=vertex(c,r),vertex(c,r+1),vertex(c+1,r),vertex(c+1,r+1)
    expected=[np.array([a,b,c1]),np.array([c1,b,d])]
    exact=[]
    for found in current:
        for triangle in expected:
            if sorted(map(tuple,found['vertices']))==sorted(map(tuple,triangle.tolist())):exact.append(found)
    assert len(exact)==1 and exact[0]['heightM']>point[1]+.5
    assert max(v['heightM']for v in proposed)<point[1]+.5
    native=take('government-xl-all-200-original-terrain-batch-v2-20261022',base/'government-xl-all-200-original-terrain-batch-v2-20261022/summary.json')
    terrain=next(row for row in native['rows']if row['uid']==g['uid'])
    assert terrain['sourceSHA256']==g['sourceSHA256'];parts=[]
    decoder=module('podium_terrain_owner_decoder',HERE/'xl-second-pass.py')
    for name in terrain['sourceTerrainPaths']:
        p=ROOT/name;metadata=take('government-xl-all-200-original-terrain-batch-v2-20261022',p)
        for buffer in metadata['buffers']:
            f=p.parent/buffer['uri'];assert digest(f.read_bytes())==pins['government-xl-all-200-original-terrain-batch-v2-20261022'][str(f.relative_to(ROOT))];refs.append(f)
        parts.append(decoder.terrain_triangles(p))
    original=heights(np.concatenate(parts))
    assert abs(max(v['heightM']for v in original)-max(v['heightM']for v in proposed))<1e-6
    result=dict(uids=[g['uid']],sourceSHA256=g['sourceSHA256'],sourceFace=558,sourceFaceVertices=face.tolist(),centroid=point.tolist(),runtimeLayers=current,privateCandidateLayers=proposed,originalTINLayers=original,extraLayerExactOwner=dict(url=url,sha256=digest(path.read_bytes()),gridCell=[c,r],mesh='5m group fallback; exact Float32 rendered triangle equality',triangle=exact[0]),retainedChildCount=len(node['patches']),installationApproved=False,publication=False,permanentRejection=False,newlyInstalled=0,sourceGeometryChanges=0,aiGeometryModelling=False,qualification='Residual burial includes an extra currently installed group fallback triangle, not an incorrectly imported source vertex or missing original terrain. Exact original TIN and private candidate agree at this witness. This single witness is not whole-model clearance, identity approval, or permission to remove the group. An explicit hierarchical replacement must retain all thirteen existing children and revalidate the complete changed domain.')
    save(out/'summary.json',result);refs.extend([HERE/'xl-second-pass.py',ROOT/'3d-viewer/city/world.js',ROOT/'3d-viewer/city/geo.js'])
    module('podium_owner_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-residual-burial-drawn-terrain-owner-diagnostic',refs,result)
    print(dict(extraLayerHeight=exact[0]['heightM'],candidateHeight=max(v['heightM']for v in proposed),sourceHeight=point[1],retainedChildren=len(node['patches'])),flush=True)

if __name__=='__main__':main()

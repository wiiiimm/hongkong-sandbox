"""Identify the three tolerated non-upward facets without inferring their role."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-peninsula-three-buried-facet-context-v1-20261029';RUNTIME='government-xl-peninsula-pair-current-v1-20261029-runtime';ATTR='government-xl-peninsula-pair-current-v1-20261029-attributes';UID='landsd/270876:0'
def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,p):
        if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    row=next(r for r in take(RUNTIME,BASE/RUNTIME/'selection.json.gz')['rows']if r['uid']==UID);g=next(r for r in take(RUNTIME,HERE/'local'/RUNTIME/'runtime-geometry.json.gz')['rows']if r['uid']==UID);attr=next(r for r in take(ATTR,BASE/ATTR/'attributes.json.gz')['rows']if r['uid']==UID);path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==row['sourceSHA256']==g['sourceSHA256']==attr['sourceSHA256'];refs.append(path);index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds=dict(original=decode_original_world_triangles(path.read_bytes()),literal=np.asarray(attr['completeLiteralWorldPosition']).reshape(-1,3)[index],explicitLeftF32=np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1,3)[index],explicitBalancedF32=np.asarray(attr['completeExplicitBalancedFloat32WorldPosition']).reshape(-1,3)[index]);ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);final=module('peninsula_exact_buried_context',HERE/'xl-final-script-pass.py');foundation='government-xl-peninsula-pair-current-v1-20261029-foundation-270876-0';rows=[]
    for mode,tri in worlds.items():
        expected=take(foundation,BASE/foundation/(mode+'.json'));assert digest(tri.astype('<f8').tobytes())==expected['sourceWorldSHA256'];lo,hi=tri.min((0,1)),tri.max((0,1));native=ground[(ground[:,:,0].max(1)>=lo[0]-1)&(ground[:,:,0].min(1)<=hi[0]+1)&(ground[:,:,2].max(1)>=lo[2]-1)&(ground[:,:,2].min(1)<=hi[2]+1)];polys=shapely.polygons(native[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;native,polys=native[valid],polys[valid];points=np.concatenate([tri,tri.mean(1)[:,None,:]],axis=1);heights=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),native,shapely.STRtree(polys)).reshape(-1,4);gaps=points[:,:,1]-heights;mask=np.isfinite(heights).all(1)&(gaps<-.5).all(1);ids=np.flatnonzero(mask);assert len(ids)==expected['foundation']['fullyBuriedTriangles']==3
        records=[]
        for i in ids:
            f=tri[i];n=np.cross(f[1]-f[0],f[2]-f[0]);norm=np.linalg.norm(n);records.append(dict(sourceFace=int(i),vertices=f.tolist(),areaM2=float(norm/2),signedNormalYRatio=float(n[1]/norm),sampleGapsM=gaps[i].tolist()))
        rows.append(dict(mode=mode,sourceWorldSHA256=expected['sourceWorldSHA256'],buriedFacets=records));print(dict(mode=mode,faces=[r['sourceFace']for r in records],normalY=[r['signedNormalYRatio']for r in records]),flush=True)
    result=dict(uids=[UID],sourceSHA256=row['sourceSHA256'],rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,correctionTo='government-xl-peninsula-authored-assembly-role-review-v1-20261029',qualification='Exact ordinary-foundation sampler replay identifies all three fully buried facets and their signed normals in every coordinate stream. The earlier role-review phrase downward basal closures was an inference not established by the aggregate upward-count metric; these full facet records supersede that label. Existing complete-ground/zero-upward-burial/area policy remains passed without threshold changes. Upper28-facade authored-joint review is unaffected. No component role, additional structural credit, source geometry edit or installation approval follows.')
    save(out/'summary.json',result);refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py']);module('peninsula_three_low_facet_context',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-three-low-facet-identification-and-aggregate-orientation-wording-correction',refs,result)
if __name__=='__main__':main()

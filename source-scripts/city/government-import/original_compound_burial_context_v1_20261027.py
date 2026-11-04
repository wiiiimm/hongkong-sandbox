"""Locate existing compound-burial flags and exact source-edge components."""
import argparse
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','attributes','strict-support']:parser.add_argument('--'+key,required=True)
    a=parser.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-') and '/' not in a.batch and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    strict=take(a.strict_support,base/a.strict_support/'summary.json');uids=[strict['supportedUid'],strict['supportUid']]
    selected={r['uid']:r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']}
    attributes=take(a.attributes,base/a.attributes/'attributes.json.gz');assert attributes['startEndAllInputsVerified'];attrs={r['uid']:r for r in attributes['rows']}
    geometry={r['uid']:r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']}
    worlds={name:{} for name in ['original','literal','leftF32','balancedF32']}
    fields=dict(literal='completeLiteralWorldPosition',leftF32='completeExplicitLeftAssociatedFloat32WorldPosition',balancedF32='completeExplicitBalancedFloat32WorldPosition')
    for uid in uids:
        source=selected[uid];path=ROOT/source['candidate']['path'];assert digest(path.read_bytes())==source['sourceSHA256']==strict['sourceSHA256ByUid'][uid]==attrs[uid]['sourceSHA256'];refs.append(path)
        worlds['original'][uid]=decode_original_world_triangles(path.read_bytes());index=np.asarray(attrs[uid]['completeOriginalIndex']).reshape(-1,3)
        for mode,field in fields.items():worlds[mode][uid]=np.asarray(attrs[uid][field],float).reshape(-1,3)[index]
    ground=np.asarray(geometry[uids[0]]['drawnGroundGeometry']).reshape(-1,3,3)
    kernel=module('compound_burial_existing_kernel',HERE/'xl-final-script-pass.py');refs.append(HERE/'xl-final-script-pass.py');rows=[]
    for mode,world in worlds.items():
        tri=world[uids[0]];support=np.concatenate([ground,world[uids[1]]]);lo,hi=tri.min((0,1)),tri.max((0,1))
        support=support[(support[:,:,0].max(1)>=lo[0]-1)&(support[:,:,0].min(1)<=hi[0]+1)&(support[:,:,2].max(1)>=lo[2]-1)&(support[:,:,2].min(1)<=hi[2]+1)]
        polygons=shapely.polygons(support[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10;support=support[valid];polygons=polygons[valid]
        points=np.concatenate([tri,tri.mean(1)[:,None,:]],axis=1);heights=kernel.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),support,shapely.STRtree(polygons)).reshape(-1,4)
        gaps=points[:,:,1]-heights;ids=np.flatnonzero(np.isfinite(heights).all(1)&(gaps<-.5).all(1))
        before=next(r for r in strict['rows'] if r['mode']==mode);assert before['sourceWorldSHA256ByUid'][uids[0]]==digest(tri.tobytes())
        assert len(ids)==before['compoundFoundation']['fullyBuriedTriangles']
        normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);sizes=np.linalg.norm(normals,axis=1)
        parent=list(range(len(tri)))
        def root(i):
            while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
            return i
        edges={}
        for i,t in enumerate(tri):
            if sizes[i]==0:continue
            v=list(map(tuple,t))
            for x,y in zip(v,v[1:]+v[:1]):
                if x==y:continue
                edge=tuple(sorted((x,y)))
                if edge in edges:parent[root(i)]=root(edges[edge])
                else:edges[edge]=i
        members=defaultdict(list)
        for i in range(len(tri)):
            if sizes[i]>0:members[root(i)].append(i)
        components={};faces=[]
        for i in ids:
            i=int(i);component=root(i);values=tri[members[component]]
            components[str(component)]=dict(faces=len(values),bounds=[values.min((0,1)).tolist(),values.max((0,1)).tolist()])
            faces.append(dict(sourceFace=i,vertices=tri[i].tolist(),signedNormalYRatio=float(normals[i,1]/sizes[i]) if sizes[i] else None,
                 areaM2=float(sizes[i]/2),component=component,allVerticesAtComponentMinimum=bool(np.all(tri[i,:,1]==values[:,:,1].min())),
                 wholeBuriedGapRangeM=[float(gaps[i].min()),float(gaps[i].max())]))
        assert sum(normals[i,1]>.25*sizes[i] for i in ids)==before['compoundFoundation']['fullyBuriedUpwardTriangles']
        save(out/(mode+'.json.gz'),dict(faces=faces,components=components,sourceWorldSHA256=digest(tri.tobytes())))
        row=dict(mode=mode,buriedFaces=len(faces),upwardBuriedFaces=before['compoundFoundation']['fullyBuriedUpwardTriangles'],
                 buriedAreaFraction=before['compoundFoundation']['fullyBuriedAreaFraction'],sourceComponents=len(components),
                 wallLikeFaces=sum(abs(f['signedNormalYRatio'])<.25 for f in faces),downwardNonWallFaces=sum(f['signedNormalYRatio']<=-.25 for f in faces))
        rows.append(row);print(row,flush=True)
    result=dict(uids=uids,rows=rows,sourceSHA256ByUid=strict['sourceSHA256ByUid'],sourceGeometryChanges=0,
                physicalAcceptance=False,sourceRoleAccepted=False,installationApproved=False,publication=False,
                qualification='Exact existing compound-burial predicate replay plus positive-area original shared-edge components. No role, foundation, support or publication approval; no source edit or tolerance change.')
    result=json.loads(json.dumps(result));save(out/'summary.json',result)
    module('compound_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-original-compound-burial-source-component-context',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()

"""Reproduce saved compound-foundation counts and name every sampled buried face."""
import argparse
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','strict','uid','peer','lease']:ap.add_argument('--'+k,required=True)
    a=ap.parse_args();lease=read(Path(a.lease));assert reservations.owns(lease)and {'building:'+a.uid,'building:'+a.peer}<=set(lease['resources']);out=BASE/a.batch;assert a.batch.startswith('government-xl-')and '/'not in a.batch and not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    rows={r['uid']:r for r in take(a.runtime,BASE/a.runtime/'selection.json.gz')['rows']};attrs={r['uid']:r for r in take(a.attributes,BASE/a.attributes/'attributes.json.gz')['rows']};g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid);terrain=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);strict=take(a.strict,BASE/a.strict/'summary.json');worlds={}
    assert strict['supportedUid']==a.uid and strict['supportUid']==a.peer
    for uid in [a.uid,a.peer]:
        r,attr=rows[uid],attrs[uid];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']==attr['sourceSHA256']==strict['sourceSHA256ByUid'][uid];refs.append(asset);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);worlds[uid]={'original':decode_original_world_triangles(asset.read_bytes()),**{name:np.asarray(attr[f],dtype='<f8').reshape(-1,3)[ix]for name,f in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]}}
    final=module('compound_buried_face_census',HERE/'xl-final-script-pass.py');results=[]
    for mode,tri in worlds[a.uid].items():
        assert reservations.owns(lease);raw=next(r for r in strict['rows']if r['mode']==mode);assert raw['sourceWorldSHA256ByUid']=={u:digest(worlds[u][mode].tobytes())for u in worlds}
        ground=np.concatenate([terrain,worlds[a.peer][mode]]);lo,hi=tri.min((0,1)),tri.max((0,1));near=ground[(ground[:,:,0].max(1)>=lo[0]-1)&(ground[:,:,0].min(1)<=hi[0]+1)&(ground[:,:,2].max(1)>=lo[2]-1)&(ground[:,:,2].min(1)<=hi[2]+1)];polygons=shapely.polygons(near[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10;near,polygons=near[valid],polygons[valid];points=np.concatenate([tri,tri.mean(1)[:,None,:]],axis=1);h=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),near,shapely.STRtree(polygons)).reshape(-1,4);gaps=points[:,:,1]-h;complete=np.isfinite(h).all(1);buried=complete&(gaps<-.5).all(1);n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);size=np.linalg.norm(n,axis=1);up=n[:,1]>.25*size;f=raw['compoundFoundation']
        assert int(complete.sum())==f['completeTerrainTriangles']==len(tri)and int(buried.sum())==f['fullyBuriedTriangles']and int((buried&up).sum())==f['fullyBuriedUpwardTriangles']
        assert float((size[buried]/2).sum())==f['fullyBuriedAreaM2']
        ids=list(map(int,np.flatnonzero(buried)));record=dict(mode=mode,sourceWorldSHA256ByUid=raw['sourceWorldSHA256ByUid'],completeCompoundGroundSHA256=digest(ground.tobytes()),fullyBuriedFaceIds=ids,fullyBuriedUpwardFaceIds=list(map(int,np.flatnonzero(buried&up))),faces=[dict(sourceFace=i,vertices=tri[i].tolist(),signedNormalYRatio=float(n[i,1]/size[i]),areaM2=float(size[i]/2),sampleGapsM=gaps[i].tolist())for i in ids],rawStrictCompoundFoundation=f,countsAndAreaExactlyReproduced=True,physicalAcceptance=False)
        save(out/(mode+'.json'),record);results.append({k:v for k,v in record.items()if k not in ['faces','rawStrictCompoundFoundation']});print(dict(mode=mode,buried=ids,upward=record['fullyBuriedUpwardFaceIds']),flush=True)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[a.runtime][str(manifest.relative_to(ROOT))];refs.append(manifest)
    result=dict(uids=[a.uid,a.peer],sourceSHA256ByUid=strict['sourceSHA256ByUid'],rows=results,countsAndAreaExactlyReproduced=True,sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Exact same full source/peer/terrain arrays, projected-valid ground facets, four vertex/centroid samples and unchanged -0.5m/normal thresholds as the saved strict compound-foundation producer. Names every sampled fullyburied facet; all counts and buried area match exactly. This is sampled diagnostic context, not exhaustive clearance or a role/support/publication decision.')
    save(out/'summary.json',result);refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py']);module('compound_face_ids_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'reproduced-four-world-compound-buried-face-ids',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()

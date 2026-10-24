"""Nominate private cameras using sampled mesh rays; never grant visual approval."""
import argparse,itertools,re
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def first_hits(camera,targets,triangles):
    """Floating diagnostic rays only; no physical/contact acceptance credit."""
    edges1=triangles[:,1]-triangles[:,0];edges2=triangles[:,2]-triangles[:,0]
    offset=camera-triangles[:,0];q=np.cross(offset,edges1);numer=np.einsum('ij,ij->i',edges2,q)
    clear=[]
    for target in targets:
        ray=target-camera;h=np.cross(ray,edges2);det=np.einsum('ij,ij->i',edges1,h)
        valid=np.abs(det)>1e-12;inv=np.zeros(len(det));inv[valid]=1/det[valid]
        u=np.einsum('ij,ij->i',offset,h)*inv;v=(q@ray)*inv;t=numer*inv
        blocked=valid&(u>=-1e-10)&(v>=-1e-10)&(u+v<=1+1e-10)&(t>1e-7)&(t<1-1e-7)
        clear.append(not np.any(blocked))
    return np.asarray(clear)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','scope','foreign','uid']:ap.add_argument('--'+k,required=True)
    a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(a.runtime,base/a.runtime/'selection.json.gz');geometry=take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']
    scope=take(a.scope,base/a.scope/'summary.json');assert scope['currentManifestSHA256']==selection['manifestSHA256']
    # This bounded nomination supports scenes with no nearby installed native actors.
    # A native overlap needs a separate complete native mesh input, never omission.
    assert all(not r['nearbyNativeActors'] for r in scope['rows'])
    basic=take(a.foreign,base/a.foreign/'basic.json');assert basic['currentManifestSHA256']==selection['manifestSHA256']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    for path,sha in basic['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    staged={r['uid']for r in geometry};meshes={r['uid']:np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for r in geometry}
    meshes.update({r['uid']:np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for r in basic['rows']if r['uid']not in staged})
    source=meshes[a.uid];area=np.linalg.norm(np.cross(source[:,1]-source[:,0],source[:,2]-source[:,0]),axis=1);ids=np.flatnonzero(area>0);ids=ids[np.linspace(0,len(ids)-1,min(96,len(ids)),dtype=int)]
    targets=source[ids].mean(1);weights=area[ids];lo,hi=source.min((0,1)),source.max((0,1));center=(lo+hi)/2;corners=np.asarray(list(itertools.product(*zip(lo,hi))))-center
    app=ROOT/'3d-viewer/city/app.js';refs.append(app);fov=float(re.search(r'PerspectiveCamera\((\d+(?:\.\d+)?),',app.read_text()).group(1));tanv=np.tan(np.deg2rad(fov/2));profiles=[]
    for width in [390,1280]:
        candidates=[]
        for elevation in [.5,1.2,3,10,100]:
            for angle in np.arange(8)*np.pi/4:
                raw=np.round([np.cos(angle),elevation,np.sin(angle)],6);direction=raw/np.linalg.norm(raw);right=np.cross([0,1,0],direction);right/=np.linalg.norm(right);up=np.cross(direction,right);tanh=tanv*width/900
                distance=max(np.max(corners@direction+np.abs(corners@right)/tanh),np.max(corners@direction+np.abs(corners@up)/tanv))*1.04;camera=center+direction*distance
                raylo=np.minimum(camera,lo);rayhi=np.maximum(camera,hi)
                alltri=np.concatenate([t for t in meshes.values()]);alltri=alltri[np.all(alltri.max(1)>=raylo,axis=1)&np.all(alltri.min(1)<=rayhi,axis=1)]
                clear=first_hits(camera,targets,alltri);candidates.append(dict(direction=raw.tolist(),camera=camera.tolist(),clearSampleFaces=int(clear.sum()),sampleFaces=len(ids),clearAreaFraction=float(weights[clear].sum()/weights.sum()),testedOccluderFaces=len(alltri)))
        chosen=max(candidates,key=lambda r:(r['clearAreaFraction'],r['clearSampleFaces']));profiles.append(dict(width=width,chosen=chosen,candidates=candidates));print(dict(width=width,chosen=chosen),flush=True)
    result=dict(uids=[a.uid],sourceSHA256=next(r['sourceSHA256']for r in geometry if r['uid']==a.uid),currentManifestSHA256=selection['manifestSHA256'],profiles=profiles,meshesChecked=sorted(meshes),sampledFaces=ids.tolist(),visualAcceptance=False,installationApproved=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='Private camera nomination only. Floating centroid rays include all staged originals/self and every captured current BASIC mesh, keeping all co-import BASIC replacements excluded only because their original meshes are explicitly present. Scope confirms no nearby installed natives. Sampled rays do not prove complete visibility, collision or identity; actual desktop/mobile exports must be inspected. No physical tolerances or production code changed.')
    save(out/'summary.json',result);module('mesh_camera_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'sampled-complete-mesh-private-camera-nomination',refs,result)

if __name__=='__main__':main()

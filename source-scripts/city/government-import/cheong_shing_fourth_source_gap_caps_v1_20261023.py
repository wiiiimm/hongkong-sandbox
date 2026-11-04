"""Close exact fourth-original terrain gaps with finite low Float32 caps."""
from pathlib import Path
import copy
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_original_projection_coverage_v2_20261010 import point,signed_area,subtract,exact_coverage
from exact_gap_float32_caps_v1_20261023 import enclosing_hull,lower_cap
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-cheong-shing-fourth-source-gap-caps-v1-20261023';out=base/batch;local=HERE/'local'/batch
    assert not out.exists()and not local.exists();refs=[Path(__file__)];pins={}
    def take(batch,name,localfile=False):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=ROOT/name if localfile else base/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    surface='government-xl-island-industrial-paired-surface-binding-v5-20261023';bound=take(surface,'summary.json');patches=[];arrays=[]
    for m in bound['members']:
        p=take(surface,m['candidate']['path'],True);patches.append(p);mesh=p['nativeMesh'];arrays.append(np.asarray(mesh['position'],dtype='<f4').reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)].astype(float))
    ground=np.concatenate(arrays);polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;finite=ground[valid];polys=polys[valid];tree=shapely.STRtree(polys)
    runtime='government-xl-island-cheong-shing-four-original-runtime-v3-20261023';sel=take(runtime,'selection.json.gz');geometry=take(runtime,'source-scripts/city/government-import/local/'+runtime+'/runtime-geometry.json.gz',True);g=next(r for r in geometry['rows']if r['uid']=='landsd/274231:0');literal=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    coverage='government-xl-island-cheong-shing-current-exact-coverage-v1-20261023';prior=take(coverage,'274231:0.json.gz');assert prior['stillUncoveredFaces']==[238];face=literal[238];original=[point(p)for p in face[:,[0,2]]];remaining=[original]
    xz=ground[:,:,[0,2]];ids=np.flatnonzero(np.all(xz.max(1)>=face[:,[0,2]].min(0),axis=1)&np.all(xz.min(1)<=face[:,[0,2]].max(0),axis=1))
    for i in ids:
        tri=[point(p)for p in xz[i]]
        if signed_area(tri):remaining=[q for p in remaining for q in subtract(p,tri)]
        if not remaining:break
    old=next(p for p in prior['proofs']if p['sourceFace']==238);assert str(sum(abs(signed_area(p))for p in remaining))==old['exactUncoveredAreaM2'];assert len(remaining)==2
    additions=[];caps=[]
    for piece in remaining:
        hull=enclosing_hull([[str(x),str(z)]for x,z in piece]);assert hull.bounds[1]>-4027.5
        faces,proof=lower_cap(hull,finite,polys,tree);additions.extend(faces);caps.append(dict(exactGapXZ=[[str(x),str(z)]for x,z in piece],**proof))
    combined=np.concatenate([ground,np.asarray(additions)]);uid=g['uid'];r=next(r for r in sel['rows']if r['uid']==uid);asset=ROOT/r['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==g['sourceSHA256'];refs.append(asset)
    attrs=take('government-xl-island-cheong-shing-four-original-attributes-v1-20261023','attributes.json.gz');a=next(r for r in attrs['rows']if r['uid']==uid);assert a['sourceSHA256']==g['sourceSHA256'];ix=np.asarray(a['completeOriginalIndex']).reshape(-1,3)
    worlds={'original':decode_original_world_triangles(raw),'literal':literal}
    for mode,field in [('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(a[field]).reshape(-1,3)[ix]
    proofs=[]
    for mode,t in worlds.items():
        proof=exact_coverage(t[238],combined);assert proof['exactProjectionCovered'];proofs.append(dict(mode=mode,sourceFace=238,**proof))
    outputs=[]
    for m,patch,t in zip(bound['members'],patches,arrays):
        candidate=copy.deepcopy(patch);mesh=candidate['nativeMesh'];new=np.concatenate([t,np.asarray(additions)])if m['member']=='north'else t
        assert np.array_equal(new[:len(t)],t);mesh['position']=new.reshape(-1).tolist();mesh['index']=list(range(new.size//3));mesh.pop('sourceOverlap',None);mesh['source'].pop('coordinatedBoundary',None)
        mesh['source']['fourthOriginalGapCaps']=dict(sourceUid=uid,sourceSHA256=g['sourceSHA256'],sourceFace=238,addedFaces=len(additions)if m['member']=='north'else 0,publicationApproved=False)
        path=local/(m['member']+'-unapproved.json');save(path,candidate);refs.append(path);outputs.append(dict(member=m['member'],candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())),replaces=m['replaces'],oldFaces=len(t),addedFaces=len(new)-len(t),terrainFaces=len(new)))
    identity=take('government-xl-island-cheong-shing-named-identity-review-v1-20261023','summary.json')
    result=dict(uids=sel['uids']if' uids'in sel else [r['uid']for r in sel['rows']],members=outputs,coInstallationRequired=identity['coInstallationRequired'],allOldTerrainFacesRetainedExactly=True,allFourWorldFace238Covered=True,proofs=proofs,sourceGeometryChanges=0,installationApproved=False,status='private-fourth-source-gap-cap-feasibility',qualification='Two exact positive-area residuals under fourth-original face238 are enclosed in Float32 hulls. Added terrain is below authenticated adjacent finite minima, rounded down one Float32 ULP, never below1.2m. All old terrain faces and all building geometry remain unchanged. Fresh paired surface, whole-source, current-neighbour and browser/publication validation still required.')
    save(out/'caps.json.gz',caps);save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_gap_float32_caps_v1_20261023.py','exact_original_projection_coverage_v2_20261010.py','exact_packed_world_geometry_20261009.py']);module('fourth_gap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'fourth-original-exact-gap-finite-float32-terrain-caps',refs,result);print(dict(addedFaces=len(additions),allFourWorldFace238Covered=True),flush=True)

if __name__=='__main__':main()

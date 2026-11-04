"""Diagnostic conforming triangulation of the local terrain edit, no acceptance."""
from pathlib import Path
import copy
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from ronsdale_local_inset_v2_20261022 import plane,lift
from exact_original_projection_coverage_v2_20261010 import exact_coverage

BATCH='government-xl-island-industrial-paired-noding-feasibility-v2-20261023'

def main():
    base=ROOT/'docs/astra-city/government-import';out=base/BATCH;local=HERE/'local'/BATCH
    assert not out.exists()and not local.exists();refs=[Path(__file__)];cache={}
    def take(batch,name):
        folder=base/batch
        if batch not in cache:cache[batch]=authenticate(folder)[1];refs.append(folder/'result.json')
        path=ROOT/name if str(name).startswith('source-scripts/')else folder/name
        assert digest(path.read_bytes())==cache[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    original='government-xl-island-industrial-paired-inset-diagnostic-v1-20261023'
    diagnostic=take(original,'summary.json');lineage=take(original,'lineage.json.gz');split=32118
    arrays=[];masks=[];templates=[]
    for member in diagnostic['members']:
        label=member['member'];patch=take(original,member['candidate']['path']);mesh=patch['nativeMesh'];t=np.asarray(mesh['position']).reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)]
        lines=[r for r in lineage['outputLineage']if(r['parentFace']<split)==(label=='south')];assert len(lines)==len(t)
        mask=np.asarray([r['kind']!='unchanged'for r in lines]);normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);mask &= np.abs(normal[:,1])>1e-10
        templates.append(patch);arrays.append(t);masks.append(mask)
    changed=np.concatenate([t[mask]for t,mask in zip(arrays,masks)]);polys=shapely.polygons(changed[:,:,[0,2]]);planes=[plane(t)for t in changed];tree=shapely.STRtree(polys)
    # All incident edges are noded together before Float32 packing, including
    # the finite member boundary. No building vertex is input to this rewrite.
    network=shapely.union_all(shapely.boundary(polys));cells=list(shapely.get_parts(shapely.polygonize(shapely.get_parts(network))))
    fresh=[[],[]];cellproof=[]
    for k,cell in enumerate(cells):
        point=cell.representative_point();ids=tree.query(point,predicate='intersects')
        if not len(ids):continue
        x,z=point.x,point.y;j=max(ids,key=lambda i:np.dot([x,z,1],planes[i]));assert cell.difference(polys[j]).area<1e-7
        faces=lift(cell,planes[j]);member=0 if z<-4027.5 else 1
        assert all((f[:,2].max()<=-4027.5+1e-8 if member==0 else f[:,2].min()>=-4027.5-1e-8)for f in faces)
        fresh[member].extend(faces);cellproof.append(dict(sourceChangedFace=int(j),member=member,triangles=len(faces),areaM2=float(cell.area)))
        if k%1000==0:print(dict(cells=k,total=len(cells)),flush=True)
    union=shapely.union_all(polys);newfaces=np.concatenate([np.asarray(f)for f in fresh]);difference=float(union.symmetric_difference(shapely.union_all(shapely.polygons(newfaces[:,:,[0,2]]))).area);assert difference<1e-7
    outputs=[];refs.extend([HERE/'ronsdale_local_inset_v2_20261022.py',HERE/'exact_original_projection_coverage_v2_20261010.py'])
    for name,t,mask,patch,faces in zip(['south','north'],arrays,masks,templates,fresh):
        candidate=copy.deepcopy(patch);combined=np.concatenate([t[~mask],np.asarray(faces)]);mesh=candidate['nativeMesh'];mesh['position']=combined.reshape(-1).tolist();mesh['index']=list(range(combined.size//3));mesh.pop('sourceOverlap',None);mesh['source'].pop('numericalCoverageGap',None)
        path=local/(name+'-unapproved.json');save(path,candidate);refs.append(path);outputs.append(dict(member=name,path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),faces=len(combined),untouchedFaces=int((~mask).sum())))
    ground=np.concatenate([np.concatenate([t[~mask],np.asarray(f)])for t,mask,f in zip(arrays,masks,fresh)]).astype('float32').astype('float64')
    runtime='government-xl-island-industrial-paired-current-runtime-v1-20261023';g=take(runtime,'source-scripts/city/government-import/local/'+runtime+'/runtime-geometry.json.gz');coverage='government-xl-island-industrial-paired-prephysical-20270-v1-20261023-coverage';rows=[]
    for row in g['rows']:
        t=np.asarray(row['position']).reshape(-1,3)[np.asarray(row['index']).reshape(-1,3)];previous=take(coverage,row['uid'].split('/')[1]+'.json.gz');proofs=[]
        for face in previous['stillUncoveredFaces']:proofs.append(dict(sourceFace=face,**exact_coverage(t[face],ground)))
        save(out/(row['uid'].replace('/','-').replace(':','-')+'.json.gz'),dict(uid=row['uid'],proofs=proofs))
        rows.append(dict(uid=row['uid'],testedFaces=len(proofs),covered=sum(p['exactProjectionCovered']for p in proofs),stillUncovered=[p['sourceFace']for p in proofs if not p['exactProjectionCovered']]))
        print(rows[-1],flush=True)
    result=dict(uids=[r['uid']for r in rows],rows=rows,members=outputs,changedBefore=len(changed),changedAfter=len(newfaces),projectionSymmetricDifferenceM2=difference,allTestedFacesCovered=all(not r['stillUncovered']for r in rows),sourceGeometryChanges=0,installationApproved=False,qualification='Local terrain triangulation feasibility only; previously failed literal source faces tested exactly against private Float32 output. All old faces outside local edit retained. Fresh native/shared-boundary, whole-source/four-world/support/current-neighbour/browser checks remain required; no prior approval transfers.')
    save(out/'cells.json.gz',cellproof);save(out/'summary.json',result)
    module('noding_feasibility_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-paired-local-terrain-noding-feasibility',refs,result)

if __name__=='__main__':main()

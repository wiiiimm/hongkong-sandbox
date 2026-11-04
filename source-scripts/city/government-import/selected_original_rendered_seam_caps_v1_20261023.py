"""Private exact caps for final-rendered Lamma terrain residuals; no admission."""
import argparse
from pathlib import Path
from fractions import Fraction
import copy
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_original_projection_coverage_v2_20261010 import point,signed_area,subtract,exact_coverage
from exact_gap_float32_caps_v1_20261023 import enclosing_hull,lower_cap


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','coverage','patch']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';batch=a.batch;out=base/batch;local=HERE/'local'/batch
    assert not out.exists()and not local.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    runtime=a.runtime;sel=take(runtime,base/runtime/'selection.json.gz');row,=sel['rows']
    geo=take(runtime,HERE/'local'/runtime/'runtime-geometry.json.gz');g,=geo['rows'];assert g['sourceSHA256']==row['sourceSHA256']
    source=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    ground=np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3);polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;ground=ground[valid];polys=polys[valid];tree=shapely.STRtree(polys)
    coverage=a.coverage;prior=take(coverage,base/coverage/(row['uid'].split('/')[1]+'.json.gz'))
    assert prior['sourceSHA256']==row['sourceSHA256']and prior['uid']==row['uid']and prior['stillUncoveredFaces']
    assert all(p['completeGroundSHA256']==digest(ground.tobytes())for p in prior['proofs'])
    xz=ground[:,:,[0,2]];additions=[];caps=[]
    for proof in prior['proofs']:
        if proof['method']!='closed-facet-area-union':continue
        i=proof['sourceFace'];face=source[i];assert digest(face.tobytes())==proof['sourceFaceSHA256']
        remaining=[[point(p)for p in face[:,[0,2]]]]
        ids=np.flatnonzero(np.all(xz.max(1)>=face[:,[0,2]].min(0),axis=1)&np.all(xz.min(1)<=face[:,[0,2]].max(0),axis=1))
        for j in ids:
            tri=[point(p)for p in xz[j]]
            if signed_area(tri):remaining=[q for p in remaining for q in subtract(p,tri)]
            if not remaining:break
        assert sum(abs(signed_area(p))for p in remaining)==Fraction(proof['exactUncoveredAreaM2'])
        for piece in remaining:
            exact=[[str(x),str(z)]for x,z in piece];hull=enclosing_hull(exact);faces,cap=lower_cap(hull,ground,polys,tree)
            additions.extend(faces);caps.append(dict(sourceFace=i,exactGapXZ=exact,**cap))
    combined=np.concatenate([ground,np.asarray(additions)])
    checks=[dict(sourceFace=i,**exact_coverage(source[i],combined))for i in prior['stillUncoveredFaces']]
    assert all(p['exactProjectionCovered']for p in checks),'Area caps do not cover all wall intervals; preserve failure'
    patchbatch=a.patch;s=take(patchbatch,base/patchbatch/'summary.json');patch=take(patchbatch,ROOT/s['candidate']['path']);scope=take(patchbatch,base/patchbatch/'scope.json')
    new=copy.deepcopy(patch);mesh=new['nativeMesh'];old=np.asarray(mesh['position'],dtype='<f4').reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)].astype(float)
    values=np.concatenate([old,np.asarray(additions)]);assert np.array_equal(values[:len(old)],old)
    mesh['position']=values.reshape(-1).tolist();mesh['index']=list(range(values.size//3))
    mesh.pop('sourceOverlap',None);mesh['source']['privateExactRenderedSeamCaps']=dict(sourceSHA256=row['sourceSHA256'],addedFaces=len(additions),installationApproved=False)
    candidate=local/'candidate-terrain.json';save(candidate,new);refs.append(candidate);save(out/'scope.json',scope);save(out/'caps.json.gz',caps);save(out/'proofs.json.gz',checks)
    result=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],candidate=dict(path=str(candidate.relative_to(ROOT)),sha256=digest(candidate.read_bytes())),oldTerrainFaces=len(old),addedTerrainFaces=len(additions),allOldTerrainFacesRetainedExactly=True,exactResidualFacesRechecked=len(checks),allPriorResidualsCovered=True,sourceGeometryChanges=0,installationApproved=False,publication=False,status='private-rendered-seam-cap-feasibility',qualification='Exact rational positive-area residuals enclosed in finite Float32 terrain caps below adjacent finite minima. All prior area/interval residuals rechecked exactly. Candidate remains unvalidated: overlap/clamp/current runtime/all four world streams/current neighbours/identity/browser/publication must be checked afresh.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_gap_float32_caps_v1_20261023.py','exact_original_projection_coverage_v2_20261010.py'])
    module('selected_rendered_caps_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-final-rendered-terrain-seam-cap-feasibility',refs,result)
    print({k:result[k]for k in ['oldTerrainFaces','addedTerrainFaces','exactResidualFacesRechecked','allPriorResidualsCovered']},flush=True)

if __name__=='__main__':main()

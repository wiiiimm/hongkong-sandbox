"""Close exact finite original-terrain domain seams with conservative terrain caps.

No building mesh changes. Every original TIN triangle remains unchanged. Caps
sit below adjacent finite minima; all small-grid domain faces are rechecked by
rational arithmetic. Construction is private and grants no placement approval.
"""
import argparse
from fractions import Fraction
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_original_projection_coverage_v2_20261010 import point,signed_area,subtract,exact_coverage
from exact_gap_float32_caps_v1_20261023 import enclosing_hull,lower_cap


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','subset','trial','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch;assert not out.exists()and not local.exists();refs=[Path(__file__)];pins={}
    def take(name,path):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    row=take(a.subset,base/a.subset/'summary.json')['rows'][0];assert row['uid']==a.uid
    scope=take(a.trial,base/a.trial/'scope.json');assert scope['uids']==[a.uid];bb=scope['bounds'];decoder=module('domain_caps_decoder',HERE/'xl-second-pass.py');parts=[]
    for filename in row['sourceTerrainPaths']:
        path=ROOT/filename;meta=take(a.subset,path)
        for b in meta.get('buffers',[]):
            member=path.parent/b['uri'];assert digest(member.read_bytes())==pins[a.subset][str(member.relative_to(ROOT))];refs.append(member)
        parts.append(decoder.terrain_triangles(path))
    ground=np.concatenate(parts);lo,hi=ground[:,:,[0,2]].min(1),ground[:,:,[0,2]].max(1)
    ground=ground[(hi[:,0]>=bb[0])&(lo[:,0]<=bb[2])&(hi[:,1]>=bb[1])&(lo[:,1]<=bb[3])]
    assert np.isfinite(ground).all() and ground[:,:,1].min()>=1.2
    polys=shapely.polygons(ground[:,:,[0,2]]);tree=shapely.STRtree(polys);xz=ground[:,:,[0,2]];added=[];caps=[];targets=[];initial=[];seen=set()
    xs=np.arange(bb[0],bb[2],10).tolist()+[bb[2]];zs=np.arange(bb[1],bb[3],10).tolist()+[bb[3]]
    for x0,x1 in zip(xs,xs[1:]):
        for z0,z1 in zip(zs,zs[1:]):
            aa=np.array([x0,2.,z0]);b=np.array([x1,2.,z0]);c=np.array([x0,2.,z1]);d=np.array([x1,2.,z1]);targets.extend([np.array([aa,b,c]),np.array([b,d,c])])
    for index,face in enumerate(targets):
        proof=exact_coverage(face,ground);initial.append(proof)
        if proof['exactProjectionCovered']:continue
        remaining=[[point(p)for p in face[:,[0,2]]]];ids=np.flatnonzero(np.all(xz.max(1)>=face[:,[0,2]].min(0),axis=1)&np.all(xz.min(1)<=face[:,[0,2]].max(0),axis=1))
        for j in ids:
            triangle=[point(p)for p in xz[j]]
            if signed_area(triangle):remaining=[q for piece in remaining for q in subtract(piece,triangle)]
            if not remaining:break
        assert sum(abs(signed_area(piece))for piece in remaining)==Fraction(proof['exactUncoveredAreaM2'])
        for piece in remaining:
            hull=enclosing_hull([[str(x),str(z)]for x,z in piece])
            if hull.wkb in seen:continue
            seen.add(hull.wkb);faces,cap=lower_cap(hull,ground,polys,tree);added.extend(faces);caps.append(dict(domainFace=index,exactGapXZ=[[str(x),str(z)]for x,z in piece],**cap))
        if index%100==0:print(dict(domainFacesChecked=index,total=len(targets),addedFaces=len(added)),flush=True)
    assert added;combined=np.concatenate([ground,np.asarray(added)]);assert np.array_equal(combined[:len(ground)],ground)
    checks=[dict(domainFace=i,**exact_coverage(face,combined))for i,face in enumerate(targets)];assert all(r['exactProjectionCovered']for r in checks)
    terrain=local/'terrain-triangles.json.gz';save(terrain,combined.tolist());refs.append(terrain)
    save(out/'initial-domain-proofs.json.gz',initial);save(out/'final-domain-proofs.json.gz',checks);save(out/'caps.json.gz',caps)
    result=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],bounds=bb,originalTerrainFaces=len(ground),addedTerrainFaces=len(added),exactDomainFaces=len(targets),allDomainFacesCovered=True,allOriginalTerrainFacesRetainedExactly=True,sourceGeometryChanges=0,installationApproved=False,publication=False,terrainPath=str(terrain.relative_to(ROOT)),terrainSHA256=digest(terrain.read_bytes()),status='private-exact-domain-seam-feasibility')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_gap_float32_caps_v1_20261023.py','exact_original_projection_coverage_v2_20261010.py','xl-second-pass.py'])
    module('domain_caps_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-original-terrain-complete-domain-seam-caps',refs,result)
    print(result,flush=True)


if __name__=='__main__':main()

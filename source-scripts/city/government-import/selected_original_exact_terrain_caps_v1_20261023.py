"""Private exact seam-cap feasibility; no building edits or installation approval."""
import argparse
from pathlib import Path
from fractions import Fraction
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_original_projection_coverage_v2_20261010 import point,signed_area,subtract,exact_coverage
from exact_gap_float32_caps_v1_20261023 import enclosing_hull,lower_cap
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    base=ROOT/'docs/astra-city/government-import'
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','discovery','selection','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();batch=a.batch
    assert batch.startswith('government-xl-')and '/'not in batch
    out=base/batch;local=HERE/'local'/batch
    assert not out.exists() and not local.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:
            pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    discovery=a.discovery
    summary=take(discovery,base/discovery/'summary.json')
    oldproofs=take(discovery,base/discovery/'exact-face-proofs.json.gz')
    selection=a.selection
    row=next(r for r in take(selection,base/selection/'selection.json.gz')['rows']if r['uid']==a.uid)
    assert summary['uids']==[a.uid]
    asset=ROOT/row['candidate']['path'];raw=asset.read_bytes()
    assert digest(raw)==summary['sourceSHA256'];refs.append(asset)
    source=decode_original_world_triangles(raw)
    assert digest(source.astype('<f8').tobytes())==summary['sourceWorldSHA256']
    decoder=module('selected_caps_decoder',HERE/'xl-second-pass.py');parts=[]
    for name in summary['sourceTerrainPaths']:
        p=ROOT/name;gltf=take(discovery,p)
        for b in gltf.get('buffers',[]):
            q=p.parent/b['uri'];assert digest(q.read_bytes())==pins[discovery][str(q.relative_to(ROOT))];refs.append(q)
        parts.append(decoder.terrain_triangles(p))
    ground=np.concatenate(parts);lo,hi=source.min((0,1)),source.max((0,1))
    keep=(ground[:,:,0].max(1)>=lo[0]-1)&(ground[:,:,0].min(1)<=hi[0]+1)&(ground[:,:,2].max(1)>=lo[2]-1)&(ground[:,:,2].min(1)<=hi[2]+1)
    ground=ground[keep]
    assert digest(ground.astype('<f8').tobytes())==oldproofs[0]['completeGroundSHA256']
    polys=shapely.polygons(ground[:,:,[0,2]]);tree=shapely.STRtree(polys)
    additions=[];caps=[];seen=set();xz=ground[:,:,[0,2]]
    for proof in oldproofs:
        if proof['exactProjectionCovered']:continue
        face=source[proof['sourceFace']];remaining=[[point(p) for p in face[:,[0,2]]]]
        ids=np.flatnonzero(np.all(xz.max(1)>=face[:,[0,2]].min(0),axis=1)&np.all(xz.min(1)<=face[:,[0,2]].max(0),axis=1))
        for i in ids:
            tri=[point(p)for p in xz[i]]
            if signed_area(tri):remaining=[q for p in remaining for q in subtract(p,tri)]
            if not remaining:break
        assert sum(abs(signed_area(p))for p in remaining)==Fraction(proof['exactUncoveredAreaM2'])
        for piece in remaining:
            exact=[[str(x),str(z)]for x,z in piece];hull=enclosing_hull(exact)
            if hull.wkb in seen:continue
            seen.add(hull.wkb);faces,cap=lower_cap(hull,ground,polys,tree)
            additions.extend(faces);caps.append(dict(sourceFace=proof['sourceFace'],exactGapXZ=exact,**cap))
    combined=np.concatenate([ground,np.asarray(additions)])
    assert np.array_equal(combined[:len(ground)],ground)
    checks=[dict(sourceFace=p['sourceFace'],**exact_coverage(source[p['sourceFace']],combined))for p in oldproofs]
    assert all(p['exactProjectionCovered']for p in checks)
    terrain=local/'terrain-triangles.json.gz';save(terrain,combined.tolist());refs.append(terrain)
    save(out/'caps.json.gz',caps);save(out/'proofs.json.gz',checks)
    result=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],originalTerrainFaces=len(ground),addedTerrainFaces=len(additions),exactRecheckedSourceFaces=len(checks),allPriorGapFacesCovered=True,allOriginalTerrainFacesRetainedExactly=True,sourceGeometryChanges=0,installationApproved=False,publication=False,terrainPath=str(terrain.relative_to(ROOT)),terrainSHA256=digest(terrain.read_bytes()),status='private-exact-terrain-seam-feasibility',qualification='Exact rational residuals enclosed by Float32 terrain caps below authenticated adjacent finite minima. Original buildings and original terrain faces unchanged. Whole-source four-world clearance, current neighbours, identity, runtime and publication remain unapproved.')
    save(out/'summary.json',result)
    refs.extend(HERE/n for n in ['exact_gap_float32_caps_v1_20261023.py','exact_original_projection_coverage_v2_20261010.py','exact_packed_world_geometry_20261009.py','xl-second-pass.py'])
    module('selected_exact_caps_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-original-terrain-seam-cap-feasibility',refs,result)
    print({k:result[k]for k in ['originalTerrainFaces','addedTerrainFaces','exactRecheckedSourceFaces','allPriorGapFacesCovered']},flush=True)

if __name__=='__main__':main()

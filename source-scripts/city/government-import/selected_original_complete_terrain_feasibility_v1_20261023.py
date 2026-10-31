"""Exhaustive exact original-face coverage and conservative terrain clearance.

Private diagnostic only: no renderer, placement, identity or publication approval.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_projection_coverage_v2_20261010 import exact_coverage
from exact_original_face_conservative_clearance_v4_20261010 import verify


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','selection','terrain','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:
            pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    row=next(r for r in take(a.selection,base/a.selection/'selection.json.gz')['rows']if r['uid']==a.uid)
    terrain=take(a.terrain,base/a.terrain/'summary.json');assert terrain['sourceSHA256']==row['sourceSHA256']
    ground=np.asarray(take(a.terrain,ROOT/terrain['terrainPath']),dtype='<f8')
    assert digest((ROOT/terrain['terrainPath']).read_bytes())==terrain['terrainSHA256']
    asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];refs.append(asset)
    source=decode_original_world_triangles(raw)
    assert len(source)==row['triangles']and np.isfinite(source).all()and np.isfinite(ground).all()
    gxz=ground[:,:,[0,2]];low,high=gxz.min(1),gxz.max(1);results=[];refinements=[]
    for i,face in enumerate(source):
        coverage=exact_coverage(face,ground)
        lo,hi=face[:,[0,2]].min(0),face[:,[0,2]].max(0)
        ids=np.flatnonzero(np.all(high>=lo,axis=1)&np.all(low<=hi,axis=1))
        bound=float(np.nextafter(float(face[:,1].min()-ground[ids,:,1].max()),-np.inf))if len(ids)else None
        passed=coverage['exactProjectionCovered']and bound is not None and bound>=-.5
        refined=None
        if coverage['exactProjectionCovered']and not passed:
            proof=verify(face,ground);assert proof['sourceFaceSHA256']==coverage['sourceFaceSHA256']
            passed=proof['existingOrdinaryClearanceBoundProved'];refined=proof['exactCertifiedLowerClearanceM']
            refinements.append(dict(sourceFace=i,**proof))
        results.append(dict(sourceFace=i,coverage=coverage,coarseLowerGapM=bound,refinedExactLowerGapM=refined,ordinaryClearanceConservativelyProved=passed))
        if(i+1)%500==0:print(dict(processed=i+1,total=len(source)),flush=True)
    save(out/'faces.json.gz',results);save(out/'refinements.json.gz',refinements)
    uncovered=[r['sourceFace']for r in results if not r['coverage']['exactProjectionCovered']]
    unresolved=[r['sourceFace']for r in results if not r['ordinaryClearanceConservativelyProved']]
    result=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],sourceWorldSHA256=digest(source.astype('<f8').tobytes()),terrainWorldSHA256=digest(ground.astype('<f8').tobytes()),completeOriginalFaces=len(source),terrainFaces=len(ground),exactCoveredFaces=len(source)-len(uncovered),uncoveredFaces=uncovered,ordinaryClearanceProvedFaces=len(source)-len(unresolved),unresolvedClearanceFaces=unresolved,refinedFaces=len(refinements),sourceGeometryChanges=0,installationApproved=False,publication=False,status='private-complete-original-terrain-feasibility',qualification='Every original source face, including collapsed XZ faces, receives an exact closed-facet projection proof. Clearance uses downward-rounded complete candidate bounds, refining failures with exact clipped conservative terrain maxima. An unresolved conservative bound is not proof of source corruption. Other runtime world transforms, support/contact, current scene, identity and publication remain unapproved.')
    save(out/'summary.json',result)
    refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_projection_coverage_v2_20261010.py','exact_original_face_conservative_clearance_v4_20261010.py'])
    module('complete_terrain_feasibility_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-exact-original-terrain-feasibility',refs,result)
    print({k:result[k]for k in ['completeOriginalFaces','exactCoveredFaces','ordinaryClearanceProvedFaces','refinedFaces']},flush=True)

if __name__=='__main__':main()

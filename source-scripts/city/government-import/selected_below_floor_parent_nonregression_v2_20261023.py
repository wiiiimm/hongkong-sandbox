"""Exact finite Float32 checks for every sub-floor face against captured parent.

Every finite source portion at or below the stated land floor is compared by
exact barycentric constraints, with full parent projection coverage retained.
"""
import argparse
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_below_floor_triangle_gap_v1_20261023 import verify
from exact_original_projection_coverage_v2_20261010 import exact_coverage


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',required=True);p.add_argument('--patch',required=True);a=p.parse_args()
    assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();receipt,pins=authenticate(base/a.patch);refs=[Path(__file__),base/a.patch/'result.json']
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
    assert receipt['status']=='private-terrain-validator-passed'
    patch=take(ROOT/receipt['candidate']['path']);parent=take(HERE/'local'/a.patch/'parent.json')
    mesh=patch['nativeMesh'];vertices=np.asarray(mesh['position'],dtype=np.float32).astype(np.float64).reshape(-1,3);faces=vertices[np.asarray(mesh['index']).reshape(-1,3)];ground=np.asarray(parent['triangles'],float);xz=ground[:,:,[0,2]];rows=[];proofs=[]
    for i in np.flatnonzero(faces[:,:,1].min(1)<1.2):
        face=faces[i];lo,hi=face[:,[0,2]].min(0),face[:,[0,2]].max(0);ids=np.flatnonzero(np.all(xz.max(1)>=lo,axis=1)&np.all(xz.min(1)<=hi,axis=1));pairs=[]
        for j in ids:pairs.append(dict(parentFace=int(j),**verify(face,ground[j])))
        gaps=[Fraction(r['exactMinimumFiniteColumnGapM'])for r in pairs if r['exactClosedHorizontalProjectionsMeet']];assert gaps
        minimum=min(gaps);coverage=exact_coverage(face,ground);passed=minimum>=0 and coverage['exactProjectionCovered']
        rows.append(dict(candidateFace=int(i),minimumCandidateY=float(face[:,1].min()),exactBelowFloorMinimumParentGapM=str(minimum),parentProjectionCovered=coverage['exactProjectionCovered'],exactBelowFloorNonregressionProved=passed));proofs.append(dict(candidateFace=int(i),coverage=coverage,pairs=pairs))
    save(out/'faces.json',rows);save(out/'proofs.json.gz',proofs)
    result=dict(uids=receipt['uids'],newSourceLandFloorM=1.2,subFloorCandidateFaces=len(rows),belowFloorNonregressionProved=sum(r['exactBelowFloorNonregressionProved']for r in rows),inconclusiveCandidateFaces=[r['candidateFace']for r in rows if not r['exactBelowFloorNonregressionProved']],allSubFloorRegionsNonregressing=all(r['exactBelowFloorNonregressionProved']for r in rows),sourceGeometryChanges=0,installationApproved=False,publication=False)
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_original_triangle_pair_column_gap_20261010.py','exact_below_floor_triangle_gap_v1_20261023.py','exact_original_projection_coverage_v2_20261010.py'])
    module('below_floor_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'finite-current-parent-subfloor-conservative-nonregression',refs,result)
    print(result,flush=True)


if __name__=='__main__':main()

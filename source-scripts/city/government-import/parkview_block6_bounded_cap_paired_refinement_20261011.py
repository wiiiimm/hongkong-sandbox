"""Distinct exact finite same-column refinement; preserves prior conservative proof."""
from run import ROOT,HERE,read,save,digest
from pathlib import Path
import numpy as np
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify as column_verify
from fractions import Fraction as F
B=ROOT/'docs/astra-city/government-import'
D=B/'government-xl-parkview-block6-bounded-original-clear-cap-probe-v1-20261011'
P=B/'government-xl-terrain-recovery-parkview-block11-complete-original-proposed-current-probe-v4-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 d=read(D/'diagnostic.json.gz');s=next(x for x in read(P/'selection.json.gz')['rows']if x['uid']=='landsd/254491:0');a=ROOT/s['candidate']['path'];n=decode_original_world_triangles(a.read_bytes());assert digest(n.tobytes())==d['completeOriginalNativeWorldSHA256']
 rp=HERE/'local'/P.name/'runtime-geometry.json.gz';rt=next(x for x in read(rp)['rows']if x['uid']=='landsd/254491:0');g=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3);assert digest(g.tobytes())==d['completeCurrentGroundSHA256']
 face=n[d['capOriginalFace']];xz=g[:,:,[0,2]];sxz=face[:,[0,2]]
 ids=np.flatnonzero(np.all(xz.max(1)>=sxz.min(0),axis=1)&np.all(xz.min(1)<=sxz.max(0),axis=1));pieces=[]
 assert list(map(int,ids))==d['capWholeFiniteCurrentGroundProof']['allProjectedBoundingCandidateOriginalGroundFacets']
 for j in ids:
  pieces.append(dict(originalGroundFace=int(j),proof=column_verify(face,g[j])))
 gaps=[F(p['proof']['exactMinimumFiniteColumnGapM'])for p in pieces if p['proof']['exactClosedHorizontalProjectionsMeet']];assert gaps
 bound=min(gaps);coverage=d['capWholeFiniteCurrentGroundProof']['completeOriginalProjectionCoverage']
 proof=dict(contract='complete-exact-finite-column-cap-refinement-v1',allAABBCandidateFiniteColumnProofs=pieces,completeOriginalProjectionCoverage=coverage,groundProjectionCovered=coverage['exactProjectionCovered'],exactCertifiedLowerClearanceM=str(bound),existingOrdinaryClearanceBoundProved=coverage['exactProjectionCovered']and bound>=F(-1,2),completeCurrentGroundSHA256=digest(g.tobytes()),sourceFaceSHA256=digest(face.tobytes()),noGroundOrSourceFaceOmitted=True,noToleranceOrBufferCredit=True,sourceGeometryChanges=0,rootOrContactCredit=False)
 refs=[ref(p)for p in [Path(__file__),D/'diagnostic.json.gz',a,P/'selection.json.gz',rp,HERE/'exact_original_paired_finite_clearance_v2_20261010.py',HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py',HERE/'exact_original_projection_coverage_20261009.py',HERE/'exact_original_closed_projection_intersection_20261010.py']]
 save(D/'paired-cap-refinement.json.gz',dict(uid='landsd/255438:0',nativeUID='landsd/254491:0',cap=58400,pairedProof=proof,evidenceRefs=refs,strictWholeCapClear=proof['groundProjectionCovered'] and float(__import__('fractions').Fraction(proof['exactCertifiedLowerClearanceM']))>0,sourceOnly=True,currentAcceptance=False,installationApproved=False,newlyInstalled=0))
 print({k:v for k,v in proof.items()if k in ['exactCertifiedLowerClearanceM','groundProjectionCovered','existingOrdinaryClearanceBoundProved']},flush=True)
if __name__=='__main__':main()

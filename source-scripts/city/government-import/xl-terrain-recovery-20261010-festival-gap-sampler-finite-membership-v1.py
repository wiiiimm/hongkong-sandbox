"""Trace actual phantom native sampler picks; no runtime modification."""
import importlib.util
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-festival-gap-sampler-finite-membership-v1';DOC=BASE/BATCH
PROPOSAL=BASE/'xl-terrain-recovery-20261010-festival-mixed-authentic-parent-gap-proposal-v3';RAYS=HERE/'local/xl-terrain-recovery-20261010-festival-gap-sampler-ray-v1/diagnostic.json.gz'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();ray=read(RAYS)
 for p,h in ray['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 candidate=read(PROPOSAL/'terrain-candidates.json')[0];patch=read(ROOT/candidate['path']);p=np.asarray(patch['nativeMesh']['position'],np.float32).astype(float).reshape(-1,3);tri=p[np.asarray(patch['nativeMesh']['index']).reshape(-1,3)];rows=[]
 for r in ray['rows']:
  if r['passed']:continue
  x,z=r['x'],r['z'];choices=[]
  for i,t in enumerate(tri):
   (ax,ay,az),(bx,by,bz),(cx,cy,cz)=t;d=(bz-cz)*(ax-cx)+(cx-bx)*(az-cz)
   if abs(d)<1e-10:continue
   u=((bz-cz)*(x-cx)+(cx-bx)*(z-cz))/d;v=((cz-az)*(x-cx)+(ax-cx)*(z-cz))/d;w=1-u-v
   if min(u,v,w)>=-1e-8:choices.append((u*ay+v*by+w*cy,i,[u,v,w]))
  assert choices;h,i,bary=max(choices);t=[[F(float(v)) for v in q] for q in tri[i]];a,b,c=t;xx,zz=F(x),F(z);d=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2]);u=((b[2]-c[2])*(xx-c[0])+(c[0]-b[0])*(zz-c[2]))/d;v=((c[2]-a[2])*(xx-c[0])+(a[0]-c[0])*(zz-c[2]))/d;exact=[u,v,1-u-v];assert abs(h-r['actualSamplerHeight'])<1e-8 and min(exact)<0
  rows.append(dict(rawRayProbe=r,actualSelectedNativeFace=i,completeActualFloat32DrawnFace=tri[i].tolist(),actualDoubleBarycentric=bary,exactFractionBarycentric=[str(v) for v in exact],outsideActualFiniteDrawnTriangle=True,acceptedOnlyByNegativeBarycentricTolerance=True,actualRuntimeMembershipFloor=-1e-8,fullAcceptance=False))
 assert len(rows)==7;refs=[ref(p) for p in [Path(__file__),RAYS,HERE/'xl-terrain-recovery-20261010-festival-gap-sampler-ray-v1.mjs',PROPOSAL/'terrain-candidates.json',PROPOSAL/'diagnostic.json.gz',PROPOSAL/'result.json',ROOT/candidate['path'],ROOT/'3d-viewer/city/native-terrain.js']];save(DOC/'diagnostic.json.gz',dict(uids=['landsd/91827:0','landsd/104302:0'],rows=rows,completeGapProbeCount=len(ray['rows']),rawFailuresPreserved=True,buildingGeometryChanges=0,terrainProposalGeometryChanged=True,runtimeChanged=False,installationApproved=False,evidenceRefs=refs));s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'actual-selected-native-facet-exact-outside-projection-sampler-cause-v1',[ROOT/r['path'] for r in refs],dict(uids=['landsd/91827:0','landsd/104302:0'],failedRaySamplerProbes=7,allSelectedNativeFacetsExactlyOutsideFiniteProjection=True,fullAcceptance=False,runtimeChanged=False));print(dict(traced=len(rows)),flush=True)
if __name__=='__main__':main()
